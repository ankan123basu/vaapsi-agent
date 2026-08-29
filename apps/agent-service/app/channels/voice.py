"""
Recoup — Multi-Language Voice Recovery Channel Adapter (gTTS + Groq Whisper STT).

Supports English, Hindi, Hinglish, Tamil, and Bengali voice recovery synthesis
with localized message content per language.
"""

import time
import logging
from typing import Optional, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)

# Supported languages for gTTS synthesis
SUPPORTED_LANGUAGES = {
    "en": {"label": "English", "gtts_lang": "en", "tld": "co.in"},
    "hi": {"label": "Hindi", "gtts_lang": "hi", "tld": "co.in"},
    "hinglish": {"label": "Hinglish", "gtts_lang": "hi", "tld": "co.in"},
    "ta": {"label": "Tamil", "gtts_lang": "ta", "tld": "co.in"},
    "bn": {"label": "Bengali", "gtts_lang": "bn", "tld": "co.in"},
}


class HinglishVoiceChannel:
    """Channel adapter for multi-language voice recovery communications."""

    def __init__(self):
        self.groq_api_key = settings.groq_api_key
        self.whisper_model = settings.groq_whisper_model_id  # whisper-large-v3-turbo

    async def transcribe_hinglish_audio(self, audio_file_bytes: bytes, filename: str = "audio.wav") -> Dict[str, Any]:
        """
        Transcribe Hinglish voice response using Groq Whisper.

        Returns transcription text, language detected, and latency.
        """
        if not self.groq_api_key:
            logger.warning("Groq API key not set. Using simulated STT transcription.")
            return {
                "text": "Haanser payment fail ho gaya tha, Naya link bhej do mai abhi pay kar deta hu.",
                "language": "hi/en",
                "confidence": 0.95,
                "latency_ms": 120.0,
                "simulated": True,
            }

        try:
            from groq import AsyncGroq

            client = AsyncGroq(api_key=self.groq_api_key)
            start = time.monotonic()

            transcription = await client.audio.transcriptions.create(
                file=(filename, audio_file_bytes),
                model=self.whisper_model,
                response_format="verbose_json",
            )
            latency_ms = (time.monotonic() - start) * 1000

            return {
                "text": transcription.text,
                "language": getattr(transcription, "language", "hi"),
                "confidence": 0.96,
                "latency_ms": round(latency_ms, 2),
                "simulated": False,
            }
        except Exception as e:
            logger.error(f"Groq Whisper transcription failed: {e}")
            return {
                "text": "[Transcription Error] " + str(e),
                "language": "unknown",
                "confidence": 0.0,
                "latency_ms": 0.0,
                "error": str(e),
            }

    def generate_recovery_script(self, customer_name: str, amount_inr: float, reason: str, lang: str = "hinglish") -> str:
        """Generate localized recovery script in the requested language."""
        formatted_amount = f"INR {amount_inr:,.0f}"

        scripts = {
            "en": (
                f"Hello {customer_name}! This is the Vaapsi recovery assistant. "
                f"Your payment of {formatted_amount} could not be completed in a recent transaction. "
                f"Would you like to receive a new payment link to complete your payment now?"
            ),
            "hi": (
                f"नमस्ते {customer_name} जी! मैं वापसी रिकवरी असिस्टेंट बोल रहा हूं। "
                f"आपका {formatted_amount} का भुगतान हाल ही की एक ट्रांजैक्शन में पूरा नहीं हो सका। "
                f"क्या आप अभी एक नया पेमेंट लिंक प्राप्त करके भुगतान करना चाहेंगे?"
            ),
            "hinglish": (
                f"Namaste {customer_name} ji! Main Vaapsi assistant bol raha hu. "
                f"Aapka {formatted_amount} ka payment recent transaction me complete nahi ho paya tha. "
                f"Kya aap abhi naya payment link receive karke pay karna chahenge?"
            ),
            "ta": (
                f"வணக்கம் {customer_name}! நான் Vaapsi மீட்பு உதவியாளர் பேசுகிறேன். "
                f"உங்கள் {formatted_amount} கட்டணம் சமீபத்திய பரிவர்த்தனையில் முடிக்கப்படவில்லை. "
                f"நீங்கள் இப்போது புதிய கட்டண இணைப்பைப் பெற்று பணம் செலுத்த விரும்புகிறீர்களா?"
            ),
            "bn": (
                f"নমস্কার {customer_name}! আমি Vaapsi রিকভারি অ্যাসিস্ট্যান্ট বলছি। "
                f"আপনার {formatted_amount} টাকার পেমেন্ট সাম্প্রতিক একটি লেনদেনে সম্পন্ন হয়নি। "
                f"আপনি কি এখন একটি नया পেমেন্ট লিঙ্ক পেয়ে পেমেন্ট করতে চান?"
            ),
        }

        return scripts.get(lang, scripts["hinglish"])

    # Backward-compatible alias
    def generate_hinglish_script(self, customer_name: str, amount_inr: float, reason: str) -> str:
        """Generate Hinglish voice script for recovery call (backward-compatible)."""
        return self.generate_recovery_script(customer_name, amount_inr, reason, lang="hinglish")

    def synthesize_hinglish_speech(self, text: str, lang: str = "hi") -> Dict[str, Any]:
        """
        Synthesize speech from text using gTTS.
        Returns audio format, base64 data / bytes, and status.
        """
        import io
        import base64

        try:
            from gtts import gTTS

            # Resolve the actual gTTS language code
            lang_config = SUPPORTED_LANGUAGES.get(lang, SUPPORTED_LANGUAGES.get("hinglish"))
            gtts_lang = lang_config["gtts_lang"] if lang_config else "hi"
            tld = lang_config.get("tld", "co.in") if lang_config else "co.in"

            tts = gTTS(text=text, lang=gtts_lang, tld=tld, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            audio_bytes = fp.read()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

            return {
                "success": True,
                "text": text,
                "language": lang,
                "audio_format": "mp3",
                "audio_base64": audio_b64,
                "size_bytes": len(audio_bytes),
            }
        except Exception as e:
            logger.error(f"gTTS speech synthesis failed: {e}")
            return {
                "success": False,
                "text": text,
                "error": str(e),
            }

    def get_supported_languages(self) -> list:
        """Return list of supported language options."""
        return [{"code": code, "label": info["label"]} for code, info in SUPPORTED_LANGUAGES.items()]


# Global singleton instance
hinglish_voice_channel = HinglishVoiceChannel()
