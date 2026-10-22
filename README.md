# Family Voice Assistant (Alexa+ Simulated Experience)

An interactive, simulated **Alexa+** voice assistant web application designed for family organization, built for the **Amazon Developer Hackathon (Alexa+ track, simulated-experience path)**.

Families can speak or type to a smart assistant that understands natural household requests and invokes specialized tools to manage:
1. **Shared Grocery List**: Add multiple items at once, remove items, and query what's currently needed.
2. **Family Reminders**: Set time-sensitive reminders for specific family members (e.g., Mom, Dad, Mia, Everyone).
3. **Shared Family Calendar**: Schedule and query appointments, matches, and family events.

---

## ✨ Features

- **3D Procedural Talking Character**: Built entirely in Three.js (no external 3D asset downloads required, bundled locally for offline use). Animates head tilt when listening, thinking eye shifts, random natural blinking, and speech-synchronized mouth visemes/phonemes with browser SpeechSynthesis. Includes a fallback to the glowing Alexa ring for older devices.
- **Voice-First Experience**: Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) for hands-free speech input, and `speechSynthesis` for spoken-style audio feedback.
- **Pluggable LLM Architecture**:
  - `mock`: Instant rule-based semantic parser that reliably handles demo phrases and natural language without external API keys or cost.
  - `bedrock`: Amazon Bedrock Converse API with native tool-use support (`boto3`) and automatic fail-safe fallback.
- **Live Family State Dashboard**: Real-time side panel reflecting the exact state of groceries, reminders, and calendar appointments.
- **Transparent Tool Calling**: Visual execution chips in the chat transcript indicating which tools were triggered (e.g. `⚡ add_grocery_item(milk)`).
- **Multi-Item Command Handling**: Say *"Add milk and eggs to the grocery list"* and watch the assistant dispatch separate tool calls for each item!

---

## 🎭 3D Talking Character

The web client features an interactive procedural 3D assistant character rendered with Three.js:
- **Zero External Model Dependencies**: Procedurally generated head, expressive eyes with eyelids, eyebrows, and a dynamic mouth geometry that morphs during speech.
- **Interactive State Transitions**:
  - `idle`: Gentle breathing oscillation, natural blinking (every 2-5s), and subtle head sway.
  - `listening`: Head tilts inquisitively, eyes widen and look attentively toward the user.
  - `thinking`: Eyes look upward and to the side during backend tool execution.
  - `speaking`: Mouth opens and closes smoothly with slight randomized phoneme modulation tied to `speechSynthesis.onboundary` and `onstart`. Closes completely on speech conclusion.
- **Autoplay Speech Compatibility**: Includes a **"✨ Start Voice Assistant"** button that unlocks browser audio policies and triggers a friendly spoken greeting.
- **Offline / Local Vendor**: Three.js is bundled directly under `static/vendor/three.module.js` (no CDN network requests required).
- **Graceful Fallback**: Automatically falls back to the glowing 2D Alexa Orb if WebGL is unavailable.

---

## 🏗️ Architecture

```
                       ┌────────────────────────────────────────┐
                       │          Browser Frontend              │
                       │  - Alexa Glow Ring Orb                 │
                       │  - Web Speech API (STT & TTS)          │
                       │  - Live Dashboard (Groceries/Reminders)│
                       └──────────────────┬─────────────────────┘
                                          │  HTTP POST /api/chat
                                          ▼
                       ┌────────────────────────────────────────┐
                       │            FastAPI Server              │
                       │             (main.py)                  │
                       └──────────────────┬─────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     ┌────────────────────────┐                     ┌────────────────────────┐
     │  Mock Engine (llm.py)  │                     │  Bedrock Converse API  │
     │  (Default / Zero Keys) │                     │ (Claude 3 Haiku/Sonnet)│
     └────────────┬───────────┘                     └────────────┬───────────┘
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          │ Tool Invocations
                                          ▼
                       ┌────────────────────────────────────────┐
                       │          Tools Layer (tools.py)        │
                       │  - add/remove/list_groceries           │
                       │  - add/list_reminders                  │
                       │  - add/list_events                     │
                       └──────────────────┬─────────────────────┘
                                          │
                                          ▼
                       ┌────────────────────────────────────────┐
                       │        Storage (storage.py)            │
                       │   In-memory + data/family_store.json   │
                       └────────────────────────────────────────┘
```

