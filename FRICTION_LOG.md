# Friction Log: Family Voice Assistant

This log tracks hurdles, edge cases, and SDK nuances encountered during development for the Amazon Developer Hackathon, along with our workarounds and suggestions.

---

### Entry 1: Tool Use Multi-Item Splitting in Spoken Prompts
- **Task**: User says *"Add milk and eggs to the grocery list"*, expecting both items to be recorded on the shared list.
- **Expected vs. Actual**:
  - *Expected*: A model or intent parser identifies compound items and performs discrete item insertions.
  - *Actual*: Naive text extraction or generic single-argument tool calls often treat `"milk and eggs"` as a single combined string item.
- **Workaround**: Implemented conjunction-aware parsing in both the mock engine (`_split_grocery_items`) and Bedrock system prompt instructions (`"If multiple items are added (e.g. 'milk and eggs'), make separate tool calls for each item."`). The frontend dynamically creates a dedicated tool chip for every tool execution received.
- **Suggestion**: In assistant frameworks, encourage tool specifications to support batch array parameters (e.g., `items: string[]`) or provide helper middleware that decomposes compound noun phrases before calling atomic endpoints.

---

### Entry 2: Bedrock Converse API Tool Schema Formatting
- **Task**: Defining tool schemas for Amazon Bedrock's Converse API.
- **Expected vs. Actual**:
  - *Expected*: Direct JSON Schema dictionary under `parameters` (as common in OpenAI/Anthropic SDKs).
  - *Actual*: Bedrock Converse expects `{ "toolSpec": { "name": "...", "description": "...", "inputSchema": { "json": { ... } } } }`.
- **Workaround**: Standardized all tool descriptions in `tools.py` under the explicit `inputSchema.json` envelope structure required by `boto3` Bedrock Runtime.
- **Suggestion**: Provide an official SDK Pydantic serializer or Python decorator in `boto3` that automatically translates Python type hints to Bedrock Converse tool specs.

---

### Entry 3: Browser Web Speech API & HTTPS Permissions
- **Task**: Running speech-to-text (`SpeechRecognition`) and text-to-speech (`speechSynthesis`) on local test setups.
- **Expected vs. Actual**:
  - *Expected*: Speech recognition works immediately in all environments.
  - *Actual*: Browsers (especially Chromium) restrict `SpeechRecognition` to `localhost` or HTTPS origins. In non-supported browsers or insecure hostnames, the API throws errors or fails silently.
  - *Workaround*: Built full fallback support: keyboard input, enter-to-submit, visual status cues, and interactive "demo prompt chips" so the assistant can be completely demonstrated and tested even without mic permissions.
- **Suggestion**: Provide clear UI error states when audio permissions are blocked, and ensure all voice actions have one-click text equivalents.

---

### Entry 4: Browser Autoplay Policy & Speech Synthesis Initial Load
- **Task**: Having the assistant speak a welcome greeting or reply immediately upon page load without prior user interaction.
- **Expected vs. Actual**:
  - *Expected*: `window.speechSynthesis.speak()` immediately outputs audio upon DOM ready.
  - *Actual*: Modern browsers enforce strict autoplay policies that block unprompted audio synthesis until an explicit user gesture (click/tap) occurs on the document.
  - *Workaround*: Added an explicit, stylish **"✨ Start Voice Assistant"** interaction button in the UI. When clicked, it unlocks browser audio, mounts the 3D character context, and speaks the initial conversational greeting naturally.
  - *Suggestion*: Always gate initial voice greetings behind an explicit user gesture and maintain visual transcripts in parallel so information is never lost if audio is suppressed.
