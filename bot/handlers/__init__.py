"""
Command handlers for the LMS Telegram bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram — same function works from:
- --test mode (CLI)
- Unit tests
- Real Telegram messages

This is called *separation of concerns*: business logic is separate from transport.
"""

from services import LmsApiClient
from config import load_config


async def handle_start() -> str:
    """Handle /start command — return welcome message."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


async def handle_help() -> str:
    """Handle /help command — list available commands."""
    return """Available commands:
/start — Welcome message
/help — Show this help
/health — Check backend status
/labs — List available labs
/scores <lab> — Get scores for a lab"""


async def handle_health() -> str:
    """Handle /health command — check backend health."""
    config = load_config()
    api_client = LmsApiClient(config)

    try:
        is_healthy = await api_client.health_check()
        if is_healthy:
            # Also get item count to prove connection works
            items = await api_client.get_items()
            if items:
                return f"✅ Backend is healthy. {len(items)} items available."
            else:
                return "✅ Backend is healthy. No items found."
        else:
            return "❌ Backend is unreachable or unhealthy"
    except Exception as e:
        error_msg = str(e)
        return f"❌ Backend error: {error_msg}. Check that the services are running."


async def handle_labs() -> str:
    """Handle /labs command — list available labs."""
    config = load_config()
    api_client = LmsApiClient(config)

    try:
        items = await api_client.get_items()
        if not items:
            return "No labs available. Backend may be down or data not synced."

        # Group by type (lab vs task)
        labs = []
        for item in items:
            name = item.get("name", "Unknown")
            item_type = item.get("type", "unknown")
            if item_type == "lab":
                labs.append(f"- {name}")

        if labs:
            return "Available labs:\n" + "\n".join(labs)
        else:
            # If no labs found, show all items
            all_items = "\n".join(
                f"- {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})"
                for item in items
            )
            return f"Available items:\n{all_items}"
    except Exception as e:
        error_msg = str(e)
        return (
            f"❌ Error fetching labs: {error_msg}. Check that the services are running."
        )


async def handle_scores(lab_name: str) -> str:
    """Handle /scores command — get scores for a lab."""
    if not lab_name:
        return "Usage: /scores <lab-name>\nExample: /scores lab-04"

    config = load_config()
    api_client = LmsApiClient(config)

    try:
        analytics = await api_client.get_analytics(lab_name)
        if not analytics:
            return f"No scores found for {lab_name}. The lab may not exist or backend is down."

        # Format the analytics response
        # Expected format: {"pass_rates": [{"task": "task-1", "pass_rate": 0.85, "attempts": 100}, ...]}
        pass_rates = analytics.get("pass_rates", [])
        if not pass_rates:
            return f"No pass rate data available for {lab_name}."

        lines = [f"Pass rates for {lab_name}:"]
        for rate in pass_rates:
            task_name = rate.get("task", "Unknown")
            pass_rate = rate.get("pass_rate", 0)
            attempts = rate.get("attempts", 0)
            percentage = f"{pass_rate * 100:.1f}%"
            lines.append(f"- {task_name}: {percentage} ({attempts} attempts)")

        return "\n".join(lines)
    except Exception as e:
        error_msg = str(e)
        return f"❌ Error fetching scores: {error_msg}. Check that the services are running."


async def handle_unknown(text: str) -> str:
    """Handle unknown commands or plain text."""
    return f"I didn't understand: {text}. Try /help for available commands."
