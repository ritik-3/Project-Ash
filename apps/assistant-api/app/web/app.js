/**
 * Ash Assistant - Web UI Control Surface
 * Refactored voice capture flow: browser audio → server processing
 */

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
  autoConversationEnabled: false,
  autoLoopInFlight: false,
  autoLoopBackoffMs: 0,
  autoLoopLockHeld: false,
  autoLoopHeartbeatId: null,
  tabId: `tab-${Math.random().toString(36).slice(2)}`,
  interactionMode: INTERACTION_MODES.DIRECT_VOICE,
  recordingState: RECORDING_STATES.IDLE,
  isSpacebarPressed: false,
};

const AUTO_LOOP_LOCK_KEY = "ash:auto-loop-owner";
const AUTO_LOOP_HEARTBEAT_MS = 1500;
const AUTO_LOOP_STALE_MS = 6000;

// DOM Elements
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const statusIndicator = document.getElementById("statusIndicator");
const statusIndicatorText = document.getElementById("statusIndicatorText");
const meterFill = document.getElementById("meterFill");
const chatLog = document.getElementById("chatLog");
const textInput = document.getElementById("textInput");
const sendButton = document.getElementById("sendButton");
const dockMicBtn = document.getElementById("dockMicBtn");
const micButton = document.getElementById("micButton");
const wakeToggle = document.getElementById("wakeToggle");
const segments = document.querySelectorAll(".segment");

// ============================================================================
// STATUS & STATE MANAGEMENT
// ============================================================================

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

// ============================================================================
// AUDIO CAPTURE & ENCODING (Browser → Server)
// ============================================================================

/**
 * Request microphone permission from user.
 * @returns {Promise<MediaStream>} Audio stream from microphone
 */
async function requestMicrophoneAccess() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    return stream;
  } catch (err) {
    setStatus("error");
    addMessage("system", `Microphone access denied: ${String(err.message)}`);
    throw err;
  }
}

/**
 * Capture audio from microphone for specified duration.
 * @param {number} durationMs - Duration to capture in milliseconds
 * @returns {Promise<Float32Array>} PCM audio data (16kHz mono)
 */
async function captureAudioMs(durationMs) {
  const stream = await requestMicrophoneAccess();
  const sampleRate = 16000;
  const audioContext = new AudioContext({ sampleRate });
  const source = audioContext.createMediaStreamSource(stream);
  const processor = audioContext.createScriptProcessor(4096, 1, 1);
  const chunks = [];

  processor.onaudioprocess = (e) => {
    const channelData = e.inputBuffer.getChannelData(0);
    chunks.push(new Float32Array(channelData));
  };

  source.connect(processor);
  processor.connect(audioContext.destination);

  // Wait for specified duration
  await new Promise((resolve) => setTimeout(resolve, durationMs));

  // Clean up
  source.disconnect();
  processor.disconnect();
  audioContext.close();

  // Combine chunks into single array
  const totalLength = chunks.reduce((len, chunk) => len + chunk.length, 0);
  const combined = new Float32Array(totalLength);
  let offset = 0;
  for (const chunk of chunks) {
    combined.set(chunk, offset);
    offset += chunk.length;
  }

  return combined;
}

/**
 * Convert PCM float32 array to WAV format (bytes) with proper WAV header.
 * @param {Float32Array} pcmData - PCM audio data
 * @param {number} sampleRate - Sample rate in Hz (default 16000)
 * @returns {Uint8Array} WAV file bytes
 */
