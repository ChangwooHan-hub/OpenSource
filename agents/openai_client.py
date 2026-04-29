from __future__ import annotations

import os
from typing import Any


class OpenAIReviewClient:
    """Small wrapper around the OpenAI Responses API.

    The agents are deterministic without an API key. When OPENAI_API_KEY is set,
    this client adds GPT-authored review notes without making XMI generation depend
    on a free-form model response.
    """

    def __init__(self, enabled: bool = True, max_output_tokens: int = 4096) -> None:
        self.enabled = enabled and bool(os.getenv("OPENAI_API_KEY"))
        self.max_output_tokens = max_output_tokens
        self._client: Any | None = None

    def _get_client(self) -> Any | None:
        if not self.enabled:
            return None
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
        except ImportError:
            self.enabled = False
            return None
        self._client = OpenAI()
        return self._client

    def review(self, model: str, developer_prompt: str, user_prompt: str) -> str | None:
        client = self._get_client()
        if client is None:
            return None

        response = client.responses.create(
            model=model,
            max_output_tokens=self.max_output_tokens,
            input=[
                {"role": "developer", "content": developer_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        output_text = getattr(response, "output_text", None)
        if output_text:
            return str(output_text).strip()

        fragments: list[str] = []
        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                text = getattr(content, "text", None)
                if text:
                    fragments.append(str(text))
        return "\n".join(fragments).strip() or None
