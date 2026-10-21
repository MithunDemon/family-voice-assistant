import os
import re
from typing import Dict, Any, List, Tuple
from tools import execute_tool, BEDROCK_TOOL_CONFIG

SYSTEM_PROMPT = """You are a helpful, warm, and natural family voice assistant modeled after Alexa+.
You help a family coordinate their shared grocery list, reminders, and calendar events.
Guidelines:
- Reply in short, conversational, spoken-style sentences (1 to 2 sentences max) optimized for text-to-speech.
- Always use the provided tools to fetch or mutate data when requested.
- If multiple items are added (e.g. "milk and eggs"), make separate tool calls for each item.
- Speak warmly and concisely as a family assistant.
"""


def _split_grocery_items(text: str) -> List[str]:
    """Splits conjunctions and commas to extract individual grocery items."""
    # Remove phrases like 'to the grocery list', 'to the list', 'to groceries'
    clean = re.sub(r'\b(to|on)\s+(the\s+)?(grocery\s+list|groceries|list)\b', '', text, flags=re.IGNORECASE)
    # Remove leading command words
    clean = re.sub(r'^(add|put|include|need|buy|get)\s+', '', clean.strip(), flags=re.IGNORECASE)
    
    # Split on commas, ' and ', ' & '
    parts = re.split(r'[,+]|\band\b|&', clean, flags=re.IGNORECASE)
    items = []
    for p in parts:
        item = p.strip()
        # Clean trailing/leading punctuation
        item = re.sub(r'^[^\w]+|[^\w]+$', '', item)
        if item and len(item) > 1 and item.lower() not in ["the", "some", "a", "an", "also", "please"]:
            items.append(item)
    return items


