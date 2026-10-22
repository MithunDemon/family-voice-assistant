# Family Voice Assistant - Video Demo Script & Recording Guide

A comprehensive 2:30 voiceover script and step-by-step recording checklist for presenting the **Family Voice Assistant (Alexa+ Simulated Experience)**.

---

## 🎬 Quick Recording Checklist (Reset, Run, Record, Upload)

1. **Reset**:
   - Ensure the server is running (`python -m uvicorn main:app --host 127.0.0.1 --port 8000`).
   - Open Chrome at `http://127.0.0.1:8000`.
   - Click the **"🔄 Reset demo"** button (or trigger `POST /api/reset`) to start with pristine seed data:
     - Groceries: `Apples (1 bag)`, `Almond milk (1 carton)`
     - Reminders: `Dad: Take out recycling (Tonight 8pm)`, `Mia: Piano practice (Today 5pm)`
     - Events: `Soccer match (Tomorrow 10:00 AM)`, `Family dinner (Sunday 6:30 PM)`
2. **Run**:
   - Make sure your screen recording software (OBS, Loom, or Windows Game Bar `Win + G`) is capturing the browser window and system audio (so the assistant's speech synthesis voice is recorded).
   - Click **"▶ Run auto demo"**. The system will autonomously run through each step, speak the responses, articulate the avatar's mouth, display tool chips, and update the Live Family State dashboard.
3. **Record**:
   - Read along with the timestamped voiceover script below, or let the assistant speak while you provide narration.
4. **Upload**:
   - Export your video in MP4/WebM format and upload to your submission platform along with `static/thumbnail.jpg`.

---

## 🎙️ 2:30 Timestamped Voiceover Script

| Timestamp | Screen Action / Visual | Spoken Voiceover Narration |
| :--- | :--- | :--- |
| **0:00 - 0:15** | Screen shows the dark glassmorphic dashboard with the 3D talking avatar idling. Click **"▶ Run auto demo"**. | *"Welcome to the Family Voice Assistant, an Alexa+ simulated experience designed to help busy households seamlessly coordinate groceries, reminders, and schedules."* |
| **0:15 - 0:30** | Step 1: Character greets: *"Hi! I'm your family assistant. What would you like to add to the list today?"* Avatar mouth opens and speaks. | *"Our interface features a procedural 3D talking character built in Three.js with natural breathing, blinking, and speech-synchronized lip movement with zero heavy external model downloads."* |
| **0:30 - 0:50** | Step 2: User prompt appears: *"Add milk and eggs to the grocery list"*. Tool chips `⚡ add_grocery_item(Milk)` and `⚡ add_grocery_item(Eggs)` fire. Right panel updates with capitalized items. | *"Watch what happens when we ask it to add multiple items at once: 'Add milk and eggs to the grocery list'. The assistant intelligently parses both items and dispatches separate tool calls to update the shared grocery board in real-time."* |
| **0:50 - 1:10** | Step 3: User prompt: *"What's on the list?"*. Assistant tool `⚡ list_groceries()` triggers and assistant replies with counts and items. | *"Any family member can check what is currently needed. Asking 'What's on the list?' triggers list inspection, returning a concise, spoken summary tailored for hands-free listening in the kitchen."* |
| **1:10 - 1:35** | Step 4: User prompt: *"Remind Mom to call the doctor at 4pm"*. Tool `⚡ add_reminder(Mom, call the doctor, at 4pm)` fires. Reminders panel updates. | *"Next, let's keep family tasks on track: 'Remind Mom to call the doctor at 4pm'. The assistant extracts the target family member, the task, and the due time, adding it to the live reminders panel without duplicates."* |
| **1:35 - 1:55** | Step 5: User prompt: *"What's on the calendar tomorrow?"*. Tool `⚡ list_events(tomorrow)` executes and assistant speaks schedule. | *"For household coordination, the calendar integration answers schedule queries. Asking 'What's on the calendar tomorrow?' instantly retrieves tomorrow's soccer match and times."* |
| **1:55 - 2:15** | Step 6: User prompt: *"Remove eggs from the list"*. Tool `⚡ remove_grocery_item(eggs)` executes. 'Eggs' disappears from the live grocery board. | *"Finally, crossing things off is just as effortless: 'Remove eggs from the list'. The assistant removes the item and immediately updates the live state."* |
| **2:15 - 2:30** | Demo banner shows completion. Camera zooms slightly on the avatar and live dashboard. | *"With clean tool calling, pluggable LLM support including Amazon Bedrock Converse API, and an expressive 3D voice avatar, the Family Voice Assistant makes household coordination natural and delighting. Thanks for watching!"* |

---

## 🛠️ Architecture Highlights for Submission Writeup

- **3D Procedural Talking Character**: Three.js avatar with dynamic mouth viseme modulation, eye tracking, eyelid blinks, and fallback to the Alexa glowing ring.
- **Deduplication & Capitalization**: Automatic first-letter capitalization and in-place updates for identical reminders or grocery items.
- **Autonomous Demo Runner**: Single-click demo orchestration with pause management, speech completion awaiting, and emergency cancel support.
