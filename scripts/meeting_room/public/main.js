import * as THREE from 'three';

// ============================================================
// Y* Bridge Labs — Meeting Room: MVP Trio Avatar Scene
// Agents: Aiden (CEO), Sofia (CMO), Samantha (Secretary)
// ============================================================

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
scene.background = new THREE.Color(0x2c2420);

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

const fillLight = new THREE.PointLight(0xff9944, 0.5, 10);
fillLight.position.set(-3, 2, 1);
scene.add(fillLight);

// --- Floor ---
const floorGeo = new THREE.PlaneGeometry(10, 10);
const floorMat = new THREE.MeshStandardMaterial({
  color: 0x8b7355,
  roughness: 0.85,
  metalness: 0.0
});
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// --- Back Wall ---
const wallGeo = new THREE.PlaneGeometry(10, 4);
const wallMat = new THREE.MeshStandardMaterial({
  color: 0x9e5a3c,
  roughness: 0.95,
  metalness: 0.0
});
const wall = new THREE.Mesh(wallGeo, wallMat);
wall.position.set(0, 2, -5);
wall.receiveShadow = true;
scene.add(wall);

// ============================================================
// AGENT DEFINITIONS — MVP Trio
// ============================================================

const AGENTS = [
  {
    name: 'Aiden',
    role: 'CEO',
    color: 0x4488cc,         // corporate blue
    position: [0, 0, 0],    // center
  },
  {
    name: 'Sofia',
    role: 'CMO',
    color: 0xcc6688,         // warm rose
    position: [-1.5, 0, 0.4], // left, slightly forward
  },
  {
    name: 'Samantha',
    role: 'Secretary',
    color: 0x66aa88,         // sage green
    position: [1.5, 0, 0.4],  // right, slightly forward
  },
];

// ============================================================
// BUILD AVATAR PLACEHOLDERS + HOTSPOTS
// ============================================================

const avatarGroup = new THREE.Group();
scene.add(avatarGroup);

const hotspots = [];       // invisible spheres for raycasting
const agentMeshes = [];    // visible avatar prisms
const badgeOverlay = document.getElementById('badge-overlay');

// Build each agent
AGENTS.forEach((agent) => {
  const group = new THREE.Group();
  group.position.set(agent.position[0], agent.position[1], agent.position[2]);

  // --- Humanoid placeholder: torso + head ---
  // Torso (tall rectangular prism)
  const torsoGeo = new THREE.BoxGeometry(0.45, 1.2, 0.25);
  const torsoMat = new THREE.MeshStandardMaterial({
    color: agent.color,
    roughness: 0.35,
    metalness: 0.15,
  });
  const torso = new THREE.Mesh(torsoGeo, torsoMat);
  torso.position.y = 0.6;
  torso.castShadow = true;
  group.add(torso);

  // Head (sphere)
  const headGeo = new THREE.SphereGeometry(0.18, 16, 12);
  const headMat = new THREE.MeshStandardMaterial({
    color: agent.color,
    roughness: 0.3,
    metalness: 0.1,
  });
  const head = new THREE.Mesh(headGeo, headMat);
  head.position.y = 1.38;
  head.castShadow = true;
  group.add(head);

  // --- Clickable hotspot (invisible sphere wrapping entire figure) ---
  const hotspotGeo = new THREE.SphereGeometry(0.5, 8, 6);
  const hotspotMat = new THREE.MeshBasicMaterial({
    transparent: true,
    opacity: 0.0,
    depthWrite: false,
  });
  const hotspot = new THREE.Mesh(hotspotGeo, hotspotMat);
  hotspot.position.y = 0.8;
  hotspot.userData = { agentName: agent.name, agentRole: agent.role };
  group.add(hotspot);
  hotspots.push(hotspot);

  // Store references for outline effect
  agentMeshes.push({ torso, head, group, agent });

  avatarGroup.add(group);

  // --- HTML Name Badge ---
  const badge = document.createElement('div');
  badge.className = 'agent-badge';
  badge.id = `badge-${agent.name.toLowerCase()}`;
  badge.innerHTML = `
    <div class="agent-badge-inner">
      <span class="badge-name">${agent.name}</span>
      <span class="badge-role">${agent.role}</span>
    </div>
  `;
  badgeOverlay.appendChild(badge);
});

