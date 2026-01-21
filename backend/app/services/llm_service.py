import os
from typing import List, Dict, AsyncIterator, Optional
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
import json


class LLMService:
    """Service for interacting with LLM providers (Anthropic, OpenAI)"""

    def __init__(self):
        self.anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _is_anthropic_model(self, model: str) -> bool:
        """Check if model is an Anthropic model"""
        return model.startswith("claude")

    def _format_messages_for_provider(
        self,
        messages: List[Dict[str, str]],
        is_anthropic: bool
    ) -> List[Dict[str, str]]:
        """Format messages for the specific provider"""
        # Both providers use similar message format, but we can adapt if needed
        return messages

    async def generate_response(
        self,
        model: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 4096
    ) -> tuple[str, Optional[str]]:
        """
        Generate a response from the LLM.
        Returns: (content, reasoning) tuple
        """
        is_anthropic = self._is_anthropic_model(model)

        if is_anthropic:
            return await self._generate_anthropic(
                model, system_prompt, messages, temperature, max_tokens
            )
        else:
            return await self._generate_openai(
                model, system_prompt, messages, temperature, max_tokens
            )

    async def generate_response_stream(
        self,
        model: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 4096
    ) -> AsyncIterator[Dict[str, str]]:
        """
        Generate a streaming response from the LLM.
        Yields: {"type": "content"|"reasoning", "delta": str}
        """
        is_anthropic = self._is_anthropic_model(model)

        if is_anthropic:
            async for chunk in self._generate_anthropic_stream(
                model, system_prompt, messages, temperature, max_tokens
            ):
                yield chunk
        else:
            async for chunk in self._generate_openai_stream(
                model, system_prompt, messages, temperature, max_tokens
            ):
                yield chunk

    async def _generate_anthropic(
        self,
        model: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> tuple[str, Optional[str]]:
        """Generate response using Anthropic API"""
        response = await self.anthropic_client.messages.create(
            model=model,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        content = ""
        reasoning = None

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif hasattr(block, "thinking") and block.type == "thinking":
                reasoning = block.text

        return content, reasoning

    async def _generate_anthropic_stream(
        self,
        model: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncIterator[Dict[str, str]]:
        """Stream response using Anthropic API"""
        async with self.anthropic_client.messages.stream(
            model=model,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        ) as stream:
            async for event in stream:
                if hasattr(event, "type"):
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            yield {"type": "content", "delta": event.delta.text}
                        elif hasattr(event.delta, "thinking"):
                            yield {"type": "reasoning", "delta": event.delta.thinking}

    async def _generate_openai(
        self,
        model: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> tuple[str, Optional[str]]:
        """Generate response using OpenAI API"""
        # Prepend system message
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        content = response.choices[0].message.content or ""
        # OpenAI doesn't have built-in reasoning traces like Anthropic
        return content, None

    async def _generate_openai_stream(
        self,
        model: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncIterator[Dict[str, str]]:
        """Stream response using OpenAI API"""
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        stream = await self.openai_client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield {"type": "content", "delta": chunk.choices[0].delta.content}
