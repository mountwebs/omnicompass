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

            direction = self._build_direction(observer, self._tracked_flight)
            self._last_direction = direction
            return direction

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

    def _fetch_flights(self, observer: ObserverLocation) -> list[Any]:
        bounds = self._api.get_bounds_by_point(
            observer.latitude,
            observer.longitude,
            self._radius_km * 1000,
        )
        return self._api.get_flights(bounds=bounds)

    def _select_tracked_flight(self, observer: ObserverLocation, flights: list[Any]) -> Optional[Any]:
        # Build index for quick lookups when we are already tracking a flight.
        flight_by_id = {flight.id: flight for flight in flights if getattr(flight, "id", None)}

        if self._tracked_flight and self._tracked_flight.id in flight_by_id:
            candidate = flight_by_id[self._tracked_flight.id]
            if self._within_radius(observer, candidate):
                return candidate

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
        self._last_fetch_ts = None
        self._last_direction = None
