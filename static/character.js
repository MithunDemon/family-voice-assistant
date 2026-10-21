import * as THREE from './vendor/three.module.js';

let scene, camera, renderer;
let characterGroup, headMesh, leftEyeGroup, rightEyeGroup, leftPupil, rightPupil;
let leftEyelid, rightEyelid, leftEyebrow, rightEyebrow;
let mouthMesh, mouthMouthGeometry;
let isWebGLAvailable = false;
let currentState = 'idle'; // idle | listening | thinking | speaking
let animTime = 0;
let isAnimating = true;

// Blinking state
let nextBlinkTime = 2.0;
let isBlinking = false;
let blinkProgress = 0;

// Speaking mouth animation state
let mouthOpenness = 0;
let targetMouthOpenness = 0;
let isSpeakingAnim = false;
let speechDurationEstimate = 0;
let speechStartTime = 0;
let speechIntervalId = null;

// Look angles for thinking / listening
let targetHeadRotY = 0;
let targetHeadRotX = 0;
let targetHeadRotZ = 0;
let currentHeadRotY = 0;
let currentHeadRotX = 0;
let currentHeadRotZ = 0;

let targetPupilX = 0;
let targetPupilY = 0;
let currentPupilX = 0;
let currentPupilY = 0;

export function initCharacter(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return false;

  try {
    const width = container.clientWidth || 240;
    const height = container.clientHeight || 200;

    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    camera.position.set(0, 0, 4.2);

    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;

    container.appendChild(renderer.domElement);
    isWebGLAvailable = true;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0x00d2ff, 1.8);
    keyLight.position.set(3, 4, 4);
    scene.add(keyLight);

    const rimLight = new THREE.DirectionalLight(0x9d4edd, 1.6);
    rimLight.position.set(-3, -2, -2);
    scene.add(rimLight);

    const fillLight = new THREE.DirectionalLight(0x0078ff, 0.9);
    fillLight.position.set(0, -3, 2);
    scene.add(fillLight);

    // Build Character
    createCharacterMesh();

    // Resize observer
    window.addEventListener('resize', () => {
      if (!container) return;
      const w = container.clientWidth || 240;
      const h = container.clientHeight || 200;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });

    // Pause rendering when tab is hidden
    document.addEventListener('visibilitychange', () => {
      isAnimating = !document.hidden;
      if (isAnimating) {
        requestAnimationFrame(animate);
      }
    });

    requestAnimationFrame(animate);
    return true;
  } catch (err) {
    console.warn("WebGL initialization failed, falling back to 2D orb:", err);
    isWebGLAvailable = false;
    return false;
  }
}

