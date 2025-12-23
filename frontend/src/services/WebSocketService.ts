export type DirectionUpdate = {
    target_id: string;
    azimuth: number;
    altitude: number;
    distance_km: number;
    timestamp: string;
};

export class WebSocketService {
    private socket: WebSocket | null = null;
    private url: string;
    private onUpdate: (data: DirectionUpdate) => void;

    constructor(url: string, onUpdate: (data: DirectionUpdate) => void) {
        this.url = url;
        this.onUpdate = onUpdate;
    }

    public connect() {
        this.socket = new WebSocket(this.url);

        this.socket.onopen = () => {
            console.log("Connected to WebSocket");
        };

        this.socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'POSITION_UPDATE') {
                this.onUpdate(message.payload);
            }
        };

        this.socket.onclose = () => {
            console.log("Disconnected from WebSocket. Reconnecting in 3s...");
            setTimeout(() => this.connect(), 3000);
        };

        this.socket.onerror = (err) => {
            console.error("WebSocket error:", err);
            this.socket?.close();
        };
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
