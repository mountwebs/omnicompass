from fastapi import WebSocket, WebSocketDisconnect
from ..domain.calculator import CelestialCalculator
from ..domain.models import ObserverLocation, CelestialBody, DirectionUpdate
from ..domain.aircraft_tracker import AircraftTracker
import json
import asyncio
from typing import Optional

AIRCRAFT_TARGET = "AIRCRAFT_OVERHEAD"


class WebSocketHandler:
    def __init__(self, calculator: CelestialCalculator):
        self.calculator = calculator
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def handle_connection(self, websocket: WebSocket):
        await self.connect(websocket)
        
        # State for this connection using a mutable container (dict) to share with closure
        state = {
            "location": None,
            "target": CelestialBody.SUN,
            "aircraft_tracker": AircraftTracker(self.calculator),
            "aircraft_status": "IDLE"
        }
        
        # Start a background task for pushing updates
        push_task = asyncio.create_task(self.push_updates(websocket, state))
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message['type'] == 'UPDATE_LOCATION':
                    payload = message['payload']
                    state["location"] = ObserverLocation(
                        latitude=payload['latitude'],
                        longitude=payload['longitude'],
                        elevation=payload.get('elevation', 0.0)
                    )
                    
                elif message['type'] == 'SWITCH_TARGET':
                    payload = message['payload']
                    target_str = payload['target']
                    if target_str == AIRCRAFT_TARGET:
                        state["target"] = AIRCRAFT_TARGET
                        state["aircraft_tracker"].reset()
                        state["aircraft_status"] = "IDLE"
                    elif target_str in CelestialBody.__members__:
                        state["target"] = CelestialBody(target_str)
                        state["aircraft_tracker"].reset()
                        state["aircraft_status"] = "IDLE"
                    
        except WebSocketDisconnect:
            self.disconnect(websocket)
            push_task.cancel()
        except Exception as e:
            print(f"Error: {e}")
            # Only disconnect if not already disconnected
            if websocket in self.active_connections:
                self.disconnect(websocket)
            push_task.cancel()

    async def push_updates(self, websocket: WebSocket, state: dict):
        try:
            while True:
                location = state["location"]
                target = state["target"]

                update: Optional[DirectionUpdate] = None
                if location and target:
                    if isinstance(target, CelestialBody):
                        update = self.calculator.calculate_position(location, target)
                    elif target == AIRCRAFT_TARGET:
                        tracker: AircraftTracker = state["aircraft_tracker"]
                        aircraft_update = await tracker.get_direction(location)
                        if aircraft_update:
                            update = aircraft_update
                            if state["aircraft_status"] != "TRACKING":
                                state["aircraft_status"] = "TRACKING"
                        elif state["aircraft_status"] != "SEARCHING":
                            state["aircraft_status"] = "SEARCHING"
                            response = {
                                "type": "AIRCRAFT_STATUS",
                                "payload": {"state": "SEARCHING"}
                            }
                            await websocket.send_text(json.dumps(response))

                if update:
                    response = {
                        "type": "POSITION_UPDATE",
                        "payload": update.model_dump(mode='json')
                    }
                    await websocket.send_text(json.dumps(response))
                
                await asyncio.sleep(0.5) # 500ms update rate
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Push error: {e}")
