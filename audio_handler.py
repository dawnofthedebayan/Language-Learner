import os
from pathlib import Path

from config import (
    AUDIO_BACKEND,
    AUDIO_OUTPUT_PATH,
    OPENAI_API_KEY,
    OPENAI_TTS_MODEL,
    OPENAI_TTS_VOICE,
    OPENAI_WHISPER_MODEL,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
)


def speak(text: str, backend: str = AUDIO_BACKEND) -> None:

    if backend == "elevenlabs":
        elevenlabs_tts(text)
    else:
        whisper_tts(text)


def whisper_tts(text: str) -> None:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    os.makedirs(os.path.dirname(AUDIO_OUTPUT_PATH), exist_ok=True)
    response = client.audio.speech.create(
        model=OPENAI_TTS_MODEL,
        voice=OPENAI_TTS_VOICE,
        input=text,
        #language="de",
    )
    response.stream_to_file(AUDIO_OUTPUT_PATH)
    print(f"[Audio] Saved to {AUDIO_OUTPUT_PATH}")


def elevenlabs_tts(text: str) -> None:
    import httpx

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    os.makedirs(os.path.dirname(AUDIO_OUTPUT_PATH), exist_ok=True)
    with httpx.Client(timeout=60) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        Path(AUDIO_OUTPUT_PATH).write_bytes(response.content)
    print(f"[Audio] Saved to {AUDIO_OUTPUT_PATH}")


def transcribe_audio(filepath: str, backend: str = AUDIO_BACKEND) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    with open(filepath, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=OPENAI_WHISPER_MODEL,
            file=audio_file,
        )
    return transcript.text


# test 
if __name__ == "__main__":
    
    speak("Hallo, wie geht es dir?")

