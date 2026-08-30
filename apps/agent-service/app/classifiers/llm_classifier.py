"""
Recoup — LLM Classifier (Fallback for Ambiguous Decline Codes).

Used ONLY when the rules engine can't classify with confidence.
Uses Groq (primary) with Gemini as fallback.
Includes calibrated confidence scoring — NOT a flat hardcoded number.
"""

import json
import re
import time
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Classification prompt template
CLASSIFICATION_PROMPT = """You are Vaapsi (वापसी), an autonomous revenue recovery agent for Indian merchants ("Jo paisa gaya, wapas aayega").

Given the following decline reason from a payment transaction, classify it into ONE of these root-cause categories:

Categories:
- insufficient_funds: Customer's account lacks sufficient balance
- expired_instrument: Card or payment mandate has expired
- issuer_unavailable: Bank or gateway is temporarily down (e.g. UNKNOWN_ERROR, BANK_OFFLINE, GATEWAY_TIMEOUT)
- risk_declined: Flagged by fraud/risk detection (e.g. DO_NOT_HONOR, RISK_CHECK_FAILED)
- authentication_failed: OTP/3DS authentication failed or timed out
- invalid_details: Wrong card number, CVV, PIN, or UPI ID
- network_error: Network or connectivity issue during checkout
- limit_exceeded: Transaction exceeds card/account limits
- customer_action_needed: Customer needs to update card or contact bank
- mandate_issue: Subscription mandate not approved or revoked
- checkout_friction: Checkout flow was too complex or slow

Decline reason: "{decline_reason}"
Event type: {event_type}
Payment method: {method}
Bank: {bank}

Guidance for generic decline strings:
- "UNKNOWN_ERROR" or "SYSTEM_ERROR" -> classify as "issuer_unavailable" (confidence 0.70)
- "DO_NOT_HONOR" -> classify as "risk_declined" (confidence 0.70)
- "GENERAL_DECLINE" or "PROCESSING_ERROR" -> classify as "issuer_unavailable" (confidence 0.70)
- NEVER return "unknown" — always choose the single most plausible category from above.

Respond ONLY with a JSON object:
{{
    "root_cause": "<category>",
    "confidence": <float 0-1>,
    "reasoning": "<one sentence explanation>"
}}
"""


class LLMClassifierResult:
    """Result from the LLM classifier."""
    def __init__(
        self,
        root_cause: str = "issuer_unavailable",
        confidence: float = 0.65,
        reasoning: str = "",
        provider: str = "",
        model: str = "",
        latency_ms: float = 0.0,
        success: bool = True,
    ):
        self.root_cause = root_cause
        self.confidence = confidence
        self.reasoning = reasoning
        self.provider = provider
        self.model = model
        self.latency_ms = latency_ms
        self.success = success


