# Research: Omni-Compass Core Architecture

**Feature**: `001-core-architecture`
**Date**: 23 December 2025

## Decisions

### 1. Backend Framework: FastAPI
- **Decision**: Use `FastAPI` for the backend.
- **Rationale**: 
    - Built-in WebSocket support (via Starlette).
    - Easy to add HTTP endpoints if needed (e.g., health checks, serving static files).
    - Modern, async-first (perfect for WebSockets).
    - Type hinting support aligns with Python best practices.
- **Alternatives Considered**: 
    - `websockets` (raw library): Simpler, but less extensible if we need HTTP later.
    - `Flask-SocketIO`: Heavier, synchronous by default (though supports async), older paradigm.

### 2. Frontend Testing: Vitest + Logic Focus
- **Decision**: Use `Vitest` for unit testing logic and services.
- **Rationale**: 
    - Fast, native Vite integration.
    - Focus tests on the *logic* (WebSocket service, coordinate transformation) rather than the 3D rendering itself for this MVP.
    - Visual regression testing is too complex for Phase 1.
- **Alternatives Considered**: 
    - `Jest`: Slower with Vite.
    - `Cypress`/`Playwright`: Good for E2E, but maybe overkill for initial setup.

### 3. Device Orientation API
- **Decision**: Use standard `DeviceOrientationEvent` with iOS permission handling.
- **Rationale**: 
    - Standard web API.
    - Must handle iOS 13+ permission request (`DeviceOrientationEvent.requestPermission()`) which requires a user interaction (button click).
- **Alternatives Considered**: 
    - `AbsoluteOrientationSensor` (Generic Sensor API): Newer, but less browser support (mainly Chrome/Android).

## Unknowns Resolved

- **Testing Setup**: Confirmed Vitest for logic.
- **WebSocket Lib**: Confirmed FastAPI.
- **Orientation**: Confirmed API and permission flow.

## Best Practices

- **Skyfield**: Load ephemeris data (`de421.bsp`) once at startup, not per request. Use `ts.now()` for real-time.
- **Three.js**: Dispose of geometries and materials when switching scenes (though we have a single scene here) to avoid memory leaks.
- **WebSockets**: Handle reconnection logic on the frontend (exponential backoff).
