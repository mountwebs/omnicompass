import * as THREE from 'three';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader';
import arrowUrl from '../assets/arrow.fbx?url';

export class AssetLoader {
    private loader: FBXLoader;

    constructor() {
        this.loader = new FBXLoader();
    }

    public loadArrow(): Promise<THREE.Group> {
        return new Promise((resolve, reject) => {
            this.loader.load(
                arrowUrl,
                (object) => {
                    // Create a container group to handle orientation correction
                    const container = new THREE.Group();
                    
                    // Normalize scale
                    object.scale.set(0.01, 0.01, 0.01); 
                    
                    // Fix orientation: 
                    // The model seems to be pointing along the X axis.
                    // We rotate it -90 degrees around Y to align it with +Z (which lookAt uses).
                    object.rotation.y = -Math.PI / 2;

                    container.add(object);
                    resolve(container);
                },
                (xhr) => {
                    console.log((xhr.loaded / xhr.total * 100) + '% loaded');
                },
                (error) => {
                    console.error('Error loading arrow:', error);
                    reject(error);
                }
            );
        });
    }
}
