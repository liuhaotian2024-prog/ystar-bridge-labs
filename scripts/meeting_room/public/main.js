import * as THREE from 'three';

// --- Renderer ---
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
document.body.appendChild(renderer.domElement);

// --- Scene ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2c2420);  // warm dark, exposed-brick vibe

// --- Camera ---
const camera = new THREE.PerspectiveCamera(
  50,
  window.innerWidth / window.innerHeight,
  0.1,
  100
);
camera.position.set(4, 3, 5);
camera.lookAt(0, 0.8, 0);

// --- Lighting ---
const ambient = new THREE.AmbientLight(0xffeedd, 0.4);
scene.add(ambient);

const dirLight = new THREE.DirectionalLight(0xfff4e0, 1.2);
dirLight.position.set(3, 5, 4);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 1024;
dirLight.shadow.mapSize.height = 1024;
scene.add(dirLight);

// Warm accent fill from the side
const fillLight = new THREE.PointLight(0xff9944, 0.5, 10);
fillLight.position.set(-3, 2, 1);
scene.add(fillLight);

// --- Floor ---
const floorGeo = new THREE.PlaneGeometry(10, 10);
const floorMat = new THREE.MeshStandardMaterial({
  color: 0x8b7355,   // warm wood tone
  roughness: 0.85,
  metalness: 0.0
});
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// --- Back Wall (exposed-brick placeholder — solid warm terracotta) ---
const wallGeo = new THREE.PlaneGeometry(10, 4);
const wallMat = new THREE.MeshStandardMaterial({
  color: 0x9e5a3c,   // terracotta brick placeholder
  roughness: 0.95,
  metalness: 0.0
});
const wall = new THREE.Mesh(wallGeo, wallMat);
wall.position.set(0, 2, -5);
wall.receiveShadow = true;
scene.add(wall);

// --- Avatar Placeholder Cube ---
const cubeGeo = new THREE.BoxGeometry(0.7, 1.6, 0.4);
const cubeMat = new THREE.MeshStandardMaterial({
  color: 0x4488cc,
  roughness: 0.3,
  metalness: 0.2
});
const cube = new THREE.Mesh(cubeGeo, cubeMat);
cube.position.set(0, 0.8, 0);
cube.castShadow = true;
scene.add(cube);

// --- Animation Loop (60 FPS target) ---
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);

  const elapsed = clock.getElapsedTime();
  cube.rotation.y = elapsed * 0.5;  // slow rotation

  renderer.render(scene, camera);
}

animate();

// --- Resize handler ---
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

console.log('[Y* Meeting Room] Scaffold scene loaded — Three.js r164');
