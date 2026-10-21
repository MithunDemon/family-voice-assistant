// State & Configuration
let chatHistory = [];
let ttsEnabled = true;
let isRecognizing = false;
let recognition = null;

// DOM Elements
const alexaRing = document.getElementById("alexaRing");
const orbStatusIcon = document.getElementById("orbStatusIcon");
const statusText = document.getElementById("statusText");
const chatHistoryEl = document.getElementById("chatHistory");
const userInput = document.getElementById("userInput");
const chatForm = document.getElementById("chatForm");
const micBtn = document.getElementById("micBtn");
const toggleTtsBtn = document.getElementById("toggleTtsBtn");
const ttsIcon = document.getElementById("ttsIcon");
const clearChatBtn = document.getElementById("clearChatBtn");
const providerBadge = document.getElementById("providerBadge");
const providerText = document.getElementById("providerText");
const lastUpdated = document.getElementById("lastUpdated");

// Live Dashboard Elements
const groceryListEl = document.getElementById("groceryList");
const groceryCountEl = document.getElementById("groceryCount");
const reminderListEl = document.getElementById("reminderList");
const reminderCountEl = document.getElementById("reminderCount");
const calendarListEl = document.getElementById("calendarList");
const calendarCountEl = document.getElementById("calendarCount");

// Initialize Web Speech API for STT
function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn("Web Speech API not supported in this browser.");
    return null;
  }

  const rec = new SpeechRecognition();
  rec.continuous = false;
  rec.interimResults = false;
  rec.lang = "en-US";

  rec.onstart = () => {
    isRecognizing = true;
    micBtn.classList.add("recording");
    setOrbState("listening", "Listening to your request...");
  };

  rec.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    if (transcript) {
      userInput.value = transcript;
      handleSendMessage(transcript);
    }
  };

  rec.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    isRecognizing = false;
    micBtn.classList.remove("recording");
    setOrbState("idle", "Tap microphone or type below");
  };

  rec.onend = () => {
    isRecognizing = false;
    micBtn.classList.remove("recording");
    if (!alexaRing.classList.contains("speaking")) {
      setOrbState("idle", "Tap microphone or type below");
    }
  };

  return rec;
}

recognition = initSpeechRecognition();

// Set Ring Orb state & status text
function setOrbState(state, message) {
  alexaRing.className = `alexa-ring ${state}`;
  if (message) statusText.innerHTML = message;

  if (state === "listening") {
    orbStatusIcon.textContent = "👂";
  } else if (state === "speaking") {
    orbStatusIcon.textContent = "🔊";
  } else {
    orbStatusIcon.textContent = "🎙️";
  }
}

