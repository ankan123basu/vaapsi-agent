"""
Recoup — Groq Model Swap Proof Script.

Proves:
1. The new openai/gpt-oss-120b model on Groq works for classification
2. The Gemini fallback triggers correctly when Groq fails
"""

import sys
import os
import asyncio
import json

# Ensure we can import from the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Force UTF-8 output
sys.stdout.reconfigure(encoding="utf-8")

import pytest

from dotenv import load_dotenv
load_dotenv()

from app.config import settings


def test_groq_classification():
    """Test 1: Real classification calls through openai/gpt-oss-120b on Groq across 5 decline scenarios."""
    print("=" * 60)
    print(f"TEST 1: Groq Multi-Scenario Classification (model: {settings.groq_model_id})")
    print("=" * 60)

    from app.classifiers.llm_classifier import classify_with_llm

    scenarios = [
        ("Your bank has declined this transaction. Please contact your bank.", "payment_failed", "card", "HDFC"),
        ("OTP verification timed out before submission", "payment_failed", "netbanking", "ICICI"),
        ("Card limit exceeded for daily transactions", "payment_failed", "card", "AXIS"),
        ("Subscription mandate charge failed due to bank server timeout", "mandate_failed", "emandate", "SBI"),
        ("Customer abandoned cart after 15 minutes of inactivity", "checkout_abandoned", "upi", "UPI"),
    ]

    all_passed = True
    for idx, (reason, evt_type, method, bank) in enumerate(scenarios, 1):
        res = classify_with_llm(
            decline_reason=reason,
            event_type=evt_type,
            method=method,
            bank=bank,
        )
        passed = res.success and res.root_cause != "unknown"
        if not passed:
            all_passed = False

        print(f"  Scenario {idx}: [{evt_type}] '{reason[:40]}...'")
        print(f"    -> Root Cause: {res.root_cause} (conf: {res.confidence}) | Provider: {res.provider} | Latency: {res.latency_ms}ms | Pass: {passed}")

    print()
    assert all_passed


def test_gemini_fallback():
    """Test 2: Force Groq failure, verify Gemini catches it."""
    print("=" * 60)
    print("TEST 2: Gemini Fallback (forcing Groq failure with bad model)")
    print("=" * 60)

    # Temporarily override the Groq model to a non-existent model
    original_model = settings.groq_model_id
    settings.groq_model_id = "this-model-does-not-exist-12345"

    from app.classifiers.llm_classifier import classify_with_llm

    result = classify_with_llm(
        decline_reason="Payment declined due to insufficient funds in the account",
        event_type="payment_failed",
        method="upi",
        bank="SBI",
    )

    # Restore
    settings.groq_model_id = original_model

    print(f"  Success:      {result.success}")
    print(f"  Provider:     {result.provider}")
    print(f"  Model:        {result.model}")
    print(f"  Root Cause:   {result.root_cause}")
    print(f"  Confidence:   {result.confidence}")
    print(f"  Reasoning:    {result.reasoning}")
    print(f"  Latency (ms): {result.latency_ms}")
    print()

    is_gemini = "gemini" in result.provider.lower()
    print(f"  [{'PASS' if is_gemini else 'FAIL'}] Fallback to Gemini: {is_gemini}")
    return is_gemini


async def main():
    print()
    print("Recoup — Groq Model Swap Verification")
    print(f"Groq API Key set:   {'YES' if settings.groq_api_key else 'NO'}")
    print(f"Gemini API Key set: {'YES' if settings.gemini_api_key else 'NO'}")
    print(f"Groq Model ID:      {settings.groq_model_id}")
    print(f"Gemini Model ID:    {settings.gemini_model_id}")
    print()

    t1 = await test_groq_classification()
    t2 = await test_gemini_fallback()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Test 1 (Groq classification):  {'PASS' if t1 else 'FAIL'}")
    print(f"  Test 2 (Gemini fallback):      {'PASS' if t2 else 'FAIL'}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
