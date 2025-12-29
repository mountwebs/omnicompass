from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class CelestialBody(str, Enum):
    SUN = "SUN"
    MARS = "MARS"
    VENUS = "VENUS"
    SATURN = "SATURN"
    JUPITER = "JUPITER"
    MOON = "MOON"

class ObserverLocation(BaseModel):
    latitude: float
    longitude: float
    elevation: float = 0.0

class DirectionUpdate(BaseModel):
    target_id: str
    azimuth: float
    altitude: float
    distance_km: float
    timestamp: datetime
    # Aircraft specific data
    aircraft_altitude_m: float | None = None
    ground_speed_kmh: float | None = None
    origin_airport: str | None = None
    destination_airport: str | None = None
    vertical_speed_mps: float | None = None