// Text-to-speech (TTS)
function speakReply(text) {
  if (!ttsEnabled || !("speechSynthesis" in window)) {
    setOrbState("idle", "Ready &bull; Tap microphone or type below");
    return;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  utterance.pitch = 1.05;

  utterance.onstart = () => {
    setOrbState("speaking", "Speaking response...");
  };

  utterance.onend = () => {
    setOrbState("idle", "Ready &bull; Tap microphone or type below");
  };

  utterance.onerror = () => {
    setOrbState("idle", "Ready &bull; Tap microphone or type below");
  };

  window.speechSynthesis.speak(utterance);
}

// Append Chat Bubble to Transcript
function appendMessage(role, text, tools = []) {
  const row = document.createElement("div");
  row.className = `chat-row ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  row.appendChild(bubble);

  // If tools were called, show a chip for each
  if (tools && tools.length > 0) {
    const chipsContainer = document.createElement("div");
    chipsContainer.className = "tool-chips-container";

    tools.forEach((t) => {
      const chip = document.createElement("span");
      chip.className = "tool-chip";
      const argStr = t.args ? Object.values(t.args).filter(Boolean).join(", ") : "";
      chip.textContent = `⚡ ${t.tool}(${argStr})`;
      chipsContainer.appendChild(chip);
    });

    row.appendChild(chipsContainer);
  }

  chatHistoryEl.appendChild(row);
  chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;

  chatHistory.push({ role, content: text });
}

// Send user query to backend
async function handleSendMessage(messageText) {
  const msg = (messageText || userInput.value).trim();
  if (!msg) return;

  userInput.value = "";
  appendMessage("user", msg);
  setOrbState("listening", "Processing with Alexa+ engine...");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: msg,
        history: chatHistory.slice(-6)
      })
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const data = await response.json();

    // Update Provider Badge
    if (data.provider) {
      updateProviderBadge(data.provider);
    }

    // Append Assistant response and tool chips
    appendMessage("assistant", data.response, data.tools_called);

    // Speak aloud
    speakReply(data.response);

    // Refresh Dashboard State
    if (data.state) {
      renderState(data.state);
    }
  } catch (err) {
    console.error("Chat error:", err);
    appendMessage("assistant", "Sorry, I had trouble processing that request.");
    setOrbState("idle", "Error connecting to service");
  }
}

// Update Provider Badge
function updateProviderBadge(provider) {
  providerBadge.className = `provider-badge ${provider}`;
  providerText.textContent = `Provider: ${provider}`;
}

// Render Dashboard State
function renderState(state) {
  if (!state) return;

  // 1. Groceries
  const groceries = state.groceries || [];
  groceryCountEl.textContent = groceries.length;
  if (groceries.length === 0) {
    groceryListEl.innerHTML = '<div class="empty-state">No items</div>';
  } else {
    groceryListEl.innerHTML = groceries
      .map(
        (g) => `
      <div class="list-item">
        <span class="main-text">${escapeHtml(g.item)}</span>
        <span class="sub-text">${escapeHtml(g.quantity || '1')}</span>
      </div>`
      )
      .join("");
  }

  // 2. Reminders
  const reminders = state.reminders || [];
  reminderCountEl.textContent = reminders.length;
  if (reminders.length === 0) {
    reminderListEl.innerHTML = '<div class="empty-state">No reminders</div>';
  } else {
    reminderListEl.innerHTML = reminders
      .map(
        (r) => `
      <div class="list-item">
        <span class="main-text">${escapeHtml(r.for_person)}: ${escapeHtml(r.text)}</span>
        <span class="sub-text">${escapeHtml(r.due_time || 'soon')}</span>
      </div>`
      )
      .join("");
  }

  // 3. Events
  const events = state.events || [];
  calendarCountEl.textContent = events.length;
  if (events.length === 0) {
    calendarListEl.innerHTML = '<div class="empty-state">No events scheduled</div>';
  } else {
    calendarListEl.innerHTML = events
      .map(
        (e) => `
      <div class="list-item">
        <span class="main-text">${escapeHtml(e.title)}</span>
        <span class="sub-text">${escapeHtml(e.date)} &bull; ${escapeHtml(e.time)}</span>
      </div>`
      )
      .join("");
  }

  const now = new Date();
  lastUpdated.textContent = `Updated ${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`;
}

// Initial State fetch on page load
async function loadInitialState() {
  try {
    const res = await fetch("/api/state");
    if (res.ok) {
      const data = await res.json();
      if (data.provider) updateProviderBadge(data.provider);
      if (data.state) renderState(data.state);
    }
  } catch (err) {
    console.warn("Could not load initial state:", err);
  }

  // Greet user
  appendMessage("assistant", "Hi there! I'm your family voice assistant. What can I do for you?");
}

// Escape helper for HTML rendering safety
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Event Listeners
chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  handleSendMessage();
});

micBtn.addEventListener("click", () => {
  if (!recognition) {
    alert("Speech recognition isn't supported in this browser. You can type queries in the box below!");
    return;
  }
  if (isRecognizing) {
    recognition.stop();
  } else {
    try {
      recognition.start();
    } catch (e) {
      console.warn("Recognition restart error", e);
    }
  }
});

toggleTtsBtn.addEventListener("click", () => {
  ttsEnabled = !ttsEnabled;
  if (ttsEnabled) {
    toggleTtsBtn.classList.add("active");
    ttsIcon.textContent = "🔊";
  } else {
    toggleTtsBtn.classList.remove("active");
    ttsIcon.textContent = "🔇";
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  }
});

clearChatBtn.addEventListener("click", () => {
  chatHistoryEl.innerHTML = "";
  chatHistory = [];
  appendMessage("assistant", "Chat cleared. What can I help with next?");
});

// Demo prompt chips click
document.querySelectorAll(".chip-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const prompt = btn.getAttribute("data-prompt");
    if (prompt) {
      userInput.value = prompt;
      handleSendMessage(prompt);
    }
  });
});

// Boot
loadInitialState();
