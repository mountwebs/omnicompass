export class LocationService {
    public getCurrentPosition(): Promise<GeolocationPosition> {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error("Geolocation not supported"));
                return;
            }
            navigator.geolocation.getCurrentPosition(resolve, reject);
        });
    }

    public watchPosition(callback: (position: GeolocationPosition) => void): number {
        if (!navigator.geolocation) {
            throw new Error("Geolocation not supported");
        }
        return navigator.geolocation.watchPosition(callback, (err) => console.error(err));
    }
    
    public clearWatch(id: number) {
        navigator.geolocation.clearWatch(id);
    }
}
