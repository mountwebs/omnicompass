# Quickstart: Omni-Compass Core Architecture

## Prerequisites

- **Conda**: Installed and initialized.
- **Node.js**: v18+ installed.

## Backend Setup (Python)

1.  **Activate Environment**:
    ```bash
    conda activate astro
    ```

2.  **Install Dependencies**:
    ```bash
    cd backend
    pip install -r requirements.txt
    # Requirements will include: fastapi, uvicorn[standard], skyfield, numpy
    ```

3.  **Run Server**:
    ```bash
    cd backend
    python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```

## Frontend Setup (Vite + Three.js)

1.  **Install Dependencies**:
    ```bash
    cd frontend
    npm install
    ```

2.  **Run Development Server**:
    ```bash
    npm run dev
    ```
    Access at `http://localhost:5173` (or port shown in terminal).

## Verification

1.  Open the frontend URL on a mobile device (connected to same network) or use browser developer tools to simulate sensors.
2.  Allow Location permissions.
3.  Verify the arrow appears.
4.  Check backend logs to see WebSocket connection and position updates.
