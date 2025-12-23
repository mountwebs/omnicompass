from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .domain.calculator import CelestialCalculator
from .api.websocket_handler import WebSocketHandler

app = FastAPI()
# Initialize calculator on startup to load data once
calculator = CelestialCalculator()
ws_handler = WebSocketHandler(calculator)

@app.get("/")
async def root():
    return {"message": "Omni-Compass Backend Running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_handler.handle_connection(websocket)

