# OmniCompass

OmniCompass is a real-time 3D compass application that points to celestial bodies (Sun, Moon, Mars, ISS) and other targets. It utilizes your device's geolocation and orientation to calculate the precise direction vector to the selected target relative to your current position.

The project consists of:
- **Backend**: A Python FastAPI service using `skyfield` for high-precision astronomical calculations.
- **Frontend**: A React application using `Three.js` to render a 3D arrow that aligns with the calculated vector in real-time.

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm (Node Package Manager)

## Setup & Installation

### 1. Backend Setup

The backend handles the astronomical calculations and serves data via WebSockets.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   .\venv\Scripts\activate
   ```

3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   # Make sure you are in the 'backend' directory (not 'backend/src')
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The backend will be available at `http://localhost:8000`.

### 2. Frontend Setup

The frontend visualizes the compass and handles device sensors.

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will typically start at `http://localhost:5173` (check the terminal output for the exact port).

## Usage

1. Ensure both the backend and frontend servers are running.
2. Open the frontend URL (e.g., `http://localhost:5173`) on a device with a magnetometer and GPS (like a smartphone), or use browser developer tools to simulate sensors.
   - **Note**: For device orientation to work on mobile devices, you may need to access the site via HTTPS or `localhost` (via port forwarding).
3. Grant permissions for **Location** and **Device Orientation** when prompted.
4. Use the dropdown menu to select a target (e.g., Sun, Moon, Mars, ISS).
5. The 3D arrow will rotate to point directly at the selected target in the sky (or through the earth).

## Architecture

- **Backend**:
  - `main.py`: FastAPI entry point and WebSocket handler.
  - `domain/calculator.py`: Logic for calculating Topocentric coordinates using `skyfield`.
- **Frontend**:
  - `components/Compass.tsx`: Main component managing the scene and UI.
  - `scene/`: Three.js logic for the 3D arrow and scene management.
  - `services/`: Handles WebSocket communication, Geolocation, and Device Orientation.
