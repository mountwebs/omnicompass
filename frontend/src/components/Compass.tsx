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
    const orientationServiceRef = useRef<DeviceOrientationService | null>(null);
    
    const [status, setStatus] = useState<string>("Initializing...");
    const [permissionGranted, setPermissionGranted] = useState<boolean>(false);
    const [currentTarget, setCurrentTarget] = useState<string>("SUN");
    const [manualBearing, setManualBearing] = useState<number>(0);
    const [isManualMode, setIsManualMode] = useState<boolean>(false);
    
    const [isManualDirectionMode, setIsManualDirectionMode] = useState<boolean>(false);
    const [manualAzimuth, setManualAzimuth] = useState<number>(0);
    const [manualAltitude, setManualAltitude] = useState<number>(0);

    const [isManualLocationMode, setIsManualLocationMode] = useState<boolean>(false);
    const [manualLatitude, setManualLatitude] = useState<number>(0);
    const [manualLongitude, setManualLongitude] = useState<number>(0);
    const [manualElevation, setManualElevation] = useState<number>(0);

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
            if (!isManualDirectionModeRef.current) {
                sceneManager.updateArrowPosition(data.azimuth, data.altitude);
                setStatus(`Tracking: ${data.target_id} (Az: ${data.azimuth.toFixed(1)}, Alt: ${data.altitude.toFixed(1)})`);
            }
        });
        wsService.connect();
        wsServiceRef.current = wsService;

        const locationService = new LocationService();
        // Watch position
        const watchId = locationService.watchPosition((pos) => {
            if (!isManualLocationModeRef.current) {
                wsService.sendLocation(pos.coords.latitude, pos.coords.longitude, pos.coords.altitude || 0);
            }
        });

        // Init Orientation Service (but don't start yet)
        // We use a ref for the callback to avoid stale closures if we were to define it here
        // But since we need to access isManualMode, we'll use a mutable ref for that state
        orientationServiceRef.current = new DeviceOrientationService((orientation) => {
            if (!isManualModeRef.current) {
                sceneManagerRef.current?.setCameraOrientation(orientation.alpha, orientation.beta, orientation.gamma);
            }
        });

        // Cleanup
        return () => {
            locationService.clearWatch(watchId);
            wsService.disconnect();
            sceneManager.dispose();
            orientationServiceRef.current?.stop();
        };
    }, []); 

    // Keep the ref in sync with state
    const isManualModeRef = useRef(isManualMode);
    useEffect(() => {
        isManualModeRef.current = isManualMode;
    }, [isManualMode]);

    const isManualDirectionModeRef = useRef(isManualDirectionMode);
    useEffect(() => {
        isManualDirectionModeRef.current = isManualDirectionMode;
    }, [isManualDirectionMode]);

    const isManualLocationModeRef = useRef(isManualLocationMode);
    useEffect(() => {
        isManualLocationModeRef.current = isManualLocationMode;
    }, [isManualLocationMode]);

    useEffect(() => {
        if (isManualMode) {
            sceneManagerRef.current?.setCameraOrientation(manualBearing, 0, 0);
        }
    }, [isManualMode, manualBearing]);

    useEffect(() => {
        if (isManualDirectionMode) {
            sceneManagerRef.current?.updateArrowPosition(manualAzimuth, manualAltitude);
            setStatus(`Manual Direction (Az: ${manualAzimuth.toFixed(1)}, Alt: ${manualAltitude.toFixed(1)})`);
        }
    }, [isManualDirectionMode, manualAzimuth, manualAltitude]);

    useEffect(() => {
        if (isManualLocationMode) {
            wsServiceRef.current?.sendLocation(manualLatitude, manualLongitude, manualElevation);
            setStatus(`Manual Location (Lat: ${manualLatitude}, Lon: ${manualLongitude}, Alt: ${manualElevation})`);
        }
    }, [isManualLocationMode, manualLatitude, manualLongitude, manualElevation]);

    const handleRequestPermission = async () => {
        if (!orientationServiceRef.current) return;
        
        const granted = await orientationServiceRef.current.requestPermission();
        if (granted) {
            setPermissionGranted(true);
            orientationServiceRef.current.start();
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
                
                <div style={{ marginTop: 10 }}>
                    <label style={{ display: 'block' }}>
                        <input 
                            type="checkbox" 
                            checked={isManualMode} 
                            onChange={(e) => setIsManualMode(e.target.checked)} 
                        />
                        Manual Bearing
                    </label>
                    {isManualMode && (
                        <div style={{ marginTop: 5 }}>
                            <input 
                                type="range" 
                                min="0" 
                                max="360" 
                                value={manualBearing} 
                                onChange={(e) => setManualBearing(Number(e.target.value))} 
                                style={{ width: '100%' }}
                            />
                            <span>{manualBearing}°</span>
                        </div>
                    )}
                </div>

                <div style={{ marginTop: 10 }}>
                    <label style={{ display: 'block' }}>
                        <input 
                            type="checkbox" 
                            checked={isManualDirectionMode} 
                            onChange={(e) => setIsManualDirectionMode(e.target.checked)} 
                        />
                        Manual Direction
                    </label>
                    {isManualDirectionMode && (
                        <div style={{ marginTop: 5 }}>
                            <div style={{ marginBottom: 5 }}>
                                <label>Azimuth: {manualAzimuth}°</label>
                                <input 
                                    type="range" 
                                    min="0" 
                                    max="360" 
                                    value={manualAzimuth} 
                                    onChange={(e) => setManualAzimuth(Number(e.target.value))} 
                                    style={{ width: '100%' }}
                                />
                            </div>
                            <div>
                                <label>Altitude: {manualAltitude}°</label>
                                <input 
                                    type="range" 
                                    min="-90" 
                                    max="90" 
                                    value={manualAltitude} 
                                    onChange={(e) => setManualAltitude(Number(e.target.value))} 
                                    style={{ width: '100%' }}
                                />
                            </div>
                        </div>
                    )}
                </div>

                <div style={{ marginTop: 10 }}>
                    <label style={{ display: 'block' }}>
                        <input 
                            type="checkbox" 
                            checked={isManualLocationMode} 
                            onChange={(e) => setIsManualLocationMode(e.target.checked)} 
                        />
                        Manual Location
                    </label>
                    {isManualLocationMode && (
                        <div style={{ marginTop: 5 }}>
                            <div style={{ marginBottom: 5 }}>
                                <label>Lat: </label>
                                <input 
                                    type="number" 
                                    value={manualLatitude} 
                                    onChange={(e) => setManualLatitude(Number(e.target.value))} 
                                    style={{ width: '60px' }}
                                />
                            </div>
                            <div style={{ marginBottom: 5 }}>
                                <label>Lon: </label>
                                <input 
                                    type="number" 
                                    value={manualLongitude} 
                                    onChange={(e) => setManualLongitude(Number(e.target.value))} 
                                    style={{ width: '60px' }}
                                />
                            </div>
                            <div>
                                <label>Elev: </label>
                                <input 
                                    type="number" 
                                    value={manualElevation} 
                                    onChange={(e) => setManualElevation(Number(e.target.value))} 
                                    style={{ width: '60px' }}
                                />
                            </div>
                        </div>
                    )}
                </div>
            </div>
            <TargetSelector currentTarget={currentTarget} onSelectTarget={handleSelectTarget} />
        </div>
    );
};
