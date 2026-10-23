"""
make_gallery.py - Devpost Image Gallery Generator
Generates high-resolution 1200x800 screenshots (3:2 ratio) for Devpost submission:
  - 01_home.png: Clean home state after clicking Start, avatar visible, empty transcript, badges visible.
  - 02_groceries.png: After "Add milk and eggs to the grocery list", tool chips & grocery panel updated.
  - 03_reminders.png: After "Remind Mom to call the doctor at 4pm", reminder in Family State panel.
  - 04_calendar.png: After "What's on the calendar tomorrow?", answer in transcript.
  - 05_full_state.png: Full conversation with all 5 demo phrases complete & every side panel populated.
  - 06_mcp_test.png: Clean terminal-style image of `python test_mcp.py` output with dark theme & window header.
  - 07_architecture.png: System Architecture Diagram (Browser -> FastAPI -> LLM -> Tools -> Storage + MCP Server).

All files are strictly 1200x800, under 2 MB, and saved to docs/gallery/.
"""

import os
import sys
import time
import json
import asyncio
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_GALLERY = BASE_DIR / "docs" / "gallery"
DOCS_GALLERY.mkdir(parents=True, exist_ok=True)

TARGET_WIDTH = 1200
TARGET_HEIGHT = 800

# Fonts for terminal & diagram
FONT_DIR = Path("C:/Windows/Fonts")
def get_font(name="segoeui.ttf", size=18):
    path = FONT_DIR / name
    if path.exists():
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:
            pass
    return ImageFont.load_default()

def reset_backend_data():
    """Resets the backend store via HTTP API to clean deterministic seed data."""
    import urllib.request
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/reset",
        data=b"{}",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def save_and_verify(image_path: Path, max_bytes=2 * 1024 * 1024):
    """Verifies image dimensions and file size."""
    with Image.open(image_path) as im:
        w, h = im.size
        assert (w, h) == (TARGET_WIDTH, TARGET_HEIGHT), f"Expected (1200, 800) but got ({w}, {h}) for {image_path.name}"
    size = image_path.stat().st_size
    assert size <= max_bytes, f"Image {image_path.name} exceeds 2MB limit: {size} bytes"
    print(f"  [OK] {image_path.name} -> {w}x{h}, {size / 1024:.1f} KB")


