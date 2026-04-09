from typing import TypedDict, Annotated
import httpx
import time
from langgraph.graph import StateGraph, START, END

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_RETRY_MAX_ATTEMPTS,
    OPENROUTER_RETRY_BASE_DELAY,
    OPENROUTER_INTER_CALL_DELAY
)





def invoke_news_summarising_agent(OPENROUTER_MODEL, json_data_array):
    # Example state: input JSON plus generated text
    class State(TypedDict):
        raw_json: dict
        news_paragraph: str
        vocabulary_sentences: str

    def _invoke_openrouter(system_text: str, user_text: str, max_retries: int = OPENROUTER_RETRY_MAX_ATTEMPTS) -> str:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com",
            "X-Title": "German Language Learner",
        }
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_text},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=60) as client:
                    response = client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = OPENROUTER_RETRY_BASE_DELAY * (2 ** attempt)
                        print(f"[OpenRouter] Rate limit hit. Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"[OpenRouter] Max retries reached. Returning fallback.")
                        return "Zusammenfassung konnte aufgrund von API-Limits nicht erstellt werden."
                else:
                    raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = OPENROUTER_RETRY_BASE_DELAY * (2 ** attempt)
                    print(f"[OpenRouter] Error: {e}. Retrying in {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    raise

            data = response.json()
            choices = data.get("choices") or []
            if not choices:
                return "Keine Zusammenfassung verfügbar."

            message = (choices[0] or {}).get("message") or {}
            content = message.get("content")

            if isinstance(content, str):
                text = content.strip()
            elif isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(item.get("text", ""))
                text = "\n".join(parts).strip()
            else:
                text = ""

            if text:
                return text

            fallback_text = (choices[0] or {}).get("text")
            if isinstance(fallback_text, str) and fallback_text.strip():
                return fallback_text.strip()

            return "Keine Zusammenfassung verfügbar."

    def summarize_json(state: State) -> State:
        raw = state["raw_json"]

        sys_msg = """
                ### **Rolle**
                Du bist ein erfahrener Nachrichten-Analyst. Deine Aufgabe ist es, strukturierte Nachrichtendaten zu verarbeiten und eine professionelle Zusammenfassung in deutscher Sprache zu erstellen.

                ### **Aufgabenstellung**
                1. **Kategorisierte Zusammenfassung:** Gruppiere die Artikel nach Kategorien (z. B. Politik, Technologie, Wissenschaft). Fasse die wichtigsten Ereignisse jeder Kategorie in prägnanten Stichpunkten zusammen. Doppelte Meldungen sind zu konsolidieren.
                2. **Integrierter Überblick:** Erstelle am Ende einen einzigen, gut lesbaren Absatz auf Deutsch, der die wichtigsten Themen aller Kategorien miteinander verknüpft. Ziel ist es, dem Leser ein Gefühl für die aktuelle "Weltlage" zu vermitteln, anstatt nur Fakten zu wiederholen.

                ### **Formatvorgaben**
                * Verwende **Fettdruck** für wichtige Begriffe, Namen oder Ereignisse.
                * Nutze klare Hierarchien mit Überschriften (## oder ###).
                * Die Sprache ist **Deutsch**. Englische Begriffe nur bei Eigennamen (z. B. "OpenAI") beibehalten.

                ### **Struktur des Outputs**
                ---
                ### **[Name der Kategorie]**
                * **[Thema]:** [Kurze, prägnante Zusammenfassung der Fakten]

                ### **Der Überblick**
                [Ein zusammenhängender, leicht verständlicher Absatz, der die Kernbotschaften aller Kategorien zu einem Gesamtbild vereint.]
                ---

                ### **Einschränkungen**
                * Vermeide bloße Auflistungen im "Überblick".
                * Übersetze englische Fachbegriffe in gängiges Deutsch.
                * Fasse dich kurz, aber verliere keine kritischen Details.
            """
        user_msg = f"Here ist mein JSON data:\n{raw}"

        generated = _invoke_openrouter(sys_msg, user_msg)
        print(f"[News] Summary generated. Waiting {OPENROUTER_INTER_CALL_DELAY}s before vocabulary generation...")
        time.sleep(OPENROUTER_INTER_CALL_DELAY)
        return {
            **state,
            "news_paragraph": generated
        }

    def vocabulary_sentence_helper(state: State) -> State:
        # Use the summary generated in the previous step
        german_text = state["news_paragraph"]

        teacher_sys_msg = """
        ### Rolle
        Du bist ein engagierter Deutschlehrer. 
        
        ### Aufgabe
        Analysiere den vorliegenden Text und wähle die 5 anspruchsvollsten Wörter aus (Niveaustufe B2-C1).
        Erstelle für jedes Wort einen Eintrag mit:
        1. **Übersetzung:** Englische Bedeutung.
        2. **Grammatik:** - Bei Verben: Präsens, Präteritum, Perfekt (z.B. machen -> macht, machte, hat gemacht).
        - Bei Nomen: Genus und Plural (z.B. der Tisch, "-e").
        3. **Beispielsatz:** Ein Satz im Kontext der Nachrichten.

        ### Format
        Gib die Antwort als Liste von Sätzen zurück, die jeweils ein Wort erklären.
        """
        
        user_msg = f"Hier ist die Zusammenfassung für die Analyse:\n{german_text}"
        
        # Invoke the LLM
        response = _invoke_openrouter(teacher_sys_msg, user_msg)
        
        # Split by double newlines or similar to get a list of vocabulary entries
        
        return {
            **state,
            "vocabulary_sentences": response
        }



    # Build the graph
    workflow = StateGraph(State)

    workflow.add_node("summarize", summarize_json)
    workflow.add_edge(START, "summarize")
    workflow.add_node("teacher", vocabulary_sentence_helper) 
    workflow.add_edge("summarize", "teacher")
    workflow.add_edge("teacher", END)

    app = workflow.compile()

    # Example usage
    input_json = json_data_array

    result = app.invoke({"raw_json": input_json})

    return result



