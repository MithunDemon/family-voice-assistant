import asyncio
from typing import Dict, Any, Optional
from mcp.server.mcpserver import MCPServer
import tools

# Initialize MCP Server instance
mcp = MCPServer("FamilyVoiceAssistantTools")


@mcp.tool()
def add_grocery_item(item: str, quantity: str = "1") -> Dict[str, Any]:
    """
    Add an item to the shared family grocery list with an optional quantity.
    
    Args:
        item: The grocery item name (e.g. 'milk', 'eggs', 'apples')
        quantity: Optional quantity or packaging (e.g. '1 gallon', '1 carton', '2')
    """
    return tools.add_grocery_item(item=item, quantity=quantity)


@mcp.tool()
def remove_grocery_item(item: str) -> Dict[str, Any]:
    """
    Remove an item from the shared family grocery list by name.
    
    Args:
        item: The name of the item to remove
    """
    return tools.remove_grocery_item(item=item)


@mcp.tool()
def list_groceries() -> Dict[str, Any]:
    """
    View all current items on the shared family grocery list.
    """
    return tools.list_groceries()


@mcp.tool()
def add_reminder(for_person: str, text: str, due_time: str = "soon") -> Dict[str, Any]:
    """
    Set a time-sensitive reminder for a specific family member or everyone.
    
    Args:
        for_person: Who the reminder is for (e.g. 'Mom', 'Dad', 'Mia', 'Everyone')
        text: The task or reminder description (e.g. 'call the doctor', 'pick up Mia')
        due_time: When the reminder is due (e.g. 'at 4pm', 'tonight', 'tomorrow morning')
    """
    return tools.add_reminder(for_person=for_person, text=text, due_time=due_time)


@mcp.tool()
def list_reminders(for_person: Optional[str] = None) -> Dict[str, Any]:
    """
    List reminders for the family, optionally filtered by family member.
    
    Args:
        for_person: Optional filter for a specific family member
    """
    return tools.list_reminders(for_person=for_person)


@mcp.tool()
def add_event(title: str, date: str = "Today", time: str = "All day") -> Dict[str, Any]:
    """
    Schedule an event or appointment on the shared family calendar.
    
    Args:
        title: The event title or activity (e.g. 'Soccer match', 'Dentist appointment')
        date: The date of the event (e.g. 'Today', 'Tomorrow', 'Sunday', 'Oct 25')
        time: The time of the event (e.g. '10:00 AM', '3pm', 'All day')
    """
    return tools.add_event(title=title, date=date, time=time)


@mcp.tool()
def list_events(date: Optional[str] = None) -> Dict[str, Any]:
    """
    List events from the shared family calendar, optionally filtered by date.
    
    Args:
        date: Optional date filter such as 'today', 'tomorrow', 'sunday'
    """
    return tools.list_events(date=date)


async def main():
    print("[MCP Server] Starting Family Voice Assistant MCP server over Streamable HTTP on http://127.0.0.1:8001/mcp...")
    await mcp.run_streamable_http_async(
        host="127.0.0.1",
        port=8001,
        streamable_http_path="/mcp"
    )


if __name__ == "__main__":
    asyncio.run(main())