---

## 🚀 Setup & Run

### 1. Prerequisites
- Python 3.11+
- Modern Web Browser (Google Chrome, Edge, or Safari for Web Speech API support)

### 2. Windows Setup (PowerShell / Command Prompt)

1. Open PowerShell in the project directory:
   ```powershell
   cd c:\Users\user\.gemini\antigravity-ide\scratch\family-voice-assistant
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install required packages:
   ```powershell
   python -m pip install -r requirements.txt
   ```

---

## 🏃 Running the Application on Windows

### Option A: Zero-Configuration Mock Mode (Default)

No AWS keys or cloud connectivity needed. Ideal for quick testing and local demos.

1. Ensure `.env` is set to `LLM_PROVIDER=mock`:
   ```powershell
   Copy-Item .env.example .env
   ```
   *(`LLM_PROVIDER=mock` is the default in `.env.example`)*

2. Start the FastAPI server:
   ```powershell
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

3. Open your browser:
   ```text
   http://127.0.0.1:8000
   ```

---

### Option B: Amazon Bedrock Provider with Safe Fallback

1. In `.env`, set:
   ```ini
   LLM_PROVIDER=bedrock
   AWS_REGION=us-east-1
   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   ```
   *(Or authenticate via standard AWS CLI: `aws configure`)*

2. Start the server:
   ```powershell
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **Safe Failover Behavior**: If AWS credentials are missing or Bedrock returns any error, the assistant catches the exception, prepends a short notification in the chat, and immediately falls back to the `mock` engine so requests never crash. The top-right provider badge dynamically updates to reflect whichever provider is actively answering (`mock` or `bedrock`).

---

## 🎬 Demo Script (Step-by-Step)

Try these exact phrases by clicking the microphone or typing into the input bar (or clicking the convenient quick-prompt chips above the input):

| Step | Voice / Text Command | Expected Assistant Action |
|:---|:---|:---|
| **1** | *"Add milk and eggs to the grocery list"* | Assistant dispatches two tool calls: `add_grocery_item(milk)` & `add_grocery_item(eggs)`. Groceries card updates in real time. |
| **2** | *"What's on the list?"* | Calls `list_groceries()` and speaks back the current grocery list contents. |
| **3** | *"Remind Mom to call the doctor at 4pm"* | Calls `add_reminder(for_person="Mom", text="call the doctor", due_time="at 4pm")`. Reminders card updates immediately. |
| **4** | *"What's on the calendar tomorrow?"* | Calls `list_events(date="tomorrow")` and recites scheduled appointments. |
| **5** | *"Remove eggs from the list"* | Calls `remove_grocery_item(eggs)`. Eggs are removed from the live grocery card. |

---

## 🛠️ Project Structure

```
family-voice-assistant/
├── .env.example              # Environment variables template
├── .gitignore                # Git exclusions
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation & demo guide
├── FRICTION_LOG.md           # Developer friction log for hackathon insights
├── main.py                   # FastAPI server & endpoints (/api/chat, /api/state)
├── storage.py                # In-memory store with JSON persistence
├── tools.py                  # Python tool functions & Bedrock Converse schema
├── llm.py                    # Pluggable LLM interface (Mock engine + Bedrock)
├── data/
│   └── family_store.json     # Saved family state
└── static/
    ├── index.html            # Web UI layout & Alexa Orb
    ├── style.css             # Glassmorphism & pulsing ring animations
    └── app.js                # Web Speech STT/TTS & state synchronization
```

---

## 📄 License
MIT License.
