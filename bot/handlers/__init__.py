"""
Command handlers for the LMS Telegram bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram — same function works from:
- --test mode (CLI)
- Unit tests
- Real Telegram messages

This is called *separation of concerns*: business logic is separate from transport.
"""


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
    # TODO: Task 2 — call backend /health endpoint
    return "Backend status: OK (placeholder)"


async def handle_labs() -> str:
    """Handle /labs command — list available labs."""
    # TODO: Task 2 — call backend /items endpoint
    return "Available labs: (placeholder)"


async def handle_scores(lab_name: str) -> str:
    """Handle /scores command — get scores for a lab."""
    # TODO: Task 2 — call backend /analytics endpoint
    return f"Scores for {lab_name}: (placeholder)"


async def handle_unknown(text: str) -> str:
    """Handle unknown commands or plain text."""
    # TODO: Task 3 — use LLM to understand intent
    return f"I didn't understand: {text}. Try /help for commands."