// ============================================================
// RAYCASTER — Click + Hover Detection
// ============================================================

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let hoveredAgent = null;
let selectedAgent = null;

// --- Outline materials for hover/select ---
const outlineMat = new THREE.MeshBasicMaterial({
  color: 0x00dcff,
  transparent: true,
  opacity: 0.15,
  side: THREE.BackSide,
});

// Create outline meshes for each agent
agentMeshes.forEach((entry) => {
  // Torso outline
  const torsoOutGeo = new THREE.BoxGeometry(0.52, 1.27, 0.32);
  const torsoOut = new THREE.Mesh(torsoOutGeo, outlineMat.clone());
  torsoOut.position.copy(entry.torso.position);
  torsoOut.visible = false;
  entry.group.add(torsoOut);
  entry.torsoOutline = torsoOut;

  // Head outline
  const headOutGeo = new THREE.SphereGeometry(0.22, 16, 12);
  const headOut = new THREE.Mesh(headOutGeo, outlineMat.clone());
  headOut.position.copy(entry.head.position);
  headOut.visible = false;
  entry.group.add(headOut);
  entry.headOutline = headOut;
});

function setOutlineVisible(entry, visible) {
  entry.torsoOutline.visible = visible;
  entry.headOutline.visible = visible;
}

function updatePointer(event) {
  pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
  pointer.y = -(event.clientY / window.innerHeight) * 2 + 1;
}

// Hover
renderer.domElement.addEventListener('pointermove', (event) => {
  updatePointer(event);
  raycaster.setFromCamera(pointer, camera);
  const intersects = raycaster.intersectObjects(hotspots);

  const newHovered = intersects.length > 0 ? intersects[0].object.userData.agentName : null;

  if (newHovered !== hoveredAgent) {
    // Clear old hover
    if (hoveredAgent) {
      const badge = document.getElementById(`badge-${hoveredAgent.toLowerCase()}`);
      if (badge) badge.classList.remove('hovered');
      const entry = agentMeshes.find(e => e.agent.name === hoveredAgent);
      if (entry && hoveredAgent !== selectedAgent) setOutlineVisible(entry, false);
    }
    // Set new hover
    hoveredAgent = newHovered;
    if (hoveredAgent) {
      const badge = document.getElementById(`badge-${hoveredAgent.toLowerCase()}`);
      if (badge) badge.classList.add('hovered');
      const entry = agentMeshes.find(e => e.agent.name === hoveredAgent);
      if (entry) setOutlineVisible(entry, true);
      renderer.domElement.style.cursor = 'pointer';
    } else {
      renderer.domElement.style.cursor = 'default';
    }
  }
});

// ============================================================
// VOICE MODE — STT + /speak TTS round-trip
// ============================================================

let voiceActive = false;
let recognition = null;
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const sttSupported = !!SpeechRecognition;

const rttOverlay = document.getElementById('rtt-overlay');
const micIndicator = document.getElementById('mic-indicator');

function updateRTT(ms, backend) {
  if (rttOverlay) {
    rttOverlay.textContent = `RTT: ${Math.round(ms)} ms [${backend}]`;
    rttOverlay.style.opacity = '1';
  }
}

function setMicState(state) {
  // state: 'off' | 'listening' | 'processing' | 'unsupported'
  if (!micIndicator) return;
  micIndicator.dataset.state = state;
  const labels = { off: 'MIC OFF', listening: 'LISTENING...', processing: 'PROCESSING...', unsupported: 'STT N/A' };
  micIndicator.textContent = labels[state] || state;
}

async function speakToAgent(agentName, text) {
  setMicState('processing');
  const t0 = performance.now();
  try {
    const resp = await fetch('/speak', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent: agentName.toLowerCase(), text }),
    });
    const serverRtt = resp.headers.get('X-Round-Trip-Ms') || '?';
    const backend = resp.headers.get('X-TTS-Backend') || 'unknown';
    const clientRtt = performance.now() - t0;

    console.log(`[Y* Voice] Server RTT: ${serverRtt}ms, Client RTT: ${Math.round(clientRtt)}ms, Backend: ${backend}`);
    updateRTT(clientRtt, backend);

    const contentType = resp.headers.get('Content-Type') || '';
    if (contentType.startsWith('audio/')) {
      const audioBlob = await resp.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.onended = () => URL.revokeObjectURL(audioUrl);
      await audio.play();
    } else {
      // text_fallback — log it
      const data = await resp.json();
      console.log(`[Y* Voice] Text fallback:`, data);
      updateRTT(data.rtt_ms || clientRtt, 'text_fallback');
    }
  } catch (err) {
    console.error('[Y* Voice] /speak request failed:', err);
    updateRTT(-1, 'error');
  }
  setMicState('off');
}

