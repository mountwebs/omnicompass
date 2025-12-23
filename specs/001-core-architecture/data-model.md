# Data Model: Omni-Compass Core Architecture

**Feature**: `001-core-architecture`

## Entities

### CelestialTarget
Represents the celestial body being tracked.

| Field | Type | Description |
|-------|------|-------------|
| `id` | String (Enum) | Unique identifier (e.g., "SUN", "MARS"). |
| `name` | String | Display name. |
| `skyfield_id` | String | Identifier used in Skyfield/Ephemeris (e.g., 'sun', 'mars'). |

### ObserverLocation
Represents the user's geographic location.

| Field | Type | Description |
|-------|------|-------------|
| `latitude` | Float | Latitude in degrees (-90 to 90). |
| `longitude` | Float | Longitude in degrees (-180 to 180). |
| `elevation` | Float | Elevation in meters (default 0). |

### DirectionUpdate
The calculated position sent to the client.

| Field | Type | Description |
|-------|------|-------------|
| `target_id` | String | ID of the target being tracked. |
| `azimuth` | Float | Azimuth in degrees (0-360, North=0, East=90). |
| `altitude` | Float | Altitude in degrees (-90 to 90, Horizon=0). |
| `distance_km` | Float | Distance to the object in kilometers. |
| `timestamp` | ISO8601 | Time of calculation. |

## State Management

### Backend State (Per Connection)
- `current_location`: ObserverLocation
- `current_target`: CelestialTarget (Default: SUN)

### Frontend State
- `device_orientation`: { alpha, beta, gamma } (Device rotation)
- `target_direction`: DirectionUpdate (Latest from server)
