import requests
import json
import base64
from pydub import AudioSegment


API_KEY_REF = "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"


url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY_REF}",
    "Content-Type": "application/json",
    "X-Title": "TTS Debug",  # Helps routing
    "HTTP-Referer": "https://example.com"  # Optional
}

payload = {
    "model": "openai/gpt-audio-mini",
    "messages": [{"role": "user", "content": "Hello there, what is your name?"}],
    "modalities": ["text", "audio"],
    "audio": {
        "voice": "alloy",
        "format": "pcm16"  # Fix: pcm16 for stream=true
    },
    "stream": True
}

response = requests.post(url, headers=headers, json=payload, stream=True)

audio_data_chunks = []
transcript_chunks = []

if response.status_code == 200:
    for line in response.iter_lines():
        if not line:
            continue
        decoded = line.decode("utf-8")
        if not decoded.startswith("data: "):
            continue
        data = decoded[len("data: "):].strip()
        if data == "[DONE]":
            break
        chunk = json.loads(data)
        delta = chunk["choices"][0].get("delta", {})
        audio = delta.get("audio", {})
        if audio.get("data"):
            audio_data_chunks.append(audio["data"])
        if audio.get("transcript"):
            transcript_chunks.append(audio["transcript"])

    transcript = "".join(transcript_chunks)
    print(f"Transcript: {transcript}")

    if audio_data_chunks:
        full_audio_b64 = "".join(audio_data_chunks)
        audio_bytes = base64.b64decode(full_audio_b64)
        # Save as raw PCM (play with: ffplay -f s16le -ar 16000 -ac 1 output.pcm)
        with open("output.pcm", "wb") as f:
            f.write(audio_bytes)
        print("Saved output.pcm")
        
        # Convert to WAV with pydub (pip install pydub)
         
        pcm_audio = AudioSegment(output.pcm, frame_rate=16000, sample_width=2, channels=1)
        pcm_audio.export("output.wav", format="wav")
    else:
        print("No audio data")
else:
    print(f"Error: {response.text}")