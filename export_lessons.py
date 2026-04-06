import sqlite3
import json
import os

def export_lessons_to_json():
    db_path = os.path.join(os.path.dirname(__file__), "language_learner.db")
    output_path = os.path.join(os.path.dirname(__file__), "docs", "lessons.json")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, type, topic, content, vocabulary, language_model
        FROM lessons
        ORDER BY date DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    lessons = []
    for row in rows:
        lessons.append({
            "date": row[0],
            "type": row[1],
            "topic": row[2],
            "content": row[3],
            "vocabulary": row[4],
            "model": row[5]
        })
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2)
    
    print(f"Exported {len(lessons)} lessons to {output_path}")

if __name__ == "__main__":
    export_lessons_to_json()