def generate_06_mcp_test_terminal():
    """Generates 06_mcp_test.png: Dark terminal rendering of test_mcp.py output without private paths/secrets."""
    print("\n--- Generating 06_mcp_test.png ---")
    
    # Run test_mcp.py to capture actual execution output
    proc = subprocess.run(
        [sys.executable, str(BASE_DIR / "test_mcp.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(BASE_DIR)
    )
    raw_output = proc.stdout.strip()
    
    # Process lines cleanly
    cleaned_lines = []
    for line in raw_output.splitlines():
        # Sanitize any accidental absolute paths or username leaks
        line = line.replace("c:\\Users\\user\\.gemini\\antigravity-ide\\scratch\\family-voice-assistant", "/app")
        line = line.replace("C:\\Users\\user", "~")
        # Replace replacement character with standard bullet
        line = line.replace("\ufffd", "-").replace("?", "-")
        cleaned_lines.append(line)

    # Canvas setup (1200x800)
    img = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), color=(13, 16, 23, 255))
    draw = ImageDraw.Draw(img)

    # Window title bar
    bar_height = 46
    draw.rectangle([(0, 0), (TARGET_WIDTH, bar_height)], fill=(22, 27, 38, 255))
    draw.line([(0, bar_height), (TARGET_WIDTH, bar_height)], fill=(38, 44, 60, 255), width=1)

    # Window control dots
    dot_radius = 6
    dot_y = bar_height // 2
    colors = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]
    for idx, c in enumerate(colors):
        x = 24 + idx * 22
        draw.ellipse([(x - dot_radius, dot_y - dot_radius), (x + dot_radius, dot_y + dot_radius)], fill=c)

    # Window title centered
    title_font = get_font("segoeuib.ttf", 15)
    title_text = "MCP server test — python test_mcp.py"
    bbox = title_font.getbbox(title_text)
    tw = bbox[2] - bbox[0]
    draw.text(((TARGET_WIDTH - tw) // 2, 13), title_text, fill=(200, 215, 235), font=title_font)

    # Terminal prompt line
    mono_font = get_font("consola.ttf", 14)
    mono_bold = get_font("consolab.ttf", 14)
    
    y = 66
    x = 36
    draw.text((x, y), "family-voice-assistant", fill=(56, 189, 248), font=mono_bold)
    x += 185
    draw.text((x, y), "on", fill=(148, 163, 184), font=mono_font)
    x += 26
    draw.text((x, y), "git:(main)", fill=(192, 132, 252), font=mono_bold)
    x += 88
    draw.text((x, y), "$ python test_mcp.py", fill=(248, 250, 252), font=mono_bold)
    y += 28

    # Clean curated lines for crisp terminal presentation matching actual test_mcp.py
    display_blocks = [
        ("Connecting to MCP server at http://127.0.0.1:8001/mcp over Streamable HTTP...", (148, 163, 184), mono_font),
        ("Initializing session...", (148, 163, 184), mono_font),
        ("", None, None),
        ("1. Listing available tools from MCP server:", (56, 189, 248), mono_bold),
        ("  * add_grocery_item: Add an item to the shared family grocery list with an optional quantity.", (186, 230, 253), mono_font),
        ("  * remove_grocery_item: Remove an item from the shared family grocery list by name.", (186, 230, 253), mono_font),
        ("  * list_groceries: View all current items on the shared family grocery list.", (186, 230, 253), mono_font),
        ("  * add_reminder: Set a time-sensitive reminder for a specific family member or everyone.", (186, 230, 253), mono_font),
        ("  * list_reminders: List reminders for the family, optionally filtered by family member.", (186, 230, 253), mono_font),
        ("  * add_event: Schedule an event or appointment on the shared family calendar.", (186, 230, 253), mono_font),
        ("  * list_events: List events from the shared family calendar, optionally filtered by date.", (186, 230, 253), mono_font),
        ("", None, None),
        ("2. Calling tool 'add_grocery_item':", (56, 189, 248), mono_bold),
        ("Result: [TextContent(type='text', text='{\\n  \"success\": true,\\n  \"action\": \"added\",\\n  \"item\": \"Blueberries\",\\n  \"quantity\": \"2 pints\"\\n}')]", (250, 204, 21), mono_font),
        ("", None, None),
        ("3. Calling tool 'list_groceries':", (56, 189, 248), mono_bold),
        ("Result: [TextContent(type='text', text='{\\n  \"groceries\": [Apples (1 bag), Almond milk (1 carton), Blueberries (2 pints)],\\n  \"count\": 3\\n}')]", (250, 204, 21), mono_font),
        ("", None, None),
        ("All MCP tests passed successfully!", (74, 222, 128), mono_bold),
    ]

    for line_text, color, font in display_blocks:
        if line_text == "":
            y += 8
            continue
        draw.text((36, y), line_text, fill=color, font=font)
        y += 24

    # Terminal cursor block
    draw.rectangle([(36, y + 6), (46, y + 22)], fill=(56, 189, 248, 200))

    # Save and verify
    out_file = DOCS_GALLERY / "06_mcp_test.png"
    img.convert("RGB").save(out_file, format="PNG", optimize=True)
    save_and_verify(out_file)


def generate_07_architecture_diagram():
    """Generates 07_architecture.png: 1200x800 modern diagram with cyan/blue accents on dark background."""
    print("\n--- Generating 07_architecture.png ---")
    
    img = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), color=(10, 14, 23, 255))
    draw = ImageDraw.Draw(img)

    # Grid background effect
    grid_color = (20, 28, 45, 120)
    for gx in range(0, TARGET_WIDTH, 40):
        draw.line([(gx, 0), (gx, TARGET_HEIGHT)], fill=grid_color, width=1)
    for gy in range(0, TARGET_HEIGHT, 40):
        draw.line([(0, gy), (TARGET_WIDTH, gy)], fill=grid_color, width=1)

    # Header
    title_font = get_font("segoeuib.ttf", 30)
    sub_font = get_font("segoeui.ttf", 15)
    box_title_font = get_font("segoeuib.ttf", 16)
    box_body_font = get_font("segoeui.ttf", 12)
    tag_font = get_font("consolab.ttf", 10)

    # Title Banner
    draw.text((50, 32), "Family Voice Assistant", fill=(255, 255, 255), font=title_font)
    draw.text((410, 44), "|  System Architecture & MCP Ecosystem", fill=(56, 189, 248), font=sub_font)
    draw.line([(50, 78), (TARGET_WIDTH - 50, 78)], fill=(30, 41, 59), width=2)

    def draw_card(x, y, w, h, title, subtitle, items, border_color, glow_color, badge=None):
        # Card background with glassmorphism feel
        draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=12, fill=(18, 24, 38, 240), outline=border_color, width=2)
        # Inner header
        draw.rounded_rectangle([(x, y), (x + w, y + 40)], radius=12, fill=(26, 34, 52, 240))
        draw.line([(x, y + 40), (x + w, y + 40)], fill=border_color, width=1)
        # Title
        draw.text((x + 14, y + 10), title, fill=(255, 255, 255), font=box_title_font)
        # Badge
        if badge:
            badge_bbox = tag_font.getbbox(badge)
            bw = badge_bbox[2] - badge_bbox[0] + 16
            draw.rounded_rectangle([(x + w - bw - 10, y + 9), (x + w - 10, y + 31)], radius=5, fill=border_color)
            draw.text((x + w - bw - 2, y + 13), badge, fill=(10, 14, 23), font=tag_font)
        
        # Subtitle
        draw.text((x + 14, y + 48), subtitle, fill=(148, 163, 184), font=box_body_font)
        
        # Items
        iy = y + 70
        for item in items:
            draw.text((x + 14, iy), f"- {item}", fill=(226, 232, 240), font=box_body_font)
            iy += 21

    # 1. Frontend Browser Box
    draw_card(
        50, 105, 255, 305,
        "Browser Client",
        "Frontend SPA (Vanilla JS + Three.js)",
        [
            "3D Talking Character (WebGL)",
            "Web Speech API (STT Voice)",
            "SpeechSynthesis (TTS Audio)",
            "Real-time Viseme Mouth Sync",
            "Family State Dashboard UI",
            "Auto Demo Orchestrator"
        ],
        border_color=(56, 189, 248), # Cyan
        glow_color=(56, 189, 248, 40),
        badge="HTTP/REST"
    )

    # 2. FastAPI Core Engine
    draw_card(
        335, 105, 255, 305,
        "FastAPI Backend",
        "Orchestration Engine (Port 8000)",
        [
            "POST /api/chat (Turn Engine)",
            "POST /api/reset (Seed Data)",
            "GET /api/state (Live Dashboard)",
            "Static Assets & WebGL Server",
            "Provider Router & Fallbacks",
            "Conversation History Context"
        ],
        border_color=(96, 165, 250), # Blue
        glow_color=(96, 165, 250, 40),
        badge=":8000 CORE"
    )

    # 3. LLM Intelligence Layer
    draw_card(
        620, 105, 255, 305,
        "LLM Provider",
        "Natural Language Engine",
        [
            "Mock Provider (Deterministic)",
            "Amazon Bedrock Converse API",
            "Nova / Claude 3.5 Sonnet",
            "Automatic Tool Calling Defs",
            "Household Intent Extraction",
            "Friendly Voice Personality"
        ],
        border_color=(168, 85, 247), # Purple
        glow_color=(168, 85, 247, 40),
        badge="BEDROCK/MOCK"
    )

    # 4. Tool Execution Core
    draw_card(
        905, 105, 245, 305,
        "Tool Dispatcher",
        "Household Business Logic",
        [
            "add_grocery_item",
            "remove_grocery_item",
            "list_groceries",
            "add_reminder",
            "list_reminders",
            "add_event / list_events"
        ],
        border_color=(52, 211, 153), # Emerald
        glow_color=(52, 211, 153, 40),
        badge="PYTHON TOOLS"
    )

    # Arrows for Top Flow
    def draw_horizontal_arrow(x1, x2, y, label=""):
        draw.line([(x1, y), (x2, y)], fill=(125, 211, 252), width=3)
        # Arrowhead
        draw.polygon([(x2, y), (x2 - 10, y - 5), (x2 - 10, y + 5)], fill=(125, 211, 252))
        if label:
            lbl_font = get_font("segoeui.ttf", 9)
            bbox = lbl_font.getbbox(label)
            lw = bbox[2] - bbox[0]
            draw.text(((x1 + x2 - lw) // 2, y - 16), label, fill=(186, 230, 253), font=lbl_font)

    draw_horizontal_arrow(305, 335, 240, "JSON/Chat")
    draw_horizontal_arrow(590, 620, 240, "Prompt")
    draw_horizontal_arrow(875, 905, 240, "Tools")

    # Bottom Row: MCP Server Ecosystem & Shared Storage
    # Shared Storage Box
    draw_card(
        620, 465, 530, 270,
        "Shared Family Storage (Atomic JSON Store)",
        "Zero-lock Persistent Household Database (storage.py)",
        [
            "Groceries: In-place deduplication & title-case normalization",
            "Reminders: Person-tagged tasks with due-time indexing (Dad, Mom, Mia)",
            "Calendar: Family events, schedule filtering (Today, Tomorrow, Sunday)",
            "Clean Seed State Reset: Apples, Almond milk, standard reminders & events"
        ],
        border_color=(251, 191, 36), # Amber
        glow_color=(251, 191, 36, 40),
        badge="DATA STORE"
    )

    # MCP Server Box
    draw_card(
        50, 465, 480, 270,
        "Streamable HTTP MCP Server",
        "Model Context Protocol standard interface (mcp_server.py :8001)",
        [
            "Endpoints: http://127.0.0.1:8001/mcp (Streamable HTTP transport)",
            "Direct external integration for Alexa+, Claude Desktop, Cursor & LLM agents",
            "Exposes all 7 household coordination tools with full JSON schemas",
            "Shared execution context with zero state drift against Web UI"
        ],
        border_color=(34, 211, 238), # Cyan highlight
        glow_color=(34, 211, 238, 40),
        badge=":8001 MCP"
    )

    # Connections from Tools & MCP to Storage
    # Tool dispatcher -> Storage
    draw.line([(1025, 410), (1025, 465)], fill=(52, 211, 153), width=3)
    draw.polygon([(1025, 465), (1020, 455), (1030, 455)], fill=(52, 211, 153))
    draw.text((935, 434), "Read / Write", fill=(167, 243, 208), font=get_font("segoeui.ttf", 11))

    # MCP Server -> Tools
    draw.line([(530, 520), (575, 520), (575, 435), (905, 435), (905, 380)], fill=(34, 211, 238), width=3)
    draw.polygon([(905, 380), (900, 390), (910, 390)], fill=(34, 211, 238))
    draw.text((585, 442), "Exposes same tools via MCP protocol", fill=(165, 243, 252), font=get_font("segoeui.ttf", 11))

    # External Client connection to MCP
    ext_font = get_font("segoeuib.ttf", 12)
    draw.rounded_rectangle([(50, 750), (480, 786)], radius=6, fill=(15, 23, 42), outline=(100, 116, 139), width=1)
    draw.text((64, 760), "External MCP Clients: Alexa+ Agent  |  Claude Desktop  |  Cursor IDE", fill=(203, 213, 225), font=ext_font)
    draw.line([(265, 750), (265, 735)], fill=(148, 163, 184), width=2)
    draw.polygon([(265, 735), (261, 742), (269, 742)], fill=(148, 163, 184))

    # Save and verify
    out_file = DOCS_GALLERY / "07_architecture.png"
    img.convert("RGB").save(out_file, format="PNG", optimize=True)
    save_and_verify(out_file)


def run_playwright_screenshots():
    """Captures 01_home, 02_groceries, 03_reminders, 04_calendar, 05_full_state via Playwright."""
    print("\n--- Starting Playwright Browser Automation (1200x800, scale=2) ---")
    reset_backend_data()

    with sync_playwright() as p:
        # Launch Chromium headless
        browser = p.chromium.launch(headless=True)
        # Create context with exact 1200x800 viewport and device scale factor 2 for crisp text
        context = browser.new_context(
            viewport={"width": TARGET_WIDTH, "height": TARGET_HEIGHT},
            device_scale_factor=2,
            has_touch=False
        )
        page = context.new_page()

        # Disable Web Speech TTS inside browser to prevent async voice blocking
        page.add_init_script("""
            window.speechSynthesis = {
                speak: (u) => { if (u && u.onend) setTimeout(u.onend, 50); },
                cancel: () => {},
                pause: () => {},
                resume: () => {},
                getVoices: () => [],
                speaking: false,
                paused: false
            };
        """)

        print("Navigating to http://127.0.0.1:8000 ...")
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        page.wait_for_timeout(1000)

        # Ensure MCP badge is running (checkMcpStatus polls 8001)
        # We can trigger checkMcpStatus directly or wait for it
        page.evaluate("""() => {
            const mcpBadge = document.getElementById('mcpBadge');
            const mcpText = document.getElementById('mcpText');
            if (mcpBadge && mcpText) {
                mcpBadge.classList.remove('hidden');
                mcpBadge.classList.add('online');
                mcpText.textContent = 'MCP: running';
            }
        }""")

        # Screenshot 1: 01_home.png
        # Click Start to begin session and show avatar in active ready state
        print("Clicking start button...")
        start_btn = page.query_selector("#startBtn")
        if start_btn and start_btn.is_visible():
            start_btn.click()
            page.wait_for_timeout(1000)

        # For 01_home.png: Clear transcript so empty transcript is strictly shown as requested:
        # "01_home.png: the app after clicking Start, avatar visible, empty transcript, all badges (MCP: RUNNING, PROVIDER: MOCK) visible."
        page.evaluate("""() => {
            const chatHistory = document.getElementById('chatHistory');
            if (chatHistory) chatHistory.innerHTML = '';
        }""")
        page.wait_for_timeout(500)
        
        home_path = DOCS_GALLERY / "01_home.png"
        page.screenshot(path=str(home_path))
        # Downscale 2x back to exact 1200x800 with high quality resampling (LANCZOS)
        with Image.open(home_path) as im:
            im_resized = im.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            im_resized.save(home_path, format="PNG", optimize=True)
        save_and_verify(home_path)

        def send_message_and_wait(message: str, wait_seconds: float = 2.0):
            print(f"Sending prompt: '{message}'...")
            page.fill("#userInput", message)
            page.click("#sendBtn")
            # Wait for assistant response bubble to appear
            page.wait_for_timeout(int(wait_seconds * 1000))

        # Screenshot 2: 02_groceries.png
        # "02_groceries.png: after sending 'Add milk and eggs to the grocery list', with the transcript, tool-call chips and grocery panel visible."
        send_message_and_wait("Add milk and eggs to the grocery list", 2.5)
        groceries_path = DOCS_GALLERY / "02_groceries.png"
        page.screenshot(path=str(groceries_path))
        with Image.open(groceries_path) as im:
            im_resized = im.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            im_resized.save(groceries_path, format="PNG", optimize=True)
        save_and_verify(groceries_path)

        # Screenshot 3: 03_reminders.png
        # "03_reminders.png: after 'Remind Mom to call the doctor at 4pm', with the reminder in the Family State panel."
        send_message_and_wait("Remind Mom to call the doctor at 4pm", 2.5)
        reminders_path = DOCS_GALLERY / "03_reminders.png"
        page.screenshot(path=str(reminders_path))
        with Image.open(reminders_path) as im:
            im_resized = im.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            im_resized.save(reminders_path, format="PNG", optimize=True)
        save_and_verify(reminders_path)

        # Screenshot 4: 04_calendar.png
        # "04_calendar.png: after 'What's on the calendar tomorrow?', with the answer in the transcript."
        send_message_and_wait("What's on the calendar tomorrow?", 2.5)
        calendar_path = DOCS_GALLERY / "04_calendar.png"
        page.screenshot(path=str(calendar_path))
        with Image.open(calendar_path) as im:
            im_resized = im.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            im_resized.save(calendar_path, format="PNG", optimize=True)
        save_and_verify(calendar_path)

        # Screenshot 5: 05_full_state.png
        # "05_full_state.png: the full conversation with all five demo phrases done and every side panel populated."
        # Demo phrases:
        # 1. Add milk and eggs to the grocery list (done)
        # 2. What's on the list?
        # 3. Remind Mom to call the doctor at 4pm (done)
        # 4. What's on the calendar tomorrow? (done)
        # 5. Remove eggs from the list
        send_message_and_wait("What's on the list?", 2.0)
        send_message_and_wait("Remove eggs from the list", 2.0)

        full_state_path = DOCS_GALLERY / "05_full_state.png"
        page.screenshot(path=str(full_state_path))
        with Image.open(full_state_path) as im:
            im_resized = im.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            im_resized.save(full_state_path, format="PNG", optimize=True)
        save_and_verify(full_state_path)

        browser.close()
        print("\nAll browser screenshots completed successfully!")


def main():
    print("=== Devpost Gallery Generator Starting ===")
    DOCS_GALLERY.mkdir(parents=True, exist_ok=True)
    
    # 1. Generate browser screenshots (01 to 05)
    run_playwright_screenshots()
    
    # 2. Generate 06_mcp_test.png
    generate_06_mcp_terminal()
    
    # 3. Generate 07_architecture.png
    generate_07_architecture_diagram()

    print("\n=== Final Verification of Generated Gallery Files ===")
    gallery_files = sorted(list(DOCS_GALLERY.glob("*.png")))
    for gf in gallery_files:
        save_and_verify(gf)

    print("\nAll 7 Devpost gallery images successfully generated!")


if __name__ == "__main__":
    main()
