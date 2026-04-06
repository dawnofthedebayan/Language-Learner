import json
import os
import datetime
from typing import Dict, Callable

from config import MEMORY_PATH, MEMORY_MAX_CHARS, MEMORY_KEEP_RECENT


def load_memory(path: str = MEMORY_PATH) -> Dict:
    if not os.path.exists(path):
        return {"summary": "", "messages": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def append_to_memory(memory: Dict, role: str, content: str) -> Dict:
    memory["messages"].append(
        {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
    )
    return memory


def _total_chars(memory: Dict) -> int:
    total = len(memory.get("summary", ""))
    for m in memory.get("messages", []):
        total += len(m.get("content", ""))
    return total


def summarise_memory(memory: Dict, llm_fn: Callable[[str], str]) -> Dict:
    if _total_chars(memory) <= MEMORY_MAX_CHARS:
        return memory

    messages = memory.get("messages", [])
    older = messages[:-MEMORY_KEEP_RECENT]
    recent = messages[-MEMORY_KEEP_RECENT:]

    if not older:
        return memory

    older_text = "\n".join(
        f"[{m['timestamp']}] {m['role'].upper()}: {m['content']}" for m in older
    )
    existing_summary = memory.get("summary", "")
    prompt = (
        "Summarise the following conversation history concisely in English, "
        "preserving key vocabulary, topics covered, and user progress. "
        "Existing summary (prepend if present):\n"
        f"{existing_summary}\n\nNew messages to incorporate:\n{older_text}"
    )
    new_summary = llm_fn(prompt)
    memory["summary"] = new_summary
    memory["messages"] = recent
    return memory


def save_memory(memory: Dict, path: str = MEMORY_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