function createCharacterMesh() {
  characterGroup = new THREE.Group();
  scene.add(characterGroup);

  // 1. Head (smooth rounded sphere)
  const headGeo = new THREE.SphereGeometry(1.0, 48, 48);
  const headMat = new THREE.MeshStandardMaterial({
    color: 0x1e293b,
    roughness: 0.25,
    metalness: 0.15,
    emissive: 0x091b33,
    emissiveIntensity: 0.35
  });
  headMesh = new THREE.Mesh(headGeo, headMat);
  characterGroup.add(headMesh);

  // Outer subtle glowing aura sphere
  const auraGeo = new THREE.SphereGeometry(1.05, 32, 32);
  const auraMat = new THREE.MeshBasicMaterial({
    color: 0x00d2ff,
    transparent: true,
    opacity: 0.08,
    side: THREE.BackSide
  });
  const auraMesh = new THREE.Mesh(auraGeo, auraMat);
  headMesh.add(auraMesh);

  // 2. Eyes
  const eyeRadius = 0.16;
  const eyeGeo = new THREE.SphereGeometry(eyeRadius, 24, 24);
  const eyeScleraMat = new THREE.MeshBasicMaterial({ color: 0xebf8ff });

  const pupilGeo = new THREE.SphereGeometry(0.085, 16, 16);
  const pupilMat = new THREE.MeshBasicMaterial({ color: 0x00b4d8 });

  // Left Eye
  leftEyeGroup = new THREE.Group();
  leftEyeGroup.position.set(-0.35, 0.12, 0.88);
  const leftSclera = new THREE.Mesh(eyeGeo, eyeScleraMat);
  leftEyeGroup.add(leftSclera);

  leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
  leftPupil.position.set(0, 0, 0.09);
  leftEyeGroup.add(leftPupil);

  // Left Eyelid (for blinking)
  const eyelidGeo = new THREE.SphereGeometry(eyeRadius * 1.05, 24, 24, 0, Math.PI * 2, 0, Math.PI * 0.5);
  const eyelidMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.3 });
  leftEyelid = new THREE.Mesh(eyelidGeo, eyelidMat);
  leftEyelid.rotation.x = -Math.PI / 2;
  leftEyelid.scale.set(1, 0, 1);
  leftEyeGroup.add(leftEyelid);

  headMesh.add(leftEyeGroup);

  // Right Eye
  rightEyeGroup = new THREE.Group();
  rightEyeGroup.position.set(0.35, 0.12, 0.88);
  const rightSclera = new THREE.Mesh(eyeGeo, eyeScleraMat);
  rightEyeGroup.add(rightSclera);

  rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
  rightPupil.position.set(0, 0, 0.09);
  rightEyeGroup.add(rightPupil);

  rightEyelid = new THREE.Mesh(eyelidGeo, eyelidMat);
  rightEyelid.rotation.x = -Math.PI / 2;
  rightEyelid.scale.set(1, 0, 1);
  rightEyeGroup.add(rightEyelid);

  headMesh.add(rightEyeGroup);

  // 3. Eyebrows
  const browGeo = new THREE.BoxGeometry(0.24, 0.04, 0.05);
  const browMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });

  leftEyebrow = new THREE.Mesh(browGeo, browMat);
  leftEyebrow.position.set(-0.35, 0.38, 0.9);
  headMesh.add(leftEyebrow);

  rightEyebrow = new THREE.Mesh(browGeo, browMat);
  rightEyebrow.position.set(0.35, 0.38, 0.9);
  headMesh.add(rightEyebrow);

  // 4. Mouth Mesh (Torus or morphing oval)
  const mouthGeo = new THREE.TorusGeometry(0.18, 0.04, 16, 32, Math.PI);
  const mouthMat = new THREE.MeshStandardMaterial({
    color: 0x00d2ff,
    emissive: 0x0078ff,
    emissiveIntensity: 0.6,
    roughness: 0.2
  });
  mouthMesh = new THREE.Mesh(mouthGeo, mouthMat);
  mouthMesh.position.set(0, -0.32, 0.88);
  mouthMesh.rotation.x = Math.PI * 0.9;
  mouthMesh.rotation.z = Math.PI;
  headMesh.add(mouthMesh);
}

// State Controller
export function setCharacterState(state) {
  currentState = state;

  switch (state) {
    case 'idle':
      targetHeadRotX = 0;
      targetHeadRotY = 0;
      targetHeadRotZ = 0;
      targetPupilX = 0;
      targetPupilY = 0;
      isSpeakingAnim = false;
      targetMouthOpenness = 0;
      leftEyebrow.rotation.z = 0;
      rightEyebrow.rotation.z = 0;
      break;

    case 'listening':
      // Head tilt, attentive eyes
      targetHeadRotX = 0.05;
      targetHeadRotY = 0.12;
      targetHeadRotZ = -0.15;
      targetPupilX = -0.02;
      targetPupilY = 0.02;
      isSpeakingAnim = false;
      targetMouthOpenness = 0.1;
      leftEyebrow.rotation.z = 0.12;
      rightEyebrow.rotation.z = -0.12;
      break;

    case 'thinking':
      // Eyes look up and to the side, slight head inclination
      targetHeadRotX = -0.12;
      targetHeadRotY = -0.2;
      targetHeadRotZ = 0.05;
      targetPupilX = 0.06;
      targetPupilY = 0.06;
      isSpeakingAnim = false;
      targetMouthOpenness = 0.05;
      leftEyebrow.rotation.z = -0.15;
      rightEyebrow.rotation.z = 0.15;
      break;

    case 'speaking':
      targetHeadRotX = 0;
      targetHeadRotY = 0;
      targetHeadRotZ = 0;
      targetPupilX = 0;
      targetPupilY = 0;
      isSpeakingAnim = true;
      leftEyebrow.rotation.z = 0.05;
      rightEyebrow.rotation.z = -0.05;
      break;
  }
}

