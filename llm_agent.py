import httpx
from typing import Callable

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    CEFR_LEVEL,
    OPENROUTER_MODELS_TEXT_AVAILABLE
)


def build_prompt(
    topic: str,
    news_context: str,
    memory_summary: str,
    cefr_level: str = CEFR_LEVEL,
) -> list:
    system_message = (
        f"Du bist ein erfahrener Deutschlehrer, der Lernende auf {cefr_level}-Niveau unterrichtet. "
        "Deine Aufgabe ist es, täglich einen lehrreichen deutschen Absatz (150–200 Wörter) zu einem "
        "gegebenen Thema zu verfassen, der aktuelle Nachrichten einbezieht. "
        "Schreibe anspruchsvolles, natürliches Deutsch. "
        "Füge am Ende eine kurze Vokabelliste mit 5 schwierigen Wörtern und ihrer englischen Übersetzung an. "
        "Halte dich an folgendes Format:\n\n"
        "**Tagesabsatz:**\n<paragraph>\n\n**Vokabeln:**\n<vocabulary list>"
    )

    user_parts = []
    if memory_summary:
        user_parts.append(f"[Lernverlauf-Zusammenfassung]\n{memory_summary}")
    user_parts.append(f"[Heutiges Thema]\n{topic}")
    user_parts.append(f"[Aktuelle Nachrichten zum Thema]\n{news_context}")
    user_parts.append("Bitte schreibe jetzt den heutigen Lernabsatz.")

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": "\n\n".join(user_parts)},
    ]


def generate_lesson(messages: list) -> str:

    # select random OPENROUTER_MODEL
    import random
    models = OPENROUTER_MODELS_TEXT_AVAILABLE
    selected_model = random.choice(models) 
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "German Language Learner",
    }
    payload = {
        "model": selected_model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 600,
    }
    with httpx.Client(timeout=30) as client:
        response = client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def make_summary_fn() -> Callable[[str], str]:
    def summarise(prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        return generate_lesson(messages)
    return summarise 



