FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy bot project files
COPY pyproject.toml uv.lock* ./

# Sync dependencies
RUN uv sync --frozen --no-dev

# Copy bot source code
COPY . .

# Run the bot
CMD ["uv", "run", "bot.py"]
