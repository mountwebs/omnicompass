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
        this.camera.position.z = 0.1; // Close to center

        // Handle resize
        window.addEventListener('resize', this.onWindowResize.bind(this));
        
        this.animate();
    }

    public setCameraOrientation(alpha: number | null, beta: number | null, gamma: number | null) {
        if (alpha === null || beta === null || gamma === null) return;

        // Convert degrees to radians
        const alphaRad = alpha * (Math.PI / 180);
        const betaRad = beta * (Math.PI / 180);
        const gammaRad = gamma * (Math.PI / 180);

        const euler = new THREE.Euler();
        // Order depends on device, usually ZXY or YXZ for device orientation
        // This is a simplified implementation. 
        // For robust implementation we would need to handle screen orientation as well.
        
        // Three.js convention:
        // alpha: rotation around Z axis
        // beta: rotation around X axis
        // gamma: rotation around Y axis
        
        // Note: This is an approximation. 
        // DeviceOrientationControls from Three.js handles this much better with Quaternions.
        // Since it's missing, we might want to look for a copy or implementation.
        
        // For now, let's try to set rotation directly
        // But actually, without DeviceOrientationControls, it's hard to get right.
        // Let's try to find if we can install it separately or if I missed it.
        
        // If I can't use the control, I will just leave the camera static for now 
        // and rotate the ARROW relative to the camera? 
        // No, the arrow points to absolute North/Sun. The camera represents the phone.
        // So if I rotate the phone, the camera rotates, and the arrow should stay fixed in WORLD space,
        // which means it moves in CAMERA space.
        
        // Let's use a simple Euler rotation for MVP
        this.camera.rotation.set(betaRad, alphaRad, -gammaRad, 'YXZ'); 
    }

    public addArrow(arrow: THREE.Group) {
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
}
