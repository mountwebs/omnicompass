# Feature Specification: Omni-Compass Core Architecture

**Feature Branch**: `001-core-architecture`
**Created**: 23 December 2025
**Status**: Draft
**Input**: User description: "Implement Omni-Compass core architecture with Python backend (Skyfield), Vite+Three.js frontend, and WebSocket communication."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real-time Sun Tracking (Priority: P1)

As a user, I want to see a 3D arrow pointing towards the Sun based on my current location so that I can know its position relative to me.

**Why this priority**: This is the core value proposition of the application. Without this, the app does not fulfill its primary purpose.

**Independent Test**: Can be fully tested by hardcoding a location and verifying the arrow points to the correct calculated position of the Sun for the current time.

**Acceptance Scenarios**:

1. **Given** the application is loaded, **When** I provide my location (latitude/longitude), **Then** the 3D arrow should orient itself to point towards the Sun.
2. **Given** the application is running, **When** time progresses, **Then** the arrow should update its orientation to track the Sun's movement.
3. **Given** the application is running, **When** I change my device orientation (if supported) or input a new orientation, **Then** the arrow should adjust to maintain the correct absolute direction.

---

### User Story 2 - Switch Celestial Targets (Priority: P2)

As a user, I want to switch the tracking target to other celestial bodies (e.g., Mars) so that I can locate them as well.

**Why this priority**: Extends the utility of the application beyond just the Sun, as described in the architecture plan.

**Independent Test**: Can be tested by selecting a different object from a UI control and verifying the arrow re-orients to the new target's coordinates.

**Acceptance Scenarios**:

1. **Given** I am tracking the Sun, **When** I select "Mars" from the target list, **Then** the arrow should smoothly re-orient to point towards Mars.
2. **Given** I have selected a new target, **When** the backend calculates the position, **Then** the frontend should receive the new coordinates via WebSocket.

### Edge Cases

- What happens when the user denies location permissions? (Should fallback to a default or prompt manual entry)
- What happens if the WebSocket connection is lost? (Should attempt reconnect or show offline status)
- What happens if the celestial body is below the horizon? (Arrow should still point to it, maybe through the ground)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Backend MUST calculate the Topocentric position (Azimuth and Altitude) of celestial bodies with astronomical precision.
- **FR-002**: The Backend MUST provide a WebSocket server to accept client connections.
- **FR-003**: The Frontend MUST render a 3D scene with a directional arrow.
- **FR-004**: The Frontend MUST render a 3D arrow model (loaded from provided assets).
- **FR-005**: The Frontend MUST send the user's geographic coordinates (Latitude, Longitude) to the Backend via WebSocket.
- **FR-006**: The Backend MUST push real-time directional updates (vector or angles) to the Frontend via WebSocket.
- **FR-007**: The System MUST support switching the tracking target between at least the Sun and Mars.
- **FR-008**: The Frontend MUST allow the user to input or detect device orientation to align the virtual scene with the real world.

### Key Entities *(include if feature involves data)*

- **CelestialTarget**: The object being tracked (e.g., Sun, Mars).
- **ObserverLocation**: The user's geographic position (Lat, Long, Elevation).
- **DirectionVector**: The calculated vector pointing from the Observer to the CelestialTarget.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The 3D arrow updates its position within 500ms of a location change or target switch.
- **SC-002**: The calculated position matches reference astronomical data for the given time and location.
- **SC-003**: The WebSocket connection remains active and stable for sessions longer than 30 minutes.
- **SC-004**: The application successfully loads and renders the 3D arrow on standard modern web browsers.

## Assumptions

- The user has a stable internet connection for WebSocket communication.
- The `assets/arrow.fbx` file is available and valid.
- The Python environment has access to install necessary packages (skyfield, websockets, etc.).
