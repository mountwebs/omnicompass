export type Orientation = {
    alpha: number | null; // Z-axis (compass) 0-360
    beta: number | null;  // X-axis (front-back) -180 to 180
    gamma: number | null; // Y-axis (left-right) -90 to 90
};

export class DeviceOrientationService {
    private onOrientationChange: (orientation: Orientation) => void;

    constructor(onOrientationChange: (orientation: Orientation) => void) {
        this.onOrientationChange = onOrientationChange;
    }

    public start() {
        window.addEventListener('deviceorientation', this.handleOrientation);
    }

    public stop() {
        window.removeEventListener('deviceorientation', this.handleOrientation);
    }

    public async requestPermission(): Promise<boolean> {
        // iOS 13+ requires permission
        if (typeof (DeviceOrientationEvent as any).requestPermission === 'function') {
            try {
                const response = await (DeviceOrientationEvent as any).requestPermission();
                return response === 'granted';
            } catch (e) {
                console.error(e);
                return false;
            }
        }
        return true;
    }

    private handleOrientation = (event: DeviceOrientationEvent) => {
        this.onOrientationChange({
            alpha: event.alpha,
            beta: event.beta,
            gamma: event.gamma
        });
    };
}