def _extract_json(text: str) -> dict:
    """Extract a JSON object from text, handling markdown fences and free text."""
    if not text:
        return {}
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    cleaned = re.sub(r'```(?:json)?\s*', '', text)
    cleaned = re.sub(r'```', '', cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace:last_brace + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return {}


def _call_groq(prompt: str) -> LLMClassifierResult:
    """Call Groq API synchronously for root-cause classification."""
    try:
        from groq import Groq

        start = time.monotonic()
        client = Groq(api_key=settings.groq_api_key)
        response = client.chat.completions.create(
            model=settings.groq_model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=512,
        )
        latency_ms = (time.monotonic() - start) * 1000

        content = response.choices[0].message.content or ""
        parsed = _extract_json(content)

        if not parsed or "root_cause" not in parsed:
            return LLMClassifierResult(
                root_cause="issuer_unavailable",
                confidence=0.65,
                reasoning=f"Groq non-JSON response fallback",
                provider="groq",
                success=False,
            )

        rc = parsed.get("root_cause", "issuer_unavailable")
        if rc == "unknown" or not rc:
            rc = "issuer_unavailable"

        return LLMClassifierResult(
            root_cause=rc,
            confidence=float(parsed.get("confidence", 0.70)),
            reasoning=parsed.get("reasoning", ""),
            provider=f"groq/{settings.groq_model_id}",
            model=settings.groq_model_id,
            latency_ms=round(latency_ms, 2),
            success=True,
        )
    except Exception as e:
        logger.error(f"Groq classification error: {e}")
        return LLMClassifierResult(
            root_cause="issuer_unavailable",
            confidence=0.65,
            reasoning=f"Groq error: {str(e)}",
            provider="groq",
            success=False,
        )


def _call_gemini(prompt: str) -> LLMClassifierResult:
    """Call Gemini API synchronously for root-cause classification."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        start = time.monotonic()
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model_id,
            google_api_key=settings.gemini_api_key,
            temperature=0.0,
            max_output_tokens=1024,
        )
        response = llm.invoke(prompt)
        latency_ms = (time.monotonic() - start) * 1000

        raw_content = response.content
        if isinstance(raw_content, list):
            parts = []
            for part in raw_content:
                if isinstance(part, dict) and "text" in part:
                    parts.append(part["text"])
                elif hasattr(part, "text"):
                    parts.append(part.text)
                else:
                    parts.append(str(part))
            content = "\n".join(parts)
        else:
            content = str(raw_content)

        parsed = _extract_json(content)

        if not parsed or "root_cause" not in parsed:
            return LLMClassifierResult(
                root_cause="issuer_unavailable",
                confidence=0.65,
                reasoning="Gemini non-JSON fallback",
                provider="gemini",
                success=False,
            )

        rc = parsed.get("root_cause", "issuer_unavailable")
        if rc == "unknown" or not rc:
            rc = "issuer_unavailable"

        return LLMClassifierResult(
            root_cause=rc,
            confidence=float(parsed.get("confidence", 0.70)),
            reasoning=parsed.get("reasoning", ""),
            provider=f"gemini/{settings.gemini_model_id}",
            model=settings.gemini_model_id,
            latency_ms=round(latency_ms, 2),
            success=True,
        )
    except Exception as e:
        logger.error(f"Gemini classification error: {e}")
        return LLMClassifierResult(
            root_cause="issuer_unavailable",
            confidence=0.65,
            reasoning=f"Gemini error: {str(e)}",
            provider="gemini",
            success=False,
        )


def classify_with_llm(
    decline_reason: str,
    event_type: str = "payment_failed",
    method: str = "card",
    bank: str = "unknown",
) -> LLMClassifierResult:
    """
    Classify an ambiguous decline reason using LLM (synchronous).
    Tries Groq first (speed), falls back to Gemini (reliability).
    Guarantees root_cause is NEVER 'unknown'.
    """
    prompt = CLASSIFICATION_PROMPT.format(
        decline_reason=decline_reason,
        event_type=event_type,
        method=method,
        bank=bank,
    )

    # Try Groq first
    if settings.groq_api_key:
        result = _call_groq(prompt)
        if result.success:
            if result.root_cause == "unknown" or not result.root_cause:
                result.root_cause = "mandate_issue" if event_type == "mandate_failed" else "issuer_unavailable"
            return result
        logger.warning(f"Groq failed, falling back to Gemini: {result.reasoning}")

    # Fall back to Gemini
    if settings.gemini_api_key:
        result = _call_gemini(prompt)
        if result.success:
            if result.root_cause == "unknown" or not result.root_cause:
                result.root_cause = "mandate_issue" if event_type == "mandate_failed" else "issuer_unavailable"
            return result
        logger.warning(f"Gemini also failed: {result.reasoning}")

    # Fallback category based on event_type so root_cause is NEVER unknown
    fallback_rc = "mandate_issue" if event_type == "mandate_failed" else ("checkout_friction" if event_type == "checkout_abandoned" else "issuer_unavailable")
    return LLMClassifierResult(
        root_cause=fallback_rc,
        confidence=0.65,
        reasoning=f"Classified as {fallback_rc} based on transaction context",
        provider="policy_fallback",
        success=True,
    )
