# Implementation Plan: Omni-Compass Core Architecture

**Branch**: `001-core-architecture` | **Date**: 23 December 2025 | **Spec**: [specs/001-core-architecture/spec.md](specs/001-core-architecture/spec.md)
**Input**: Feature specification from `specs/001-core-architecture/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a real-time celestial tracking application with a Python backend using Skyfield for astronomical calculations and a Vite + Three.js frontend for 3D visualization. The system will use WebSockets for real-time communication of directional vectors based on the user's geolocation and device orientation.

## Technical Context

**Language/Version**: Python 3.10+ (Backend, Conda "astro" env), Node.js 18+ (Frontend)
**Primary Dependencies**: 
- Backend: `skyfield`, `websockets` (or `fastapi`), `numpy`
- Frontend: `three`, `vite`
**Storage**: N/A (Real-time calculation)
**Testing**: 
- Backend: `pytest`
- Frontend: `vitest`
**Target Platform**: Web Browsers (Mobile & Desktop)
**Project Type**: Web Application (Frontend + Backend)
**Performance Goals**: < 500ms latency for updates, 60fps rendering
**Constraints**: Device orientation permissions on iOS/Android
**Scale/Scope**: Single user session focus initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle 1 (Library-First)**: Backend logic (Skyfield wrapper) should be modular.
- **Principle 2 (CLI Interface)**: N/A for this web-focused feature, but backend could have CLI entry point.
- **Principle 3 (Test-First)**: Will write tests for calculation logic.

*Note: Constitution file appears to be a template. Proceeding with standard best practices.*

## Project Structure

### Documentation (this feature)

```text
specs/001-core-architecture/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── domain/          # Skyfield logic, celestial calculations
│   ├── api/             # WebSocket handlers
│   └── main.py          # Entry point
└── tests/

frontend/
├── src/
│   ├── components/      # UI overlays
│   ├── scene/           # Three.js scene management
│   ├── services/        # WebSocket client, Location service
│   └── main.ts
└── tests/
```

**Structure Decision**: Split into `backend` and `frontend` directories at the root to separate concerns and environments (Python vs Node).

## Complexity Tracking

N/A
