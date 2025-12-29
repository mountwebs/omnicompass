from __future__ import annotations

import asyncio
import math
import time
from typing import Any, Optional, Tuple

from FlightRadar24 import FlightRadar24API
from skyfield.api import Topos

from .calculator import CelestialCalculator
from .models import DirectionUpdate, ObserverLocation

# Conversion helper for feet to meters when altitude information is provided.
FEET_TO_METERS = 0.3048


class _InterpolatedFlight:
    def __init__(self, original: Any, latitude: float, longitude: float):
        self._original = original
        self.latitude = latitude
        self.longitude = longitude

    def __getattr__(self, name: str) -> Any:
        return getattr(self._original, name)


class AircraftTracker:
    """Polls FlightRadar24 for nearby aircraft and computes pointing data."""

    def __init__(
        self,
        calculator: CelestialCalculator,
        *,
        radius_km: float = 15.0,
        refresh_interval: float = 60.0,
        tracking_interval: float = 10.0,
    ) -> None:
        self._calculator = calculator
        self._radius_km = radius_km
        self._refresh_interval = refresh_interval
        self._tracking_interval = tracking_interval
        self._api = FlightRadar24API()

        self._lock = asyncio.Lock()
        self._tracked_flight: Optional[Any] = None
        self._last_flight_update_ts: Optional[float] = None
        self._last_fetch_ts: Optional[float] = None
        self._last_direction: Optional[DirectionUpdate] = None
        self._last_location: Optional[Tuple[float, float]] = None

    async def get_direction(self, observer: ObserverLocation) -> Optional[DirectionUpdate]:
        """Return pointing info for the tracked aircraft if one is available."""
        async with self._lock:
            location_changed = self._location_shifted(observer)
            now = time.monotonic()

            if location_changed:
                self._tracked_flight = None
                self._last_fetch_ts = None

            if self._needs_refresh(now):
                await self._refresh_flights(observer)
                self._last_fetch_ts = now

            if not self._tracked_flight:
                # Preserve last_direction to avoid jittering between None and data
                return None

            interpolated_flight = self._interpolate_flight(self._tracked_flight)
            direction = self._build_direction(observer, interpolated_flight)
            self._last_direction = direction
            return direction

    def _interpolate_flight(self, flight: Any) -> Any:
        if not self._last_flight_update_ts:
            return flight

        # Use time.time() (UTC-ish) to calculate elapsed time since the data timestamp
        now = time.time()
        elapsed = now - self._last_flight_update_ts

        if elapsed <= 0:
            return flight

        speed_knots = float(getattr(flight, "ground_speed", 0) or 0)
        heading = float(getattr(flight, "heading", 0) or 0)

        if speed_knots <= 0:
            return flight

        # 1 knot = 1.852 km/h
        speed_kmh = speed_knots * 1.852
        distance_km = speed_kmh * (elapsed / 3600.0)

        lat = float(flight.latitude)
        lon = float(flight.longitude)

        new_lat, new_lon = self._calculate_new_position(lat, lon, distance_km, heading)

        return _InterpolatedFlight(flight, new_lat, new_lon)

    def _calculate_new_position(self, lat: float, lon: float, distance_km: float, bearing_deg: float) -> Tuple[float, float]:
        R = 6371.0  # Earth radius in km
        lat1 = math.radians(lat)
        lon1 = math.radians(lon)
        bearing = math.radians(bearing_deg)

        lat2 = math.asin(
            math.sin(lat1) * math.cos(distance_km / R)
            + math.cos(lat1) * math.sin(distance_km / R) * math.cos(bearing)
        )

        lon2 = lon1 + math.atan2(
            math.sin(bearing) * math.sin(distance_km / R) * math.cos(lat1),
            math.cos(distance_km / R) - math.sin(lat1) * math.sin(lat2),
        )

        return math.degrees(lat2), math.degrees(lon2)

    def _needs_refresh(self, now: float) -> bool:
        if self._last_fetch_ts is None:
            return True

        interval = self._tracking_interval if self._tracked_flight else self._refresh_interval
        return (now - self._last_fetch_ts) >= interval

    def _location_shifted(self, observer: ObserverLocation) -> bool:
        coords = (observer.latitude, observer.longitude)
        if self._last_location is None:
            self._last_location = coords
            return True

        distance = self._surface_distance_km(self._last_location, coords)
        # If the observer moved more than half the tracking radius, force a refresh.
        if distance >= self._radius_km / 2:
            self._last_location = coords
            return True

        # Always keep the latest reading so small drifts accumulate correctly.
        self._last_location = coords
        return False

    async def _refresh_flights(self, observer: ObserverLocation) -> None:
        try:
            flights = await asyncio.to_thread(self._fetch_flights, observer)
        except Exception as exc:  # pragma: no cover - defensive logging for API errors
            print(f"FlightRadarAPI fetch failed: {exc}")
            return

        if not flights:
            self._tracked_flight = None
            return

        updated = self._select_tracked_flight(observer, flights)
        self._tracked_flight = updated
        if updated:
            # Prefer the flight's timestamp if available, otherwise use current time
            self._last_flight_update_ts = getattr(updated, "time", None) or time.time()

    def _fetch_flights(self, observer: ObserverLocation) -> list[Any]:
        bounds = self._api.get_bounds_by_point(
            observer.latitude,
            observer.longitude,
            self._radius_km * 1000,
        )
        return self._api.get_flights(bounds=bounds)

    def _select_tracked_flight(self, observer: ObserverLocation, flights: list[Any]) -> Optional[Any]:
        nearest: Optional[Tuple[float, Any]] = None
        for flight in flights:
            if flight.latitude is None or flight.longitude is None:
                continue
            distance = self._distance_to_observer(observer, flight)
            if distance is None or distance > self._radius_km:
                continue
            if nearest is None or distance < nearest[0]:
                nearest = (distance, flight)

        return nearest[1] if nearest else None

    def _within_radius(self, observer: ObserverLocation, flight: Any) -> bool:
        distance = self._distance_to_observer(observer, flight)
        return bool(distance is not None and distance <= self._radius_km)

    def _distance_to_observer(self, observer: ObserverLocation, flight: Any) -> Optional[float]:
        lat = getattr(flight, "latitude", None)
        lon = getattr(flight, "longitude", None)
        if lat is None or lon is None:
            return None
        return self._surface_distance_km(
            (observer.latitude, observer.longitude),
            (lat, lon),
        )

    def _surface_distance_km(self, origin: Tuple[float, float], target: Tuple[float, float]) -> float:
        lat1, lon1 = map(math.radians, origin)
        lat2, lon2 = map(math.radians, target)
        cosine = (
            math.sin(lat1) * math.sin(lat2)
            + math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
        )
        cosine = max(min(cosine, 1.0), -1.0)
        return math.acos(cosine) * 6371

    def _build_direction(self, observer: ObserverLocation, flight: Any) -> DirectionUpdate:
        t = self._calculator.ts.now()
        observer_topos = self._calculator.earth + Topos(
            latitude_degrees=observer.latitude,
            longitude_degrees=observer.longitude,
            elevation_m=observer.elevation,
        )

        altitude_m = float(getattr(flight, "altitude", 0.0) or 0.0) * FEET_TO_METERS
        target_topos = self._calculator.earth + Topos(
            latitude_degrees=float(flight.latitude),
            longitude_degrees=float(flight.longitude),
            elevation_m=altitude_m,
        )

        apparent = observer_topos.at(t).observe(target_topos).apparent()
        alt, az, distance = apparent.altaz()

        return DirectionUpdate(
            target_id=self._format_target_id(flight),
            azimuth=az.degrees,
            altitude=alt.degrees,
            distance_km=distance.km,
            timestamp=t.utc_datetime(),
        )

    def _format_target_id(self, flight: Any) -> str:
        return (
            getattr(flight, "callsign", None)
            or getattr(flight, "registration", None)
            or getattr(flight, "number", None)
            or getattr(flight, "id", "AIRCRAFT_OVERHEAD")
        )

    def reset(self) -> None:
        self._tracked_flight = None
        self._last_flight_update_ts = None
        self._last_fetch_ts = None
        self._last_direction = None
