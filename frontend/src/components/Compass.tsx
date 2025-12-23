import { useEffect, useRef, useState } from 'react';
import { SceneManager } from '../scene/SceneManager';
import { AssetLoader } from '../scene/AssetLoader';
import { LocationService } from '../services/LocationService';
import { WebSocketService, type DirectionUpdate } from '../services/WebSocketService';
import { DeviceOrientationService } from '../services/DeviceOrientationService';
import { TargetSelector } from './TargetSelector';

export const Compass = () => {
    const containerRef = useRef<HTMLDivElement>(null);
    const sceneManagerRef = useRef<SceneManager | null>(null);
    const wsServiceRef = useRef<WebSocketService | null>(null);
    
    const [status, setStatus] = useState<string>("Initializing...");
    const [permissionGranted, setPermissionGranted] = useState<boolean>(false);
    const [currentTarget, setCurrentTarget] = useState<string>("SUN");

    useEffect(() => {
        if (!containerRef.current) return;

        // Init Scene
        const sceneManager = new SceneManager(containerRef.current);
        sceneManagerRef.current = sceneManager;

        // Load Asset
        const loader = new AssetLoader();
        loader.loadArrow().then((arrow) => {
            sceneManager.addArrow(arrow);
            setStatus("Arrow loaded. Waiting for location...");
        }).catch(err => {
            console.error(err);
            setStatus("Error loading asset");
        });

        // Init Services
        // Note: Hardcoded URL for MVP, should be env var
        const wsService = new WebSocketService('ws://localhost:8000/ws', (data: DirectionUpdate) => {
            sceneManager.updateArrowPosition(data.azimuth, data.altitude);
            setStatus(`Tracking: ${data.target_id} (Az: ${data.azimuth.toFixed(1)}, Alt: ${data.altitude.toFixed(1)})`);
        });
        wsService.connect();
        wsServiceRef.current = wsService;

        const locationService = new LocationService();
        // Watch position
        const watchId = locationService.watchPosition((pos) => {
            wsService.sendLocation(pos.coords.latitude, pos.coords.longitude, pos.coords.altitude || 0);
        });

        // Cleanup
        return () => {
            locationService.clearWatch(watchId);
            wsService.disconnect();
            sceneManager.dispose();
        };
    }, []);

    const handleRequestPermission = async () => {
        const orientationService = new DeviceOrientationService((orientation) => {
            sceneManagerRef.current?.setCameraOrientation(orientation.alpha, orientation.beta, orientation.gamma);
        });
        const granted = await orientationService.requestPermission();
        if (granted) {
            setPermissionGranted(true);
            orientationService.start();
        } else {
            setStatus("Orientation permission denied");
        }
    };

    const handleSelectTarget = (target: string) => {
        setCurrentTarget(target);
        wsServiceRef.current?.switchTarget(target);
    };

    return (
        <div style={{ width: '100%', height: '100vh', position: 'relative' }}>
            <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
            <div style={{ position: 'absolute', top: 10, left: 10, color: 'white', background: 'rgba(0,0,0,0.5)', padding: 10 }}>
                <p>{status}</p>
                {!permissionGranted && (
                    <button onClick={handleRequestPermission}>Enable Orientation</button>
                )}
            </div>
            <TargetSelector currentTarget={currentTarget} onSelectTarget={handleSelectTarget} />
        </div>
    );
};
