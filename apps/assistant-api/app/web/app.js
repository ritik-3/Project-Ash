const INTERACTION_MODES = {
  DIRECT_VOICE: "DIRECT_VOICE",
  AUTO_CONTINUOUS: "AUTO_CONTINUOUS",
  WAKE_WORD_TRIGGERED: "WAKE_WORD_TRIGGERED",
  SPACEBAR_HOLD: "SPACEBAR_HOLD",
};

const RECORDING_STATES = {
  IDLE: "IDLE",
  LISTENING: "LISTENING",
  RECORDING: "RECORDING",
  PROCESSING: "PROCESSING",
};

const state = {
  sessionId: "default",
  status: "idle",
  wakeWordModel: "",
  autoConversationEnabled: true,
  autoLoopInFlight: false,
  autoLoopBackoffMs: 0,
  autoLoopLockHeld: false,
  autoLoopHeartbeatId: null,
  tabId: `tab-${Math.random().toString(36).slice(2)}`,
  interactionMode: INTERACTION_MODES.DIRECT_VOICE,
  recordingState: RECORDING_STATES.IDLE,
  isSpacebarPressed: false,
  audio: {
    stream: null,
    context: null,
    analyser: null,
    rafId: null,
  },
};

const AUTO_LOOP_LOCK_KEY = "ash:auto-loop-owner";
const AUTO_LOOP_HEARTBEAT_MS = 1500;
const AUTO_LOOP_STALE_MS = 6000;

// DOM Elements
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const orb = document.getElementById("orb");
const statusIndicator = document.getElementById("statusIndicator");
const statusIndicatorText = document.getElementById("statusIndicatorText");
const meterFill = document.getElementById("meterFill");
const chatLog = document.getElementById("chatLog");
const textInput = document.getElementById("textInput");
const sendButton = document.getElementById("sendButton");
const dockMicBtn = document.getElementById("dockMicBtn");
const micButton = document.getElementById("micButton"); // The visualizer toggle
const wakeToggle = document.getElementById("wakeToggle");
const segments = document.querySelectorAll(".segment");

function setStatus(next) {
  state.status = next;
  statusDot.className = `status-dot ${next}`;
  statusText.textContent = next;
}

function setRecordingState(newState) {
  state.recordingState = newState;
  
  // Update status indicator animation
  statusIndicator.className = `status-indicator ${newState.toLowerCase()}`;
  
  let label = "Idle";
  if (newState === RECORDING_STATES.RECORDING) label = "Recording";
  if (newState === RECORDING_STATES.PROCESSING) label = "Processing";
  if (newState === RECORDING_STATES.LISTENING) label = "Listening";
  
  statusIndicatorText.textContent = label;

  if (newState === RECORDING_STATES.RECORDING) {
    if (!state.audio.stream) {
      enableMicVisualizer().catch((err) => {
        console.error("Failed to enable mic visualizer:", err);
      });
    }
  }

  if (window.OrbVisualizer) {
    window.OrbVisualizer.setState(newState);
  }
}

