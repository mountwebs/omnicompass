from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt, degrees
from typing import Tuple

# WGS84 ellipsoid constants
a = 6378137.0  # semi-major axis (m)
f = 1 / 298.257223563  # flattening
e2 = f * (2 - f)  # eccentricity squared


@dataclass(frozen=True)
class GeoPoint:
    """Geodetic point with altitude in meters."""

    latitude_deg: float
    longitude_deg: float
    altitude_m: float = 0.0


def geodetic_to_ecef(point: GeoPoint) -> Tuple[float, float, float]:
    """Convert geodetic coordinates to ECEF (Earth-Centered, Earth-Fixed)."""
    lat = radians(point.latitude_deg)
    lon = radians(point.longitude_deg)

    sin_lat = sin(lat)
    cos_lat = cos(lat)
    sin_lon = sin(lon)
    cos_lon = cos(lon)

    # Prime vertical radius of curvature
    N = a / sqrt(1.0 - e2 * sin_lat * sin_lat)

    x = (N + point.altitude_m) * cos_lat * cos_lon
    y = (N + point.altitude_m) * cos_lat * sin_lon
    z = (N * (1.0 - e2) + point.altitude_m) * sin_lat
    return x, y, z


def ecef_to_enu(dx: float, dy: float, dz: float, origin: GeoPoint) -> Tuple[float, float, float]:
    """Rotate ECEF delta vector into local ENU frame at origin."""
    lat = radians(origin.latitude_deg)
    lon = radians(origin.longitude_deg)

    sin_lat = sin(lat)
    cos_lat = cos(lat)
    sin_lon = sin(lon)
    cos_lon = cos(lon)

    east = -sin_lon * dx + cos_lon * dy
    north = -sin_lat * cos_lon * dx - sin_lat * sin_lon * dy + cos_lat * dz
    up = cos_lat * cos_lon * dx + cos_lat * sin_lon * dy + sin_lat * dz
    return east, north, up


def azimuth_elevation_distance(observer: GeoPoint, target: GeoPoint) -> Tuple[float, float, float]:
    """Return azimuth (deg), elevation (deg), and slant distance (m)."""
    obs_ecef = geodetic_to_ecef(observer)
    tgt_ecef = geodetic_to_ecef(target)

    dx = tgt_ecef[0] - obs_ecef[0]
    dy = tgt_ecef[1] - obs_ecef[1]
    dz = tgt_ecef[2] - obs_ecef[2]

    east, north, up = ecef_to_enu(dx, dy, dz, observer)

    distance = sqrt(dx * dx + dy * dy + dz * dz)
    horizontal = sqrt(east * east + north * north)

    azimuth = (degrees(atan2(east, north)) + 360.0) % 360.0
    elevation = degrees(atan2(up, horizontal))
    return azimuth, elevation, distance


def _feet_to_meters(value_ft: float) -> float:
    return value_ft * 0.3048


def main() -> None:
    # Replace with your observer position (latitude, longitude in degrees, altitude in meters).
    observer = GeoPoint(latitude_deg=59.9111, longitude_deg=10.7528, altitude_m=50.0)

    # Aircraft position in degrees. Convert altitude from feet to meters to match observer units.
    aircraft = GeoPoint(latitude_deg=60.0836, longitude_deg=11.0547, altitude_m=_feet_to_meters(2200.0))

    azimuth, elevation, distance = azimuth_elevation_distance(observer, aircraft)

    print(f"Azimuth: {azimuth:.2f} deg")
    print(f"Elevation: {elevation:.2f} deg")
    print(f"Distance: {distance:.1f} m")


if __name__ == "__main__":
    main()
