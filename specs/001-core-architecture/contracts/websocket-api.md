# WebSocket API Contract

**Endpoint**: `/ws`

## Message Format
All messages are JSON objects.
Every message from Client to Server must have a `type` field.
Every message from Server to Client will have a `type` field.

## Client -> Server Messages

### 1. Update Location
Sent when the user's geolocation changes.

```json
{
  "type": "UPDATE_LOCATION",
  "payload": {
    "latitude": 59.91,
    "longitude": 10.75,
    "elevation": 50.0
  }
}
```

### 2. Switch Target
Sent when the user selects a new celestial body to track.

```json
{
  "type": "SWITCH_TARGET",
  "payload": {
    "target": "MARS"
  }
}
```

## Server -> Client Messages

### 1. Position Update
Sent periodically (e.g., every 100ms-1s) or upon location/target change.

```json
{
  "type": "POSITION_UPDATE",
  "payload": {
    "target": "MARS",
    "azimuth": 145.32,   // Degrees
    "altitude": 45.12,   // Degrees
    "distance_km": 225000000,
    "timestamp": "2025-12-23T12:00:00Z"
  }
}
```

### 2. Error
Sent when an invalid request is received or an internal error occurs.

```json
{
  "type": "ERROR",
  "payload": {
    "code": "INVALID_TARGET",
    "message": "Target 'PLUTO' is not supported."
  }
}
```
