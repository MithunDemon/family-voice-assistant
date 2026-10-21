from typing import Dict, Any, List
from storage import store

# Python functions wrapping store operations

def add_grocery_item(item: str, quantity: str = "1") -> Dict[str, Any]:
    return store.add_grocery_item(item=item, quantity=quantity)

def remove_grocery_item(item: str) -> Dict[str, Any]:
    return store.remove_grocery_item(item=item)

def list_groceries() -> Dict[str, Any]:
    items = store.list_groceries()
    return {"groceries": items, "count": len(items)}

def add_reminder(for_person: str, text: str, due_time: str = "soon") -> Dict[str, Any]:
    return store.add_reminder(for_person=for_person, text=text, due_time=due_time)

def list_reminders(for_person: str = None) -> Dict[str, Any]:
    reminders = store.list_reminders(for_person=for_person)
    return {"reminders": reminders, "count": len(reminders)}

def add_event(title: str, date: str = "Today", time: str = "All day") -> Dict[str, Any]:
    return store.add_event(title=title, date=date, time=time)

def list_events(date: str = None) -> Dict[str, Any]:
    events = store.list_events(date=date)
    return {"events": events, "count": len(events)}


TOOL_MAPPING = {
    "add_grocery_item": add_grocery_item,
    "remove_grocery_item": remove_grocery_item,
    "list_groceries": list_groceries,
    "add_reminder": add_reminder,
    "list_reminders": list_reminders,
    "add_event": add_event,
    "list_events": list_events,
}


def execute_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    func = TOOL_MAPPING.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(**args)
    except Exception as e:
        return {"error": str(e)}


# Bedrock Converse Tool Specifications
BEDROCK_TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "add_grocery_item",
                "description": "Add an item to the shared family grocery list with an optional quantity.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "item": {
                                "type": "string",
                                "description": "The grocery item name, e.g. milk, eggs, apples."
                            },
                            "quantity": {
                                "type": "string",
                                "description": "Optional quantity or packaging, e.g. 1 gallon, 1 carton, 2."
                            }
                        },
                        "required": ["item"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "remove_grocery_item",
                "description": "Remove an item from the family grocery list by its name.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "item": {
                                "type": "string",
                                "description": "The name of the item to remove from the grocery list."
                            }
                        },
                        "required": ["item"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "list_groceries",
                "description": "View all current items on the shared family grocery list.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "add_reminder",
                "description": "Set a reminder for a specific family member or everyone with a due time.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "for_person": {
                                "type": "string",
                                "description": "Who the reminder is for, e.g. Mom, Dad, Mia, Everyone."
                            },
                            "text": {
                                "type": "string",
                                "description": "The task or reminder description, e.g. call the doctor, pick up Mia."
                            },
                            "due_time": {
                                "type": "string",
                                "description": "When the reminder is due, e.g. at 4pm, tonight, tomorrow morning."
                            }
                        },
                        "required": ["for_person", "text"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "list_reminders",
                "description": "List reminders for the family, optionally filtered by person.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "for_person": {
                                "type": "string",
                                "description": "Optional filter for a specific family member."
                            }
                        }
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "add_event",
                "description": "Add a new event or appointment to the shared family calendar.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The event title or activity name, e.g. Soccer match, Dentist appointment."
                            },
                            "date": {
                                "type": "string",
                                "description": "The date of the event, e.g. Today, Tomorrow, Friday, Oct 25."
                            },
                            "time": {
                                "type": "string",
                                "description": "The time of the event, e.g. 10:00 AM, 3pm, All day."
                            }
                        },
                        "required": ["title"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "list_events",
                "description": "List events from the family calendar, optionally filtered by date.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Optional date filter such as 'today', 'tomorrow', 'Sunday'."
                            }
                        }
                    }
                }
            }
        }
    ]
}
