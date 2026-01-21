from typing import List
from datetime import datetime

from app.models import Message, VerificationResult
from app.services import LLMService


class Verifier:
    """
    Verifies whether the candidate agent achieved its objective
    based on the conversation history.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def verify(
        self,
        candidate_objective: str,
        verification_prompt: str,
        conversation_history: List[Message]
    ) -> VerificationResult:
        """
        Verify if the candidate achieved its objective.

        Args:
            candidate_objective: The objective the candidate was trying to achieve
            verification_prompt: Custom verification instructions
            conversation_history: Full conversation between agents

        Returns:
            VerificationResult with success status and explanation
        """
        # Build verification prompt
        system_prompt = f"""You are a verification system. Your job is to determine whether the candidate agent successfully achieved its objective based on the conversation history.

CANDIDATE'S OBJECTIVE:
{candidate_objective}

VERIFICATION CRITERIA:
{verification_prompt}

Analyze the conversation and determine:
1. Did the candidate achieve its objective?
2. Provide a clear explanation of why or why not.

Respond in the following format:
SUCCESS: [YES or NO]
EXPLANATION: [Your detailed explanation]
"""

        # Format conversation history
        conversation_text = self._format_conversation(conversation_history)

        # Call LLM to verify
        messages = [
            {"role": "user", "content": f"Here is the conversation to verify:\n\n{conversation_text}"}
        ]

        response, _ = await self.llm_service.generate_response(
            model="claude-sonnet-4-5-20250929",  # Use a capable model for verification
            system_prompt=system_prompt,
            messages=messages,
            temperature=0.0,  # Deterministic verification
            max_tokens=2048
        )

        # Parse response
        success = self._parse_success(response)
        explanation = self._parse_explanation(response)

        return VerificationResult(
            success=success,
            explanation=explanation,
            timestamp=datetime.now()
        )

    def _format_conversation(self, messages: List[Message]) -> str:
        """Format conversation history for verification"""
        formatted = []
        for msg in messages:
            speaker = msg.role.value.upper()
            formatted.append(f"[{speaker} - Turn {msg.turn_number}]")
            formatted.append(msg.content)
            if msg.reasoning:
                formatted.append(f"[{speaker} Internal Reasoning: {msg.reasoning}]")
            formatted.append("")  # Blank line

        return "\n".join(formatted)

    def _parse_success(self, response: str) -> bool:
        """Parse success status from verification response"""
        response_upper = response.upper()
        if "SUCCESS: YES" in response_upper or "SUCCESS:YES" in response_upper:
            return True
        elif "SUCCESS: NO" in response_upper or "SUCCESS:NO" in response_upper:
            return False
        else:
            # Default to checking for "YES" or "NO" in the response
            if "YES" in response_upper and "NO" not in response_upper:
                return True
            return False

    def _parse_explanation(self, response: str) -> str:
        """Parse explanation from verification response"""
        # Try to extract explanation after "EXPLANATION:"
        if "EXPLANATION:" in response.upper():
            parts = response.split("EXPLANATION:", 1)
            if len(parts) > 1:
                return parts[1].strip()

        # Otherwise return the full response
        return response.strip()
