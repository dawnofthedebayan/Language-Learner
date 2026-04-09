import os
from dotenv import load_dotenv

load_dotenv()

# --- OpenRouter ---
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
OPENROUTER_MODELS_TEXT_AVAILABLE: list = os.getenv("OPENROUTER_MODELS_AVAILABLE", [
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-2-9b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
])

# --- OpenAI (Whisper + TTS) ---
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_TTS_MODEL: str = "tts-1"
OPENAI_TTS_VOICE: str = "nova"
OPENAI_WHISPER_MODEL: str = "whisper-1"

# --- ElevenLabs ---
ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "")

# --- Audio backend: "whisper" | "elevenlabs" ---
AUDIO_BACKEND: str = os.getenv("AUDIO_BACKEND", "whisper")

# --- News ---
NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
NEWS_BASE_URL: str = "https://newsapi.org/v2/top-headlines"
NEWS_MAX_ARTICLES: int = 3
NEWS_LANGUAGE: str = "en"

# --- Memory ---
MEMORY_PATH: str = os.path.join(os.path.dirname(__file__), "data", "memory.json")
MEMORY_MAX_CHARS: int = 6000
MEMORY_KEEP_RECENT: int = 4

# --- Topics ---
TOPICS_PATH: str = os.path.join(os.path.dirname(__file__), "data", "topics.json")

# --- CEFR level ---
CEFR_LEVEL: str = "B2-C2"

# --- Output ---
AUDIO_OUTPUT_PATH: str = os.path.join(os.path.dirname(__file__), "data", "lesson_audio.mp3")