def run_mock_turn(message: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Robust rule & pattern matcher for the mock provider.
    Specifically guarantees handling the demo script phrases:
    - "Add milk and eggs to the grocery list"
    - "What's on the list?"
    - "Remind Mom to call the doctor at 4pm"
    - "What's on the calendar tomorrow?"
    - "Remove eggs from the list"
    Plus many natural variations.
    """
    msg = message.strip()
    msg_lower = msg.lower()
    tools_called = []
    
    # 1. REMOVE FROM GROCERY LIST
    if any(k in msg_lower for k in ["remove", "delete", "take off", "scratch off", "cross off"]):
        # e.g. "Remove eggs from the list"
        m = re.search(r'(?:remove|delete|take off|cross off)\s+(?:the\s+)?(.+?)(?:\s+from\s+(?:the\s+)?(?:grocery\s+list|list|groceries)|$)', msg_lower)
        if m:
            raw_target = m.group(1).strip()
            # Split in case user said "remove milk and eggs"
            items_to_remove = _split_grocery_items(raw_target)
            if not items_to_remove:
                items_to_remove = [raw_target]
            
            removed = []
            for item in items_to_remove:
                args = {"item": item}
                res = execute_tool("remove_grocery_item", args)
                tools_called.append({"tool": "remove_grocery_item", "args": args, "result": res})
                if res.get("success"):
                    removed.append(res.get("item", item))
            
            if removed:
                if len(removed) == 1:
                    return f"I've removed {removed[0]} from your grocery list.", tools_called
                else:
                    items_str = " and ".join(removed)
                    return f"I've removed {items_str} from your grocery list.", tools_called
            else:
                return f"I couldn't find {raw_target} on your grocery list.", tools_called

    # 2. ADD TO GROCERY LIST (Multiple items supported)
    if (any(k in msg_lower for k in ["grocery", "groceries"]) and any(k in msg_lower for k in ["add", "put", "buy", "need", "get"])) or \
       (re.match(r'^(add|put|need|buy)\s+', msg_lower) and ("list" in msg_lower or "to " in msg_lower or not any(x in msg_lower for x in ["event", "calendar", "meeting", "reminder", "remind"]))):
        
        items = _split_grocery_items(msg)
        if items:
            added = []
            for item in items:
                args = {"item": item, "quantity": "1"}
                res = execute_tool("add_grocery_item", args)
                tools_called.append({"tool": "add_grocery_item", "args": args, "result": res})
                added.append(item)
            
            if len(added) == 1:
                return f"I've added {added[0]} to your grocery list.", tools_called
            elif len(added) == 2:
                return f"I've added {added[0]} and {added[1]} to your grocery list.", tools_called
            else:
                items_str = ", ".join(added[:-1]) + f", and {added[-1]}"
                return f"I've added {items_str} to your grocery list.", tools_called

    # 3. LIST GROCERIES ("What's on the list?", "show groceries", etc.)
    if any(q in msg_lower for q in ["on the list", "on the grocery", "grocery list", "show groceries", "what groceries", "what do we need"]):
        res = execute_tool("list_groceries", {})
        tools_called.append({"tool": "list_groceries", "args": {}, "result": res})
        items = res.get("groceries", [])
        if not items:
            return "Your grocery list is currently empty.", tools_called
        
        item_names = [f"{g['item']}" for g in items]
        if len(item_names) <= 3:
            items_str = " and ".join(item_names)
            return f"You have {len(items)} items on your grocery list: {items_str}.", tools_called
        else:
            first_few = ", ".join(item_names[:3])
            return f"You have {len(items)} items on your list, including {first_few}, and others.", tools_called

    # 4. ADD REMINDER ("Remind Mom to call the doctor at 4pm")
    if "remind" in msg_lower:
        # Match pattern: remind [Person] to [Task] (at|on|for) [Time]
        m = re.search(r'remind\s+([a-zA-Z]+)\s+to\s+(.+?)(?:\s+(at|by|on|for|tomorrow|tonight)\s+(.+))?$', msg, re.IGNORECASE)
        if m:
            person = m.group(1).strip()
            task = m.group(2).strip()
            time_prep = m.group(3) or ""
            time_val = m.group(4) or ""
            due_time = f"{time_prep} {time_val}".strip() if (time_prep or time_val) else "soon"
            
            # Clean trailing punct
            task = task.rstrip('.?!')
            due_time = due_time.rstrip('.?!')

            args = {"for_person": person, "text": task, "due_time": due_time}
            res = execute_tool("add_reminder", args)
            tools_called.append({"tool": "add_reminder", "args": args, "result": res})
            return f"I've set a reminder for {person} to {task} {due_time}.", tools_called
        else:
            # Fallback simpler reminder
            args = {"for_person": "Everyone", "text": msg, "due_time": "soon"}
            res = execute_tool("add_reminder", args)
            tools_called.append({"tool": "add_reminder", "args": args, "result": res})
            return f"I've created that reminder for the family.", tools_called

    # 5. LIST REMINDERS
    if any(k in msg_lower for k in ["reminders", "what are my reminders", "any reminders"]):
        person = None
        for p in ["mom", "dad", "mia"]:
            if p in msg_lower:
                person = p.capitalize()
                break
        args = {"for_person": person} if person else {}
        res = execute_tool("list_reminders", args)
        tools_called.append({"tool": "list_reminders", "args": args, "result": res})
        rems = res.get("reminders", [])
        if not rems:
            return "There are no reminders scheduled right now.", tools_called
        top = rems[0]
        return f"You have {len(rems)} reminders. For example: {top['for_person']} to {top['text']} {top['due_time']}.", tools_called

    # 6. CALENDAR: WHAT'S ON THE CALENDAR ("What's on the calendar tomorrow?")
    if any(k in msg_lower for k in ["calendar", "schedule", "events"]):
        target_date = None
        if "tomorrow" in msg_lower:
            target_date = "tomorrow"
        elif "today" in msg_lower:
            target_date = "today"
        elif "sunday" in msg_lower:
            target_date = "sunday"
        
        args = {"date": target_date} if target_date else {}
        res = execute_tool("list_events", args)
        tools_called.append({"tool": "list_events", "args": args, "result": res})
        events = res.get("events", [])
        
        date_label = target_date if target_date else "the calendar"
        if not events:
            return f"There are no events scheduled for {date_label}.", tools_called
        
        event_descriptions = [f"{e['title']} at {e['time']}" for e in events]
        return f"On {date_label}, you have {', and '.join(event_descriptions)}.", tools_called

    # 7. ADD CALENDAR EVENT
    if any(k in msg_lower for k in ["add event", "schedule", "calendar"]):
        # Generic event addition
        args = {"title": msg, "date": "Tomorrow", "time": "All day"}
        res = execute_tool("add_event", args)
        tools_called.append({"tool": "add_event", "args": args, "result": res})
        return f"I've added that to your family calendar.", tools_called

    # Default greeting / conversational response
    if any(g in msg_lower for g in ["hello", "hi", "hey", "who are you"]):
        return "Hello! I'm your family voice assistant. How can I help with your groceries, reminders, or calendar today?", []

    return "I'm here to help. You can ask me to manage your grocery list, set reminders, or check the family calendar.", []


def run_bedrock_turn(message: str, history: List[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]], str]:
    """
    Executes a turn using AWS Bedrock Converse API with toolConfig.
    Falls back safely to mock if credentials, region, model access, or SDK errors occur,
    notifying the user in chat and reporting the actual provider used.
    """
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError

    model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    region = os.getenv("AWS_REGION", "us-east-1")

    # Safe check for AWS credentials presence if explicit keys aren't found in env or session
    try:
        session = boto3.Session(region_name=region)
        credentials = session.get_credentials()
        if not credentials:
            fallback_text, tools = run_mock_turn(message)
            notice = "[Notice: AWS credentials not found. Safely fell back to mock provider] "
            return notice + fallback_text, tools, "mock"

        client = session.client("bedrock-runtime")
    except Exception as e:
        fallback_text, tools = run_mock_turn(message)
        notice = f"[Notice: Bedrock init failed ({e}). Safely fell back to mock provider] "
        return notice + fallback_text, tools, "mock"

    # Prepare messages
    messages = []
    if history:
        for turn in history[-6:]:  # keep recent 6 turns for context
            role = "user" if turn.get("role") == "user" else "assistant"
            content = turn.get("content", "")
            if content:
                messages.append({"role": role, "content": [{"text": content}]})

    messages.append({"role": "user", "content": [{"text": message}]})

    tools_called = []
    max_loops = 5

    try:
        for _ in range(max_loops):
            response = client.converse(
                modelId=model_id,
                system=[{"text": SYSTEM_PROMPT}],
                messages=messages,
                toolConfig=BEDROCK_TOOL_CONFIG
            )

            output_message = response.get("output", {}).get("message", {})
            stop_reason = response.get("stopReason")
            messages.append(output_message)

            if stop_reason == "tool_use":
                tool_results = []
                for content_block in output_message.get("content", []):
                    if "toolUse" in content_block:
                        tool_use = content_block["toolUse"]
                        tool_use_id = tool_use["toolUseId"]
                        tool_name = tool_use["name"]
                        tool_input = tool_use.get("input", {})

                        # Execute tool
                        result = execute_tool(tool_name, tool_input)
                        tools_called.append({
                            "tool": tool_name,
                            "args": tool_input,
                            "result": result
                        })

                        tool_results.append({
                            "toolResult": {
                                "toolUseId": tool_use_id,
                                "content": [{"json": result}],
                                "status": "success" if "error" not in result else "error"
                            }
                        })

                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                # Normal completion
                text_blocks = [c["text"] for c in output_message.get("content", []) if "text" in c]
                final_text = " ".join(text_blocks).strip()
                return final_text or "All set!", tools_called, "bedrock"

        return "I completed your request.", tools_called, "bedrock"

    except (BotoCoreError, ClientError) as e:
        fallback_text, tools = run_mock_turn(message)
        notice = f"[Notice: Bedrock request failed ({e}). Safely fell back to mock provider] "
        return notice + fallback_text, tools, "mock"
    except Exception as e:
        fallback_text, tools = run_mock_turn(message)
        notice = f"[Notice: Bedrock error ({e}). Safely fell back to mock provider] "
        return notice + fallback_text, tools, "mock"


def process_user_turn(message: str, history: List[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]], str]:
    """
    Main entry point governed by LLM_PROVIDER.
    Returns (assistant_text, tools_called, provider_actually_used)
    """
    provider_pref = os.getenv("LLM_PROVIDER", "mock").lower().strip()
    if provider_pref == "bedrock":
        return run_bedrock_turn(message, history)
    else:
        text, tools = run_mock_turn(message)
        return text, tools, "mock"

