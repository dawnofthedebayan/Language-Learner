import sys
import time
from datetime import datetime
from config import (
    MEMORY_PATH,
    TOPICS_PATH,
    AUDIO_BACKEND,
    OPENROUTER_MODELS_TEXT_AVAILABLE,
    OPENROUTER_AGENT_DELAY
)
from topics import load_topics, pick_topic_of_day
from news_fetcher import fetch_regional_news
from audio_handler import speak
from news_summarising_agent import invoke_news_summarising_agent
from topic_discussion_agent import invoke_topic_discussion_agent 

#sql database connection
import sqlite3
import random

def sql_connection():
    """
    Creates a connection to the SQLite database if it doesn't exist.
    """
    conn = sqlite3.connect("language_learner.db") 
    # create a table with schema as date, type, content, language_model if it does not exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            date TEXT,
            type TEXT,
            topic TEXT,
            content TEXT,
            vocabulary TEXT,
            language_model TEXT
        )
    """)
    return conn

def get_previous_topics(days: int, type: str, topic: str) -> list:
    """
    Gets the previous topics from the SQLite database.
    """
    conn = sql_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content FROM lessons WHERE date >= date('now', '-{} days') AND type = ? AND topic = ?
    """.format(days), (type, topic))
    topics = cursor.fetchall()
    conn.close()
    return topics


def get_all_lessons():
    """
    Gets all lessons from the SQLite database.
    """
    conn = sql_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM lessons
    """)
    lessons = cursor.fetchall()
    conn.close()
    return lessons

def add_lesson_to_database(date: str, type: str, topic: str, content: str,vocabulary:str, language_model: str) -> None:
    """
    Adds a lesson to the SQLite database.
    """
    conn = sql_connection()
    conn.execute("""
        INSERT INTO lessons (date, type, topic, content, vocabulary, language_model)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, type, topic, content, vocabulary, language_model))
    conn.commit()
    conn.close()

def main() -> None:
    print("=== German Language Learner – Daily Lesson ===\n")

    # sql database connection
    llm_model = random.choice(OPENROUTER_MODELS_TEXT_AVAILABLE)
    
    topics = load_topics(TOPICS_PATH)
    topic = pick_topic_of_day(topics)
    print(f"[Topic] {topic}")

    try:
        categories = ["general", "business", "technology", "health", "science", "sports", "entertainment"]
        articles = fetch_regional_news(["us"], category=categories)
        print(f"[News] Fetched {len(articles)} articles")
    except Exception as e:
        print(f"[News] Could not fetch news: {e}")
        articles = []


    # invoke news summarising agent 
    # remove the urls from articles
    article_copy = articles.copy() 
    for article in article_copy:
        del article["url"]
    
    print(f"[LLM] Using model: {llm_model}")
    print("[News] Generating news summary...")
    result = invoke_news_summarising_agent(llm_model, article_copy)
    # show news summary 
    print(result["news_paragraph"])
    print(f"[News] Summary complete. Waiting {OPENROUTER_AGENT_DELAY}s before topic agent...")
    time.sleep(OPENROUTER_AGENT_DELAY)  # Wait 5 seconds to avoid rate limits
    # add to this result today's date
    
    date = datetime.now().strftime("%Y-%m-%d") 
    result["date"] = date

    # add to database
    add_lesson_to_database(date, "news", "NA", result["news_paragraph"], result["vocabulary_sentences"], llm_model)

    # get previous topic over the past 7 days 
    previous_topics = get_previous_topics(7, "topic", topic) 

    # format previous topics into topic and content 
    previous_topics_content = ""
    for row in previous_topics:
        previous_topics_content += f"Topic: {topic}\n"
        previous_topics_content += f"Content: {row[0]}\n"
    
    print("Previous topics:")
    print(previous_topics_content)


    # topic agent
    print("[Topic] Generating topic discussion...")
    topic_result = invoke_topic_discussion_agent(llm_model, topic, previous_topics_content)
    print("[Topic] Discussion complete.")

    # add topic result to database
    add_lesson_to_database(date, "topic", topic, topic_result["topic_discussion"], topic_result["vocabulary_sentences"], llm_model)
    

if __name__ == "__main__":
    main()
