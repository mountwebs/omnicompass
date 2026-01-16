import * as THREE from 'three';

export class SceneManager {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private container: HTMLElement;
    private arrow: THREE.Group | null = null;

    constructor(container: HTMLElement) {
        this.container = container;
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        
        this.init();
    }

    private init() {
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.container.appendChild(this.renderer.domElement);

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(0, 10, 10);
        this.scene.add(directionalLight);

        // Camera position
        this.camera.position.z = 5; // Move camera back to see the arrow

        // Handle resize
        window.addEventListener('resize', this.onWindowResize.bind(this));
        
        this.animate();
    }

    public setCameraOrientation(alpha: number | null, beta: number | null, gamma: number | null) {
        if (alpha === null) return;

        // Convert degrees to radians
        const alphaRad = THREE.MathUtils.degToRad(alpha);
        
        // Orbit the camera around the center (0,0,0) based on the bearing (alpha)
        // Radius
        const r = 5;
        
        // Calculate camera position
        // Alpha = 0 (North) -> Camera at (0, 0, 5) looking at (0, 0, 0) (Looking North/-Z)
        // Alpha = 90 (East) -> Camera at (-5, 0, 0) looking at (0, 0, 0) (Looking East/+X)
        const x = -r * Math.sin(alphaRad);
        const z = r * Math.cos(alphaRad);
        
        // For now, we keep the camera level (y=0) to simplify the compass view
        // We could incorporate beta (tilt) to look up/down, but for a compass 
        // it's often better to keep the horizon stable.
        
        this.camera.position.set(x, 0, z);
        this.camera.lookAt(0, 0, 0);
        
        // Optional: Apply screen orientation or gamma (roll) if needed
        // But for the basic "stay in place" requirement, this orbit is key.
    }

    public addArrow(arrow: THREE.Group) {
        console.log('Adding arrow to scene', arrow);
        this.arrow = arrow;
        this.scene.add(this.arrow);
    }

    public updateArrowPosition(azimuth: number, altitude: number) {
        if (!this.arrow) return;
        
        // Convert degrees to radians
        const azRad = THREE.MathUtils.degToRad(azimuth);
        const altRad = THREE.MathUtils.degToRad(altitude);
        
        // Spherical coordinates to Cartesian (Three.js Y-up)
        // Azimuth 0 -> North -> -Z
        // Azimuth 90 -> East -> +X
        const x = Math.sin(azRad) * Math.cos(altRad);
        const z = -Math.cos(azRad) * Math.cos(altRad);
        const y = Math.sin(altRad);
        
        const target = new THREE.Vector3(x, y, z).normalize().multiplyScalar(5);
        this.arrow.lookAt(target);
    }

    private onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    private animate() {
        requestAnimationFrame(this.animate.bind(this));
        this.renderer.render(this.scene, this.camera);
    }
    
    public getScene(): THREE.Scene {
        return this.scene;
    }

    public dispose() {
        if (this.container.contains(this.renderer.domElement)) {
            this.container.removeChild(this.renderer.domElement);
        }
        this.renderer.dispose();
    }
}
