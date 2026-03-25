#!/usr/bin/env python3
"""
LMS Telegram Bot — Entry Point

Usage:
    Telegram mode:  uv run bot.py
    Test mode:      uv run bot.py --test "/command"

The bot uses a testable handler architecture:
- Handlers are plain functions that take input and return text
- Same handlers work from --test mode, unit tests, or Telegram
- This is called *separation of concerns*
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add bot directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_unknown,
)
from services import LmsApiClient


async def run_command(command: str) -> str:
    """
    Route a command to the appropriate handler and return the response.

    This function is called from both:
    - --test mode (CLI)
    - Telegram message handler
    """
    # Parse command and arguments
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    # Route to appropriate handler
    if cmd == "/start":
        return await handle_start()
    elif cmd == "/help":
        return await handle_help()
    elif cmd == "/health":
        return await handle_health()
    elif cmd == "/labs":
        return await handle_labs()
    elif cmd == "/scores":
        return await handle_scores(arg)
    else:
        # Unknown command or plain text
        return await handle_unknown(command)


async def run_telegram_bot():
    """Run the bot in Telegram mode (requires BOT_TOKEN)."""
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
    except ImportError:
        print("Error: aiogram not installed. Run: uv sync")
        sys.exit(1)

    config = load_config()

    if not config.bot_token:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    # Register command handlers
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        response = await handle_start()
        await message.answer(response)

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        response = await handle_help()
        await message.answer(response)

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        response = await handle_health()
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        response = await handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message, args: str):
        response = await handle_scores(args)
        await message.answer(response)

    @dp.message()
    async def handle_message(message: types.Message):
        """Handle plain text messages (Task 3: LLM intent routing)."""
        response = await handle_unknown(message.text)
        await message.answer(response)

    # Start polling
    print("Bot is running... Press Ctrl+C to stop.")
    await dp.start_polling(bot)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Run a command in test mode (no Telegram connection)",
    )

    args = parser.parse_args()

    if args.test:
        # Test mode: run command and print result to stdout
        response = asyncio.run(run_command(args.test))
        print(response)
        sys.exit(0)
    else:
        # Telegram mode: start the bot
        asyncio.run(run_telegram_bot())


if __name__ == "__main__":
    main()