function updateModeUI() {
  segments.forEach((btn) => {
    if (btn.dataset.mode === state.interactionMode) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Update Dock Mic Icon style based on mode
  if (state.interactionMode === INTERACTION_MODES.AUTO_CONTINUOUS) {
    dockMicBtn.innerHTML = `<span class="mic-icon">${state.autoConversationEnabled ? "⏸️" : "▶️"}</span>`;
    dockMicBtn.title = state.autoConversationEnabled ? "Pause Conversation" : "Start Conversation";
  } else {
    dockMicBtn.innerHTML = `<span class="mic-icon">🎤</span>`;
    dockMicBtn.title = "Trigger Voice";
  }
}

function setInteractionMode(newMode) {
  if (state.recordingState !== RECORDING_STATES.IDLE) {
    console.warn("Cannot switch mode while recording");
    return;
  }

  // Cleanup old mode
  if (state.interactionMode === INTERACTION_MODES.AUTO_CONTINUOUS) {
    state.autoConversationEnabled = false;
  }

  if (state.interactionMode === INTERACTION_MODES.WAKE_WORD_TRIGGERED) {
    state.autoConversationEnabled = false;
  }

  // Set new mode
  state.interactionMode = newMode;
  setRecordingState(RECORDING_STATES.IDLE);
  updateModeUI();

  // For wake mode, immediately start listening
  if (newMode === INTERACTION_MODES.WAKE_WORD_TRIGGERED) {
    state.autoConversationEnabled = true;
    startWakeWordLoop();
  }
}

function nowMs() {
  return Date.now();
}

function readAutoLoopLock() {
  try {
    const raw = localStorage.getItem(AUTO_LOOP_LOCK_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed.id !== "string" || typeof parsed.ts !== "number") return null;
    return parsed;
  } catch (_err) {
    return null;
  }
}

function writeAutoLoopLock() {
  const payload = { id: state.tabId, ts: nowMs() };
  localStorage.setItem(AUTO_LOOP_LOCK_KEY, JSON.stringify(payload));
}

function tryAcquireAutoLoopLock() {
  const lock = readAutoLoopLock();
  const stale = !lock || nowMs() - lock.ts > AUTO_LOOP_STALE_MS;
  const mine = lock && lock.id === state.tabId;

  if (stale || mine) {
    writeAutoLoopLock();
    state.autoLoopLockHeld = true;
    return true;
  }

  state.autoLoopLockHeld = false;
  return false;
}

function releaseAutoLoopLock() {
  const lock = readAutoLoopLock();
  if (lock && lock.id === state.tabId) {
    localStorage.removeItem(AUTO_LOOP_LOCK_KEY);
  }
  state.autoLoopLockHeld = false;
}

function addMessage(role, content) {
  const row = document.createElement("div");
  row.className = `msg ${role}`;
  row.textContent = content;
  chatLog.appendChild(row);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Request failed with ${res.status}`);
  }
  return await res.json();
}

const seenSystem = new Set();
function addSystemOnce(message) {
  if (seenSystem.has(message)) return;
  seenSystem.add(message);
  addMessage("system", message);
}

async function pollHealth() {
  try {
    const data = await api("/api/v1/health", { method: "GET" });
    state.wakeWordModel = data.wake_word_model || "";
    if (state.status === "error") {
      setStatus("idle");
    }
    if (!data.voice_model_ready) {
      addSystemOnce("TTS is using Windows fallback voice (Piper model not configured).");
    }
    if (state.wakeWordModel) {
      addSystemOnce(`Wake-word model is '${state.wakeWordModel}'.`);
    }
  } catch (_err) {
    setStatus("error");
  }
}

async function sendTextMessage() {
  const message = textInput.value.trim();
  if (!message) return;

  textInput.value = "";
  addMessage("user", message);

  try {
    setStatus("busy");
    const data = await api("/api/v1/chat", {
      method: "POST",
      body: JSON.stringify({
        session_id: state.sessionId,
        message,
      }),
    });
    addMessage("assistant", data.reply);
    setStatus("active");
  } catch (err) {
    setStatus("error");
    addMessage("system", `Chat failed: ${String(err.message || err)}`);
  }
}

function applyVoiceTurnResult(data, { manual = false } = {}) {
  if (data.transcript) addMessage("user", data.transcript);
  if (data.reply) {
    addMessage("assistant", data.reply);
    if (window.OrbVisualizer) {
      window.OrbVisualizer.setState('SPEAKING');
      // Simulate speaking duration based on text length
      const duration = Math.max(1500, Math.min(6000, data.reply.length * 60));
      setTimeout(() => {
        if (state.recordingState === RECORDING_STATES.IDLE && window.OrbVisualizer) {
          window.OrbVisualizer.setState('IDLE');
        }
      }, duration);
    }
  }

  if (data.status === "ok") {
    state.autoLoopBackoffMs = 0;
    setStatus("active");
    return;
  }

  const detailText = String(data.detail || "").toLowerCase();
  const isSilentNoSpeech = detailText.includes("no speech");
  if (data.status === "timeout" || isSilentNoSpeech) {
    state.autoLoopBackoffMs = 2600;
    if (manual && data.status === "timeout" && wakeToggle && wakeToggle.checked) {
      addMessage("system", `Wake word timeout. Say '${state.wakeWordModel || "configured wake word"}'`);
    }
    setStatus("idle");
    return;
  }

  setStatus("error");
  state.autoLoopBackoffMs = 3200;
  addMessage("system", data.detail || `Voice status: ${data.status}`);
}

async function requestVoiceTurn(speakReply = true) {
  return await api("/api/v1/voice/turn", {
    method: "POST",
    body: JSON.stringify({
      session_id: state.sessionId,
      wait_for_wake_word: wakeToggle ? Boolean(wakeToggle.checked) : false,
      speak_reply: Boolean(speakReply),
    }),
  });
}

async function runVoiceTurn() {
  if (state.recordingState !== RECORDING_STATES.IDLE) {
    console.warn("Already recording or processing");
    return;
  }

  try {
    setRecordingState(RECORDING_STATES.RECORDING);
    setStatus("busy");
    const data = await requestVoiceTurn(true);
    applyVoiceTurnResult(data, { manual: true });
  } catch (err) {
    setStatus("error");
    addMessage("system", `Voice turn failed: ${String(err.message || err)}`);
  } finally {
    setRecordingState(RECORDING_STATES.IDLE);
  }
}

async function runVoiceTurnAuto() {
  if (state.autoLoopInFlight) return;
  state.autoLoopInFlight = true;
  try {
    setStatus("busy");
    setRecordingState(RECORDING_STATES.PROCESSING);
    const data = await requestVoiceTurn(true);
    applyVoiceTurnResult(data, { manual: false });
  } catch (err) {
    setStatus("error");
    addMessage("system", `Auto voice loop failed: ${String(err.message || err)}`);
  } finally {
    state.autoLoopInFlight = false;
    setRecordingState(RECORDING_STATES.IDLE);
  }
}

async function startWakeWordLoop() {
  if (state.interactionMode !== INTERACTION_MODES.WAKE_WORD_TRIGGERED) return;
  if (!tryAcquireAutoLoopLock()) {
    addSystemOnce("Wake word listening is running in another tab. Passive mode.");
    return;
  }

  addSystemOnce(`Wake-word model is '${state.wakeWordModel || "hey_jarvis"}'. Say the wake phrase.`);

  const loop = async () => {
    if (state.interactionMode !== INTERACTION_MODES.WAKE_WORD_TRIGGERED || !state.autoConversationEnabled) return;
    if (!state.autoLoopLockHeld && !tryAcquireAutoLoopLock()) return;
    
    await runVoiceTurnAuto();
    const nextDelayMs = Math.max(state.status === "error" ? 3000 : 1200, state.autoLoopBackoffMs || 0);
    setTimeout(loop, nextDelayMs);
  };
  void loop();
}

function startAutoConversationLoop() {
  if (!state.autoConversationEnabled || state.interactionMode !== INTERACTION_MODES.AUTO_CONTINUOUS) return;
  if (!tryAcquireAutoLoopLock()) {
    addSystemOnce("Auto conversation is running in another tab. Passive mode.");
    return;
  }

  if (state.autoLoopHeartbeatId) clearInterval(state.autoLoopHeartbeatId);
  state.autoLoopHeartbeatId = setInterval(() => {
    if (state.autoLoopLockHeld) writeAutoLoopLock();
  }, AUTO_LOOP_HEARTBEAT_MS);

  addSystemOnce("Auto conversation is running in the background.");

  const loop = async () => {
    if (!state.autoConversationEnabled || state.interactionMode !== INTERACTION_MODES.AUTO_CONTINUOUS) return;
    if (!state.autoLoopLockHeld && !tryAcquireAutoLoopLock()) return;
    
    await runVoiceTurnAuto();
    const nextDelayMs = Math.max(state.status === "error" ? 3000 : 1200, state.autoLoopBackoffMs || 0);
    setTimeout(loop, nextDelayMs);
  };
  void loop();
}

function animateFromAudio() {
  const analyser = state.audio.analyser;
  if (!analyser) return;

  const data = new Uint8Array(analyser.fftSize);
  analyser.getByteTimeDomainData(data);

  let sum = 0;
  for (let i = 0; i < data.length; i += 1) {
    const normalized = (data[i] - 128) / 128;
    sum += normalized * normalized;
  }

  const rms = Math.sqrt(sum / data.length);
  const clamped = Math.min(1, rms * 5);
  
  if (meterFill) meterFill.style.width = `${(clamped * 100).toFixed(0)}%`;

  if (window.OrbVisualizer) {
    const freqData = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(freqData);
    window.OrbVisualizer.setAudioData(freqData);
  }

  state.audio.rafId = requestAnimationFrame(animateFromAudio);
}

async function enableMicVisualizer() {
  if (state.audio.stream) return;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const context = new AudioContext();
    const source = context.createMediaStreamSource(stream);
    const analyser = context.createAnalyser();
    analyser.fftSize = 1024;
    source.connect(analyser);

    state.audio.stream = stream;
    state.audio.context = context;
    state.audio.analyser = analyser;

    micButton.style.color = "var(--color-success)";
    addSystemOnce("Microphone visualizer enabled.");

    animateFromAudio();
    if (state.status === "idle") setStatus("active");
  } catch (err) {
    setStatus("error");
    addMessage("system", `Mic access failed: ${String(err.message || err)}`);
  }
}

// Event Listeners
sendButton.addEventListener("click", sendTextMessage);
textInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendTextMessage();
  }
});

micButton.addEventListener("click", enableMicVisualizer);

// Segmented Control Listeners
segments.forEach((btn) => {
  btn.addEventListener("click", () => {
    const mode = btn.dataset.mode;
    if (mode && INTERACTION_MODES[mode]) {
      setInteractionMode(INTERACTION_MODES[mode]);
    }
  });
});

// Dock Mic Button Listener
dockMicBtn.addEventListener("click", async () => {
  if (state.interactionMode === INTERACTION_MODES.DIRECT_VOICE || state.interactionMode === INTERACTION_MODES.SPACEBAR_HOLD) {
    await runVoiceTurn();
  } else if (state.interactionMode === INTERACTION_MODES.AUTO_CONTINUOUS) {
    if (!state.autoConversationEnabled) {
      state.autoConversationEnabled = true;
      startAutoConversationLoop();
      updateModeUI();
    } else {
      state.autoConversationEnabled = false;
      updateModeUI();
    }
  }
});

// Spacebar Push-to-Talk
document.addEventListener("keydown", async (e) => {
  if (state.interactionMode !== INTERACTION_MODES.SPACEBAR_HOLD) return;
  if (e.code !== "Space" || e.target === textInput) return; // ignore if typing
  if (state.isSpacebarPressed) return;

  e.preventDefault();
  state.isSpacebarPressed = true;
  setRecordingState(RECORDING_STATES.RECORDING);
});

document.addEventListener("keyup", async (e) => {
  if (state.interactionMode !== INTERACTION_MODES.SPACEBAR_HOLD) return;
  if (e.code !== "Space" || e.target === textInput) return;
  if (!state.isSpacebarPressed) return;

  e.preventDefault();
  state.isSpacebarPressed = false;
  await runVoiceTurn();
});

window.addEventListener("beforeunload", () => {
  if (state.autoLoopHeartbeatId) clearInterval(state.autoLoopHeartbeatId);
  releaseAutoLoopLock();
});

// Init
setStatus("idle");
addSystemOnce("Ash control surface ready.");
updateModeUI();
pollHealth();
setInterval(pollHealth, 3000);
