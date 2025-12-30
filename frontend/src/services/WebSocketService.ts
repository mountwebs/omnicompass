export type DirectionUpdate = {
    target_id: string;
    azimuth: number;
    altitude: number;
    distance_km: number;
    timestamp: string;
    aircraft_altitude_m?: number;
    ground_speed_kmh?: number;
    origin_airport?: string;
    destination_airport?: string;
    vertical_speed_mps?: number;
    horizontal_distance_km?: number;
};

export type AircraftStatusPayload = {
    state: 'SEARCHING' | 'TRACKING' | 'IDLE';
};

export class WebSocketService {
    private socket: WebSocket | null = null;
    private url: string;
    private onUpdate: (data: DirectionUpdate) => void;
    private shouldReconnect: boolean = true;
    private onAircraftStatus?: (payload: AircraftStatusPayload) => void;

    constructor(
        url: string,
        onUpdate: (data: DirectionUpdate) => void,
        onAircraftStatus?: (payload: AircraftStatusPayload) => void
    ) {
        this.url = url;
        this.onUpdate = onUpdate;
        this.onAircraftStatus = onAircraftStatus;
    }

    public connect() {
        this.shouldReconnect = true;
        this.socket = new WebSocket(this.url);

        this.socket.onopen = () => {
            console.log("Connected to WebSocket");
        };

        this.socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'POSITION_UPDATE') {
                this.onUpdate(message.payload);
            } else if (message.type === 'AIRCRAFT_STATUS' && this.onAircraftStatus) {
                this.onAircraftStatus(message.payload);
            }
        };

        this.socket.onclose = () => {
            if (this.shouldReconnect) {
                console.log("Disconnected from WebSocket. Reconnecting in 3s...");
                setTimeout(() => this.connect(), 3000);
            }
        };

        this.socket.onerror = (err) => {
            console.error("WebSocket error:", err);
            this.socket?.close();
        };
    }

    public disconnect() {
        this.shouldReconnect = false;
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }


    public sendLocation(latitude: number, longitude: number, elevation: number = 0) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'UPDATE_LOCATION',
                payload: { latitude, longitude, elevation }
            }));
        }
    }

    public switchTarget(target: string) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'SWITCH_TARGET',
                payload: { target }
            }));
        }
    }
}
