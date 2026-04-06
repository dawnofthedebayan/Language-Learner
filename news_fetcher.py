import requests
from typing import List, Dict

from config import NEWS_API_KEY, NEWS_BASE_URL, NEWS_MAX_ARTICLES, NEWS_LANGUAGE


def fetch_news(topic: str, max_articles: int = NEWS_MAX_ARTICLES) -> List[Dict]:
    params = {
        "q": topic,
        "language": NEWS_LANGUAGE,
        "pageSize": max_articles,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY,
    }

    response = requests.get(NEWS_BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    articles = response.json().get("articles", [])

    return [
        {
            "title": a.get("title", ""),
            "summary": a.get("description", ""),
            "url": a.get("url", ""),
        }
        for a in articles
        if a.get("title")
    ]


def format_news_context(articles: List[Dict]) -> str:
    if not articles:
        return "Keine aktuellen Nachrichten gefunden."

    lines = []
    for i, article in enumerate(articles, 1):
        lines.append(f"{i}. {article['title']}")
        if article.get("summary"):
            lines.append(f"   {article['summary']}")
    return "\n".join(lines)


def fetch_regional_news(countries: List[str], max_per_region: int = 3, category: List[str] = ["general"]) -> List[Dict]:
    """
    Fetches top headlines for a list of specific countries.
    :param countries: List of 2-letter ISO codes (e.g., ['us', 'de', 'gb'])
    """
    all_articles = []
    
    for country in countries:
        for cat in category:
            params = {
                "country": country,
                "pageSize": max_per_region,
                "apiKey": NEWS_API_KEY,
                "language":"en",
                "category": cat
            }
        
            try:
                response = requests.get(NEWS_BASE_URL, params=params, timeout=10)
                response.raise_for_status()
                articles = response.json().get("articles", [])
                
                for a in articles:
                    if a.get("title"):
                        all_articles.append({
                            "title": f"[{country.upper()}] {a.get('title')}",
                            "summary": a.get("description", ""),
                            "url": a.get("url", ""),
                            "country": country,
                            "category": cat
                        })
            except Exception as e:
                print(f"Error fetching news for {country}: {e}")
            
    return all_articles



    
# example usage
if __name__ == "__main__":

    categories = ["general", "business", "technology", "health", "science", "sports", "en"]
    articles = fetch_regional_news(["us", "gb"], 5, categories) 

    print(articles)
