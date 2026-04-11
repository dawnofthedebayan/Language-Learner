# 🇩🇪 German Language Learner – Codebase Flowchart

## Overview

Two entry points exist: **manual** (`python main.py`) and **automated** (GitHub Actions cron at 07:00 UTC daily). Both converge on `main.py`.

---

## 1. Top-Level Execution Flow

```mermaid
flowchart TD
    A([🕖 GitHub Actions Cron\n07:00 UTC daily]) --> B[github_action_runner.py\nsetup_env + run]
    C([👨‍💻 Manual\npython main.py]) --> D

    B --> D[main.py · main]

    D --> E[topics.py\nload_topics · pick_topic_of_day\n→ random topic from topics.json]
    E --> F[news_fetcher.py\nfetch_regional_news\n→ US headlines across 7 categories]
    F --> G{Articles fetched?}
    G -- Yes --> H[Strip URLs from articles]
    G -- No / Error --> I[articles = empty list]
    I --> H

    H --> J[Pick random LLM model\nfrom OPENROUTER_MODELS_TEXT_AVAILABLE]
    J --> K[news_summarising_agent.py\ninvoke_news_summarising_agent]
    K --> L[Wait OPENROUTER_AGENT_DELAY\n15s]
    L --> M[Query DB: previous 7-day\ndiscussions for this topic]
    M --> N[topic_discussion_agent.py\ninvoke_topic_discussion_agent]
    N --> O[SQLite · add_lesson_to_database\nnews record + topic record]
    O --> P([End])
```

---

## 2. News Summarising Agent (LangGraph)

Called from `main.py` with the scraped articles JSON.

```mermaid
flowchart TD
    START([Input:\nraw articles JSON]) --> A

    subgraph LangGraph Workflow
        A[Node: summarize_json\nSend articles to LLM\nSystem: Nachrichten-Analyst\n→ categorised German news summary]
        A --> SLEEP[Sleep OPENROUTER_INTER_CALL_DELAY\n8s between nodes]
        SLEEP --> B[Node: vocabulary_sentence_helper\nSend summary to LLM\nSystem: Deutschlehrer\n→ 5 B2-C1 vocab words with grammar]
    end

    B --> END([Output State:\nnews_paragraph\nvocabulary_sentences])
```

---

## 3. Topic Discussion Agent (LangGraph)

Called from `main.py` with today's topic and past 7-day discussion history.

```mermaid
flowchart TD
    START([Input:\ntopic + old_topic_discussion]) --> A

    subgraph LangGraph Workflow
        A[Node: topic_discussion_node\nSend topic to LLM\nSystem: Hilfreicher Assistent\n→ structured German essay\nEinleitung · Hauptteil · Schluss]
        A --> SLEEP[Sleep OPENROUTER_INTER_CALL_DELAY\n8s between nodes]
        SLEEP --> B[Node: vocabulary_sentence_helper\nSend essay to LLM\nSystem: Deutschlehrer\n→ 5 B2-C1 vocab words with grammar]
    end

    B --> END([Output State:\ntopic_discussion\nvocabulary_sentences])
```

---

## 4. OpenRouter API Call with Retry Logic

Used inside both agents — every single LLM call goes through this.

```mermaid
flowchart TD
    A([Call _invoke_openrouter\nsystem_text + user_text]) --> B[Build headers + payload\nPOST openrouter.ai/chat/completions]
    B --> C{HTTP response}

    C -- 200 OK --> D[Parse response JSON\nextract choices[0].message.content]
    D --> E{Content present?}
    E -- Yes --> F([Return text])
    E -- No --> G([Return fallback string])

    C -- 429 Rate Limit --> H{attempt < max_retries?}
    H -- Yes --> I[Sleep BASE_DELAY × 2^attempt\n3s · 6s · 12s · 24s · 48s · 96s]
    I --> B
    H -- No --> J([Return fallback string])

    C -- Other HTTP Error --> K([Raise exception])
    C -- Network Error --> H
```

---

## 5. News Fetcher

```mermaid
flowchart TD
    A([fetch_regional_news\ncountries + categories]) --> B

    B[For each country × category\nGET newsapi.org/v2/top-headlines] --> C{Success?}
    C -- Yes --> D[Extract title, summary, url\ncountry, category tags]
    C -- Error --> E[Print error, skip]
    D --> F([Return all_articles list])
    E --> F
```

---

## 6. SQLite Database

All lessons are persisted in `language_learner.db`.

```mermaid
flowchart TD
    A([add_lesson_to_database]) --> B[(SQLite\nlanguage_learner.db\ntable: lessons)]
    C([get_previous_topics\nlast N days]) --> B
    B --> D([export_lessons.py\nSELECT * ORDER BY date DESC])
    D --> E[docs/lessons.json]
    E --> F([GitHub Pages Website\ndocs/index.html + app.js])
```

---

## 7. GitHub Actions CI/CD

```mermaid
flowchart TD
    T([⏰ Cron 07:00 UTC\nor manual dispatch]) --> A[Checkout repo]
    A --> B[Install requirements.txt]
    B --> C[python github_action_runner.py\n→ runs main.py]
    C --> D[python export_lessons.py\n→ writes docs/lessons.json]
    D --> E[git commit\nlanguage_learner.db + docs/lessons.json]
    E --> F[Deploy docs/ → gh-pages branch\nGitHub Pages]

    P([Push to main\ndocs/ changed]) --> G[deploy-site.yml\nDeploy docs/ → gh-pages]
```

---

## 8. Website Frontend (`docs/`)

```mermaid
flowchart TD
    A([User opens GitHub Pages site]) --> B[index.html loads app.js]
    B --> C[fetch lessons.json]
    C --> D{Parse OK?}
    D -- Yes --> E[populateFilters\ntopics · models · dates]
    E --> F[renderLessons\nCreate lesson cards]
    F --> G{User clicks card}
    G -- Yes --> H[openModal\nRender markdown content\n+ vocabulary via marked.js]
    D -- No / null content --> I[Show error or fallback text]
```

---

## 9. Config & Module Dependency Map

```mermaid
flowchart LR
    config.py --> main.py
    config.py --> news_fetcher.py
    config.py --> news_summarising_agent.py
    config.py --> topic_discussion_agent.py
    config.py --> audio_handler.py
    config.py --> memory_manager.py
    config.py --> llm_agent.py
    config.py --> topics.py

    main.py --> news_fetcher.py
    main.py --> news_summarising_agent.py
    main.py --> topic_discussion_agent.py
    main.py --> topics.py
    main.py --> audio_handler.py

    github_action_runner.py --> main.py
    export_lessons.py --> language_learner.db[(SQLite DB)]
    export_lessons.py --> docs/lessons.json
```

---

## 10. Data Flow Summary

```
NewsAPI ──────────────────────────────────────────────────────┐
                                                              ↓
topics.json → pick random topic                         raw articles JSON
                    ↓                                         ↓
             main.py ←───────────── random LLM model ────────┘
                    │
          ┌─────────┴──────────┐
          ↓                    ↓
  news_summarising        topic_discussion
     _agent.py               _agent.py
          │                    │
     [LangGraph]           [LangGraph]
    summarize →            discuss topic →
    vocabulary             vocabulary
          │                    │
          └─────────┬──────────┘
                    ↓
          SQLite language_learner.db
                    ↓
          export_lessons.py
                    ↓
          docs/lessons.json
                    ↓
          GitHub Pages Website
```