function startListening(agentName) {
  if (!sttSupported) {
    setMicState('unsupported');
    console.warn('[Y* Voice] Web Speech API not supported in this browser.');
    // Fallback: prompt for text input
    const text = prompt(`Speech-to-text unavailable. Type your message to ${agentName}:`);
    if (text) speakToAgent(agentName, text);
    return;
  }

  if (voiceActive) return; // already listening
  voiceActive = true;
  setMicState('listening');

  recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  recognition.continuous = false;

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    console.log(`[Y* Voice] Heard: "${transcript}"`);
    voiceActive = false;
    speakToAgent(agentName, transcript);
  };

  recognition.onerror = (event) => {
    console.error('[Y* Voice] STT error:', event.error);
    voiceActive = false;
    setMicState('off');
  };

  recognition.onend = () => {
    if (voiceActive) {
      voiceActive = false;
      setMicState('off');
    }
  };

  recognition.start();
  console.log(`[Y* Voice] Listening for speech to ${agentName}...`);
}

// ============================================================
// CONVERSATION PANEL — slide-in dialogue UI
// ============================================================

const convPanel = document.getElementById('conv-panel');
const convAgentName = document.getElementById('conv-agent-name');
const convAgentRole = document.getElementById('conv-agent-role');
const convTranscript = document.getElementById('conv-transcript');
const convTextInput = document.getElementById('conv-text-input');
const convSendBtn = document.getElementById('conv-send-btn');
const convMicBtn = document.getElementById('conv-mic-btn');
const convCloseBtn = document.getElementById('conv-close');

let panelAgent = null;         // currently open agent name
const transcripts = {};        // per-agent transcript history (last 10)
const MAX_TRANSCRIPT = 10;

function openPanel(agentName, agentRole) {
  panelAgent = agentName;
  convAgentName.textContent = agentName;
  convAgentRole.textContent = agentRole;
  convPanel.classList.add('open');
  renderTranscript(agentName);
  convTextInput.focus();
}

function closePanel() {
  convPanel.classList.remove('open');
  panelAgent = null;
}

function addBubble(agentName, sender, text) {
  if (!transcripts[agentName]) transcripts[agentName] = [];
  transcripts[agentName].push({ sender, text });
  // Keep last MAX_TRANSCRIPT exchanges (each exchange = 2 entries)
  if (transcripts[agentName].length > MAX_TRANSCRIPT * 2) {
    transcripts[agentName] = transcripts[agentName].slice(-MAX_TRANSCRIPT * 2);
  }
  renderTranscript(agentName);
}

function renderTranscript(agentName) {
  convTranscript.innerHTML = '';
  const entries = transcripts[agentName] || [];
  entries.forEach(({ sender, text }) => {
    const bubble = document.createElement('div');
    bubble.className = `conv-bubble ${sender}`;
    bubble.textContent = text;
    convTranscript.appendChild(bubble);
  });
  convTranscript.scrollTop = convTranscript.scrollHeight;
}

async function sendDialogue(agentName, text) {
  if (!text.trim()) return;
  addBubble(agentName, 'user', text);
  try {
    const resp = await fetch('/dialogue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent: agentName.toLowerCase(), text }),
    });
    const data = await resp.json();
    addBubble(agentName, 'agent', data.response);
    // Also speak the response via TTS
    speakToAgent(agentName, data.response);
  } catch (err) {
    console.error('[Y* Dialogue] request failed:', err);
    addBubble(agentName, 'agent', '[Error: could not reach server]');
  }
}

// Send button
convSendBtn.addEventListener('click', () => {
  if (!panelAgent) return;
  const text = convTextInput.value;
  convTextInput.value = '';
  sendDialogue(panelAgent, text);
});