function pcmToWavBytes(pcmData, sampleRate = 16000) {
  const numChannels = 1;
  const bitsPerSample = 16;
  const blockAlign = (numChannels * bitsPerSample) / 8;
  const byteRate = sampleRate * blockAlign;

  // Convert float32 to int16
  const int16Data = new Int16Array(pcmData.length);
  for (let i = 0; i < pcmData.length; i++) {
    const sample = Math.max(-1, Math.min(1, pcmData[i]));
    int16Data[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
  }

  // Build WAV file
  const wavLength = 36 + numChannels * sampleRate * 2;
  const wavBuffer = new ArrayBuffer(44 + int16Data.byteLength);
  const view = new DataView(wavBuffer);

  // Helper to write string to ArrayBuffer
  const writeString = (offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  // RIFF header
  writeString(0, "RIFF");
  view.setUint32(4, wavLength, true);
  writeString(8, "WAVE");

  // fmt subchunk
  writeString(12, "fmt ");
  view.setUint32(16, 16, true); // subchunk1 size
  view.setUint16(20, 1, true); // PCM format
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitsPerSample, true);

  // data subchunk
  writeString(36, "data");
  view.setUint32(40, int16Data.byteLength, true);

  // Copy PCM data
  const uint8 = new Uint8Array(wavBuffer);
  uint8.set(new Uint8Array(int16Data.buffer), 44);

  return uint8;
}

/**
 * Encode WAV bytes to base64 string.
 * @param {Uint8Array} wavBytes - WAV file bytes
 * @returns {string} Base64-encoded WAV data
 */
function wavBytesToBase64(wavBytes) {
  let binary = "";
  for (let i = 0; i < wavBytes.byteLength; i++) {
    binary += String.fromCharCode(wavBytes[i]);
  }
  return btoa(binary);
}

// ============================================================================
// INTERACTION MODES
// ============================================================================

async function setInteractionMode(newMode) {
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

  // Request mic access for voice modes
  const voiceModes = [
    INTERACTION_MODES.DIRECT_VOICE,
    INTERACTION_MODES.SPACEBAR_HOLD,
    INTERACTION_MODES.AUTO_CONTINUOUS,
    INTERACTION_MODES.WAKE_WORD_TRIGGERED,
  ];

  if (voiceModes.includes(newMode)) {
    try {
      await requestMicrophoneAccess();
    } catch (err) {
      console.warn("Mic permission not granted; voice modes will not work");
      setStatus("error");
      return;
    }
  }

  // Start wake word or auto loop
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

// ============================================================================
// VOICE INTERACTIONS (Browser Audio Capture)
// ============================================================================

/**
 * Execute a voice turn with browser-captured audio.
 * Captures 6 seconds from microphone, sends to server for processing.
 */
async function runVoiceTurn() {
  if (state.recordingState !== RECORDING_STATES.IDLE) {
    console.warn("Already recording or processing");
    return;
  }

  try {
    setRecordingState(RECORDING_STATES.RECORDING);
    setStatus("busy");

    // Request mic permission first
    await requestMicrophoneAccess();

    // Capture 6 seconds of audio from browser microphone
    const pcmData = await captureAudioMs(6000);

    // Encode PCM to WAV
    const wavBytes = pcmToWavBytes(pcmData);

    // Encode WAV to base64
    const audioBase64 = wavBytesToBase64(wavBytes);

    // Send to new browser-audio endpoint
    const data = await api("/api/v1/voice/turn-with-audio", {
      method: "POST",
      body: JSON.stringify({
        session_id: state.sessionId,
        audio_base64: audioBase64,
        speak_reply: true,
      }),
    });

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
    const pcmData = await captureAudioMs(6000);
    const wavBytes = pcmToWavBytes(pcmData);
    const audioBase64 = wavBytesToBase64(wavBytes);

    const data = await api("/api/v1/voice/turn-with-audio", {
      method: "POST",
      body: JSON.stringify({
        session_id: state.sessionId,
        audio_base64: audioBase64,
        speak_reply: true,
      }),
    });

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

// ============================================================================
// EVENT LISTENERS
// ============================================================================

sendButton.addEventListener("click", sendTextMessage);
textInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendTextMessage();
  }
});

// Segmented Control Listeners (mode selection)
segments.forEach((btn) => {
  btn.addEventListener("click", async () => {
    const mode = btn.dataset.mode;
    if (mode && INTERACTION_MODES[mode]) {
      await setInteractionMode(INTERACTION_MODES[mode]);
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
