# LMS Telegram Bot — Development Plan

## Overview

This document describes the implementation plan for the LMS Telegram bot, which allows users to interact with the LMS backend through chat. The bot supports slash commands like `/health` and `/labs`, and uses an LLM to understand plain text questions.

## Architecture

The bot follows a **testable handler architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      Entry Point (bot.py)                    │
│  - CLI --test mode                                          │
│  - Telegram polling (aiogram)                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Handlers (handlers/)                    │
│  - Plain functions: input → text                            │
│  - No Telegram dependency                                   │
│  - Testable in isolation                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Services (services/)                    │
│  - LmsApiClient: HTTP client for backend                    │
│  - LlmClient: LLM API for intent routing                    │
└─────────────────────────────────────────────────────────────┘
```

## Task 1: Scaffold and Test Mode

**Goal:** Create project structure with `--test` mode for offline verification.

**Approach:**

- Create `bot/` directory with `bot.py`, `handlers/`, `services/`, `config.py`
- Implement `--test` mode that calls handlers directly without Telegram
- Handlers return placeholder text initially
- Verify with `uv run bot.py --test "/command"`

**Deliverables:**

- `bot/bot.py` — entry point with `--test` mode
- `bot/handlers/__init__.py` — handler functions
- `bot/config.py` — environment loading with pydantic-settings
- `bot/pyproject.toml` — dependencies (aiogram, httpx, pydantic-settings)

## Task 2: Backend Integration

**Goal:** Connect slash commands to real backend data.

**Approach:**

- Implement `LmsApiClient` with Bearer token authentication
- Add error handling for network failures and non-200 responses
- Update handlers to call API endpoints:
  - `/health` → `GET /health`
  - `/labs` → `GET /items/`
  - `/scores <lab>` → `GET /analytics/{lab}`
- Format responses for Telegram (markdown, tables)

**Deliverables:**

- `bot/services/lms_api.py` — API client with retry logic
- Updated handlers with real API calls
- Friendly error messages when backend is down

## Task 3: Intent-Based Natural Language Routing

**Goal:** Use LLM to understand plain text queries and route to appropriate tool.

**Approach:**

- Define tool descriptions for all 9 backend endpoints
- Use LLM to parse user intent and select tool
- Execute tool with LLM-provided parameters
- Format and return results

**Tool descriptions example:**

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_labs",
            "description": "List all available labs",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get scores for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab_name": {"type": "string", "description": "Lab name like 'lab-04'"}
                },
                "required": ["lab_name"]
            }
        }
    }
]
```

**Deliverables:**

- `bot/services/llm_client.py` — LLM API client
- `bot/handlers/intent_router.py` — LLM-based routing
- Tool descriptions for all endpoints

## Task 4: Containerize and Deploy

**Goal:** Deploy bot alongside backend on VM using Docker Compose.

**Approach:**

- Create `bot/Dockerfile` with Python 3.14 base image
- Add bot service to `docker-compose.yml`
- Configure networking (containers use service names, not localhost)
- Set up health checks and restart policies
- Document deployment in README

**Docker networking:**

```yaml
services:
  bot:
    build: ./bot
    environment:
      - LMS_API_BASE_URL=http://backend:8000
    depends_on:
      - backend
```

**Deliverables:**

- `bot/Dockerfile`
- Updated `docker-compose.yml`
- Deployment documentation

## Testing Strategy

1. **Unit tests** — Test handlers in isolation with mocked services
2. **Test mode** — Manual verification via `--test` flag
3. **Integration tests** — Test against running backend
4. **E2E tests** — Test in Telegram with real user flow

## Security Considerations

- Secrets loaded from `.env.bot.secret` (gitignored)
- Bearer token authentication for API calls
- No secrets committed to git
- Input validation on all user-provided data

## Future Improvements (P2)

- Response caching to reduce API calls
- Conversation context for multi-turn dialogs
- Rich formatting (tables, charts as images)
- Inline keyboard buttons for common actions
