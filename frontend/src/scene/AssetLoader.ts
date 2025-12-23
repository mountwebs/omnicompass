import * as THREE from 'three';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader';

export class AssetLoader {
    private loader: FBXLoader;

    constructor() {
        this.loader = new FBXLoader();
    }

    public loadArrow(): Promise<THREE.Group> {
        return new Promise((resolve, reject) => {
            this.loader.load(
                '/assets/arrow.fbx',
                (object) => {
                    // Normalize scale and position if needed
                    // We might need to adjust this based on the actual model size
                    object.scale.set(0.01, 0.01, 0.01); 
                    resolve(object);
                },
                (xhr) => {
                    console.log((xhr.loaded / xhr.total * 100) + '% loaded');
                },
                (error) => {
                    reject(error);
                }
            );
        });
    }
}
