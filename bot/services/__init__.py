"""
Services for the LMS Telegram bot.

Services handle external API communication:
- LmsApiClient — communicates with the LMS backend
- LlmClient — communicates with the LLM API (Task 3)
"""

import httpx
from config import BotConfig


class LmsApiClient:
    """Client for the LMS backend API."""

    def __init__(self, config: BotConfig):
        self.config = config
        self.base_url = config.lms_api_base_url
        self.headers = config.lms_headers

    async def health_check(self) -> bool:
        """Check if the backend is healthy."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self.headers,
                    timeout=5.0,
                )
                return response.status_code == 200
            except httpx.HTTPError:
                return False

    async def get_items(self) -> list:
        """Get all items (labs) from the backend."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/items/",
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return []

    async def get_analytics(self, lab_name: str) -> dict:
        """Get analytics/scores for a specific lab."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/analytics/{lab_name}",
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return {}


class LlmClient:
    """Client for the LLM API (Task 3)."""

    def __init__(self, config: BotConfig):
        self.config = config
        self.base_url = config.llm_api_base_url
        self.headers = config.llm_headers
        self.model = config.llm_api_model

    async def chat(self, messages: list, tools: list | None = None) -> dict:
        """Send a chat request to the LLM."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "model": self.model,
                    "messages": messages,
                }
                if tools:
                    payload["tools"] = tools
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"error": str(e)}
