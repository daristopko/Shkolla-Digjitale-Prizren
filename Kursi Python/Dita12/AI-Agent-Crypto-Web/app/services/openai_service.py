from __future__ import annotations

import json
from typing import TypeVar

import httpx
from openai import APIConnectionError, APIStatusError, APITimeoutError, AuthenticationError, OpenAI
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class OpenAIService:
    def __init__(self, api_key: str, model: str, base_url: str = ""):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to .env before running AI analysis.")
        if api_key.strip().upper().startswith("OPENAI_API_KEY") or api_key.strip().lower() in {"your_key_here", "sk-..."}:
            raise ValueError("OPENAI_API_KEY still looks like a placeholder. Add a real sk-... OpenAI key or nvapi-... NVIDIA key in Settings.")
        base_url = base_url.strip()
        if not base_url and api_key.startswith("nvapi-"):
            base_url = "https://integrate.api.nvidia.com/v1"
        if not base_url:
            base_url = "https://api.openai.com/v1"
        client_args = {
            "api_key": api_key,
            "base_url": base_url,
            # Ignore broken machine-wide proxy env vars such as HTTP_PROXY=127.0.0.1:9.
            "http_client": httpx.Client(trust_env=False, timeout=30),
        }
        self.client = OpenAI(**client_args)
        self.model = model
        self.base_url = base_url

    def structured(self, system: str, payload: dict, schema: type[T]) -> tuple[str, T]:
        prompt = json.dumps(payload, separators=(",", ":"), default=str)
        last_error = ""
        for attempt in range(2):
            instruction = system + " Return valid JSON only matching this JSON Schema: " + json.dumps(schema.model_json_schema())
            if attempt:
                instruction += f" Previous output was invalid ({last_error}). Correct it; no markdown."
            try:
                response = self.client.chat.completions.create(model=self.model, temperature=0.1, response_format={"type": "json_object"}, messages=[{"role": "system", "content": instruction}, {"role": "user", "content": prompt}])
            except AuthenticationError as error:
                raise ValueError(self._auth_message()) from error
            except (APIConnectionError, APITimeoutError) as error:
                raise ValueError(
                    "AI provider connection failed. Check your internet connection, firewall/VPN, Base URL, and model settings. "
                    "For OpenAI keys, leave Base URL empty. For NVIDIA nvapi keys, use https://integrate.api.nvidia.com/v1."
                ) from error
            except APIStatusError as error:
                if error.status_code == 401:
                    raise ValueError(self._auth_message()) from error
                raise
            raw = response.choices[0].message.content or "{}"
            try:
                return raw, schema.model_validate_json(raw)
            except (ValidationError, ValueError) as error:
                last_error = str(error)
        raise ValueError(f"AI returned invalid structured output twice: {last_error}")

    def _auth_message(self) -> str:
        provider = "NVIDIA" if self.base_url and "nvidia.com" in self.base_url else "OpenAI"
        return (
            f"{provider} API key was rejected. Check Settings: API key, model, and Base URL.\n\n"
            "For OpenAI use an sk-... key with Base URL empty.\n"
            "For NVIDIA nvapi-... keys use Base URL https://integrate.api.nvidia.com/v1."
        )
