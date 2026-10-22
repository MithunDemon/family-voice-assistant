import json
import os
from typing import Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "family_store.json")

DEFAULT_STATE: Dict[str, Any] = {
    "groceries": [
        {"id": "g-1", "item": "Apples", "quantity": "1 bag"},
        {"id": "g-2", "item": "Almond milk", "quantity": "1 carton"}
    ],
    "reminders": [
        {"id": "r-1", "for_person": "Dad", "text": "Take out recycling", "due_time": "Tonight 8pm"},
        {"id": "r-2", "for_person": "Mia", "text": "Piano practice", "due_time": "Today 5pm"}
    ],
    "events": [
        {"id": "e-1", "title": "Soccer match", "date": "Tomorrow", "time": "10:00 AM"},
        {"id": "e-2", "title": "Family dinner", "date": "Sunday", "time": "6:30 PM"}
    ]
}


class FamilyStore:
    def __init__(self, filepath: str = DATA_FILE):
        self.filepath = filepath
        self.state: Dict[str, Any] = {}
        self._load()

    def _load(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
                    return
            except Exception:
                pass
        self.state = json.loads(json.dumps(DEFAULT_STATE))
        self._save()

    def _save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Store] Error saving state: {e}")

    def get_state(self) -> Dict[str, Any]:
        return self.state

    def reset(self) -> Dict[str, Any]:
        """Resets the store state to clean default seed data."""
        self.state = json.loads(json.dumps(DEFAULT_STATE))
        self._save()
        return self.state

    # Groceries
    def add_grocery_item(self, item: str, quantity: str = "1") -> Dict[str, Any]:
        raw_item = item.strip()
        # Capitalize the first letter of grocery item names (e.g. "milk" -> "Milk")
        clean_item = raw_item[0].upper() + raw_item[1:] if raw_item else ""
        if not clean_item:
            return {"success": False, "action": "empty", "item": ""}

        # Check if already exists (case-insensitive) - update instead of creating duplicate
        for g in self.state.get("groceries", []):
            if g["item"].lower() == clean_item.lower():
                g["quantity"] = quantity or g.get("quantity", "1")
                self._save()
                return {"success": True, "action": "updated", "item": g["item"], "quantity": g["quantity"]}

        new_entry = {
            "id": f"g-{len(self.state.get('groceries', [])) + 1}",
            "item": clean_item,
            "quantity": quantity or "1"
        }
        self.state.setdefault("groceries", []).append(new_entry)
        self._save()
        return {"success": True, "action": "added", "item": new_entry["item"], "quantity": new_entry["quantity"]}

    def remove_grocery_item(self, item: str) -> Dict[str, Any]:
        clean_item = item.strip().lower()
        groceries = self.state.get("groceries", [])
        matched = [g for g in groceries if g["item"].lower() == clean_item]
        if not matched:
            # Fallback partial match (e.g. "eggs" inside "brown eggs")
            matched = [g for g in groceries if clean_item in g["item"].lower()]

        if matched:
            target = matched[0]
            self.state["groceries"] = [g for g in groceries if g["id"] != target["id"]]
            self._save()
            return {"success": True, "action": "removed", "item": target["item"]}
        return {"success": False, "action": "not_found", "item": item}

    def list_groceries(self) -> List[Dict[str, Any]]:
        return self.state.get("groceries", [])

    # Reminders
    def add_reminder(self, for_person: str, text: str, due_time: str = "soon") -> Dict[str, Any]:
        person_clean = for_person.strip().capitalize() if for_person else "Everyone"
        clean_text = text.strip()
        clean_due = due_time.strip() if due_time else "soon"

        # Check for identical reminder (same person and similar/same text) - update instead of duplicate
        for r in self.state.get("reminders", []):
            if (r.get("for_person", "").lower() == person_clean.lower() and
                    r.get("text", "").lower().strip() == clean_text.lower()):
                r["due_time"] = clean_due
                self._save()
                return {"success": True, "action": "updated", "reminder": r}

        new_entry = {
            "id": f"r-{len(self.state.get('reminders', [])) + 1}",
            "for_person": person_clean,
            "text": clean_text,
            "due_time": clean_due
        }
        self.state.setdefault("reminders", []).append(new_entry)
        self._save()
        return {"success": True, "action": "added", "reminder": new_entry}

    def list_reminders(self, for_person: str = None) -> List[Dict[str, Any]]:
        reminders = self.state.get("reminders", [])
        if for_person:
            p_clean = for_person.strip().lower()
            return [r for r in reminders if r.get("for_person", "").lower() == p_clean]
        return reminders

    # Calendar Events
    def add_event(self, title: str, date: str = "Today", time: str = "All day") -> Dict[str, Any]:
        clean_title = title.strip()
        clean_date = date.strip().capitalize() if date else "Today"
        clean_time = time.strip() if time else "All day"

        # Avoid exact duplicate events
        for e in self.state.get("events", []):
            if (e.get("title", "").lower() == clean_title.lower() and
                    e.get("date", "").lower() == clean_date.lower()):
                e["time"] = clean_time
                self._save()
                return {"success": True, "action": "updated", "event": e}

        new_entry = {
            "id": f"e-{len(self.state.get('events', [])) + 1}",
            "title": clean_title,
            "date": clean_date,
            "time": clean_time
        }
        self.state.setdefault("events", []).append(new_entry)
        self._save()
        return {"success": True, "action": "added", "event": new_entry}

    def list_events(self, date: str = None) -> List[Dict[str, Any]]:
        events = self.state.get("events", [])
        if date:
            d_clean = date.strip().lower()
            return [e for e in events if d_clean in e.get("date", "").lower()]
        return events


# Global storage instance
store = FamilyStore()