// Enter key sends
convTextInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    convSendBtn.click();
  }
});

// Mic button — voice input into panel
convMicBtn.addEventListener('click', () => {
  if (!panelAgent) return;
  if (!sttSupported) {
    const text = prompt(`Speech-to-text unavailable. Type your message to ${panelAgent}:`);
    if (text) sendDialogue(panelAgent, text);
    return;
  }
  if (voiceActive) return;
  voiceActive = true;
  convMicBtn.classList.add('listening');
  setMicState('listening');

  const rec = new SpeechRecognition();
  rec.lang = 'en-US';
  rec.interimResults = false;
  rec.maxAlternatives = 1;
  rec.continuous = false;

  rec.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    voiceActive = false;
    convMicBtn.classList.remove('listening');
    setMicState('off');
    sendDialogue(panelAgent, transcript);
  };
  rec.onerror = () => {
    voiceActive = false;
    convMicBtn.classList.remove('listening');
    setMicState('off');
  };
  rec.onend = () => {
    voiceActive = false;
    convMicBtn.classList.remove('listening');
    setMicState('off');
  };
  rec.start();
});

// Close button
convCloseBtn.addEventListener('click', closePanel);

// Click — select agent + open conversation panel
renderer.domElement.addEventListener('click', (event) => {
  updatePointer(event);
  raycaster.setFromCamera(pointer, camera);
  const intersects = raycaster.intersectObjects(hotspots);

  // Deselect previous
  if (selectedAgent) {
    const badge = document.getElementById(`badge-${selectedAgent.toLowerCase()}`);
    if (badge) badge.classList.remove('selected');
    const entry = agentMeshes.find(e => e.agent.name === selectedAgent);
    if (entry) setOutlineVisible(entry, false);
  }

  if (intersects.length > 0) {
    const { agentName, agentRole } = intersects[0].object.userData;
    selectedAgent = agentName;
    console.log(`[Y* Meeting Room] Clicked: ${agentName} (${agentRole}) — opening conversation panel`);

    const badge = document.getElementById(`badge-${agentName.toLowerCase()}`);
    if (badge) badge.classList.add('selected');
    const entry = agentMeshes.find(e => e.agent.name === agentName);
    if (entry) setOutlineVisible(entry, true);

    // Open conversation panel instead of direct voice
    openPanel(agentName, agentRole);
  } else {
    selectedAgent = null;
    closePanel();
  }
});

// ============================================================
// ANIMATION LOOP — Badge Projection + Gentle Idle
// ============================================================

const clock = new THREE.Clock();
const tempVec = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);

  const elapsed = clock.getElapsedTime();

  // Subtle idle breathing motion for each avatar
  agentMeshes.forEach((entry, i) => {
    const phase = elapsed * 0.8 + i * 2.1;
    entry.group.position.y = Math.sin(phase) * 0.015;
  });

  // Project 3D badge positions to 2D screen coordinates
  AGENTS.forEach((agent, i) => {
    const group = agentMeshes[i].group;
    // Badge anchor point: above head
    tempVec.set(
      group.position.x + agent.position[0] * 0,
      1.65 + group.position.y,
      group.position.z + agent.position[2] * 0
    );
    // Apply parent transforms
    group.localToWorld(tempVec.copy(new THREE.Vector3(0, 1.65, 0)));

    tempVec.project(camera);

    const x = (tempVec.x * 0.5 + 0.5) * window.innerWidth;
    const y = (-tempVec.y * 0.5 + 0.5) * window.innerHeight;

    const badge = document.getElementById(`badge-${agent.name.toLowerCase()}`);
    if (badge) {
      // Hide if behind camera
      if (tempVec.z > 1) {
        badge.style.opacity = '0';
      } else {
        badge.style.opacity = '1';
        badge.style.left = `${x}px`;
        badge.style.top = `${y}px`;
      }
    }
  });

  renderer.render(scene, camera);
}

animate();

// --- Resize handler ---
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

console.log('[Y* Meeting Room] MVP trio loaded — Aiden, Sofia, Samantha');
console.log('[Y* Meeting Room] Click any avatar to select. Hover for cyan outline.');