// Smooth mouth phoneme / syllable trigger
export function triggerMouthPhoneme(strength = 0.6) {
  if (currentState === 'speaking' || isSpeakingAnim) {
    targetMouthOpenness = Math.min(1.0, strength + (Math.random() * 0.3 - 0.1));
  }
}

export function closeMouthImmediately() {
  targetMouthOpenness = 0;
  mouthOpenness = 0;
  isSpeakingAnim = false;
}

// Animation Loop
function animate(timestamp) {
  if (!isAnimating) return;
  requestAnimationFrame(animate);

  const delta = 0.016; // approximate delta
  animTime += delta;

  // 1. Head sway and subtle breathing
  let breathY = 0;
  let breathRotZ = 0;

  if (currentState === 'idle') {
    breathY = Math.sin(animTime * 1.5) * 0.04;
    breathRotZ = Math.cos(animTime * 0.8) * 0.03;
  } else if (currentState === 'speaking') {
    breathY = Math.sin(animTime * 5.0) * 0.02;
    breathRotZ = Math.sin(animTime * 3.0) * 0.02;
  }

  // Smooth slerp/lerp rotations
  currentHeadRotX += (targetHeadRotX - currentHeadRotX) * 0.1;
  currentHeadRotY += (targetHeadRotY - currentHeadRotY) * 0.1;
  currentHeadRotZ += (targetHeadRotZ + breathRotZ - currentHeadRotZ) * 0.1;

  if (characterGroup) {
    characterGroup.position.y = breathY;
    characterGroup.rotation.x = currentHeadRotX;
    characterGroup.rotation.y = currentHeadRotY;
    characterGroup.rotation.z = currentHeadRotZ;
  }

  // Smooth pupil motion
  currentPupilX += (targetPupilX - currentPupilX) * 0.15;
  currentPupilY += (targetPupilY - currentPupilY) * 0.15;
  if (leftPupil && rightPupil) {
    leftPupil.position.x = currentPupilX;
    leftPupil.position.y = currentPupilY;
    rightPupil.position.x = currentPupilX;
    rightPupil.position.y = currentPupilY;
  }

  // 2. Random Blinking (every 2.5 - 5 seconds)
  if (animTime >= nextBlinkTime && !isBlinking) {
    isBlinking = true;
    blinkProgress = 0;
  }

  if (isBlinking) {
    blinkProgress += delta * 12.0; // blink duration ~0.15s
    const blinkScale = Math.sin(Math.min(blinkProgress, Math.PI));
    if (leftEyelid && rightEyelid) {
      leftEyelid.scale.y = blinkScale;
      rightEyelid.scale.y = blinkScale;
    }
    if (blinkProgress >= Math.PI) {
      isBlinking = false;
      leftEyelid.scale.y = 0;
      rightEyelid.scale.y = 0;
      nextBlinkTime = animTime + 2.0 + Math.random() * 3.5;
    }
  }

  // 3. Mouth Animation (Speaking mode)
  if (isSpeakingAnim) {
    // Continuous dynamic modulation with random pauses for words
    const noise = Math.sin(animTime * 16.0) * 0.4 + Math.sin(animTime * 25.0) * 0.3;
    targetMouthOpenness = Math.max(0.05, Math.min(0.9, 0.4 + noise * 0.5));
  } else if (currentState !== 'listening') {
    targetMouthOpenness = 0;
  }

  mouthOpenness += (targetMouthOpenness - mouthOpenness) * 0.25;

  if (mouthMesh) {
    // Scale mouth Y for opening/closing, and slight X stretching for speech realism
    const openY = Math.max(0.1, mouthOpenness * 2.2);
    const stretchX = 1.0 + mouthOpenness * 0.15;
    mouthMesh.scale.set(stretchX, openY, 1.0);
  }

  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}
