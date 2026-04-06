from typing import TypedDict, Annotated
import httpx
from langgraph.graph import StateGraph, START, END

from config import OPENROUTER_API_KEY


def invoke_topic_discussion_agent(OPENROUTER_MODEL, topic, old_topic_discussion):

    # Example state: input JSON plus generated text
    class State(TypedDict):
        topic: str
        old_topic_discussion: str
        topic_discussion: str
        vocabulary_sentences: str


    
    def _invoke_openrouter(system_text: str, user_text: str) -> str:
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
        }
        with httpx.Client(timeout=60.0) as client:
            resp = client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    def topic_discussion_node(state: State) -> State:
        # System prompt in German with structure and "do not repeat" instructions
        system_text = (
            "Du bist ein hilfreicher Assistent, der Themen auf Deutsch bespricht. "
            "Deine Antwort muss zwingend so strukturiert sein: Eine Einleitung, ein Hauptteil und ein Schluss. "
            "WICHTIG: Die bereitgestellten Informationen unter 'Alte Diskussion' dienen nur als Kontext, "
            "was bereits besprochen wurde. Erwähne diese alten Inhalte nicht und wiederhole sie nicht. "
            "Konzentriere dich nur auf das neue Thema."
        )
        
        # User text clearly separating the new topic from the history
        user_text = (
            f"Neues Thema: {state['topic']}\n\n"
            f"Alte Diskussion (Nicht erwähnen!): {state['old_topic_discussion']}"
        )
        
        topic_discussion = _invoke_openrouter(system_text, user_text)
        
        return {
            **state,
            "topic_discussion": topic_discussion
        }
        
    
    def vocabulary_sentence_helper(state: State) -> State:
        # Use the summary generated in the previous step
        german_text = state["topic_discussion"]

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

    # llm graph 
    workflow = StateGraph(State)

    workflow.add_node("topic_discussion", topic_discussion_node) 
    workflow.add_node("vocabulary_sentence", vocabulary_sentence_helper)
    workflow.add_edge(START, "topic_discussion")
    workflow.add_edge("topic_discussion", "vocabulary_sentence")
    workflow.add_edge("vocabulary_sentence", END)

    app = workflow.compile()

    # Example usage
    input_state = {
        "topic": topic,
        "old_topic_discussion": old_topic_discussion
    }

    result = app.invoke(input_state)

    return result
    

# test 
#if __name__ == "__main__":

#    model = "google/gemini-2.5-flash"
#    result = invoke_topic_discussion_agent(model, "Klimawandel und Umweltpolitik", " Klimawandel ist ein wichtiges Thema in der heutigen Welt.")
#    print(result)

     

    

