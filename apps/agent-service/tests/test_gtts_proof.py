import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.channels.voice import hinglish_voice_channel

def test_voice():
    script = hinglish_voice_channel.generate_hinglish_script("Neha Patel", 5000.0, "insufficient_funds")
    print("Generated Script:", script)

    result = hinglish_voice_channel.synthesize_hinglish_speech(script, lang="hi")
    print("Success:", result.get("success"))
    print("Format:", result.get("audio_format"))
    print("Size (bytes):", result.get("size_bytes"))
    print("Base64 preview:", result.get("audio_base64")[:40] + "...")

if __name__ == "__main__":
    test_voice()
