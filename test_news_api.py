#!/usr/bin/env python3
"""
Test script for News API integration
Tests various endpoints and validates responses
"""

import requests
import json
from datetime import datetime
from config import NEWS_API_KEY, NEWS_BASE_URL


def test_api_key():
    """Test if API key is configured"""
    print("=" * 60)
    print("TEST 1: API Key Configuration")
    print("=" * 60)
    
    if not NEWS_API_KEY:
        print("❌ FAILED: NEWS_API_KEY is not set in .env file")
        return False
    
    print(f"✅ PASSED: API key is configured (length: {len(NEWS_API_KEY)})")
    print(f"   Key preview: {NEWS_API_KEY[:8]}...{NEWS_API_KEY[-4:]}")
    return True


def test_api_status():
    """Test if News API is reachable"""
    print("\n" + "=" * 60)
    print("TEST 2: API Status Check")
    print("=" * 60)
    
    try:
        # Simple test with minimal parameters
        params = {
            "q": "test",
            "pageSize": 1,
            "apiKey": NEWS_API_KEY
        }
        
        response = requests.get(NEWS_BASE_URL, params=params, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            print("✅ PASSED: API is reachable and responding")
            return True
        elif response.status_code == 401:
            print("❌ FAILED: Invalid API key (401 Unauthorized)")
            return False
        elif response.status_code == 429:
            print("⚠️  WARNING: Rate limit exceeded (429)")
            return False
        else:
            print(f"❌ FAILED: Unexpected status code {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ FAILED: Request timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ FAILED: Request error - {e}")
        return False


def test_top_headlines():
    """Test fetching top headlines"""
    print("\n" + "=" * 60)
    print("TEST 3: Top Headlines (US)")
    print("=" * 60)
    
    try:
        params = {
            "country": "us",
            "pageSize": 5,
            "apiKey": NEWS_API_KEY,
            "category": "general"
        }
        
        response = requests.get(NEWS_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        
        print(f"   Total Results: {data.get('totalResults', 0)}")
        print(f"   Articles Returned: {len(articles)}")
        
        if articles:
            print("\n   Sample Headlines:")
            for i, article in enumerate(articles[:3], 1):
                title = article.get("title", "No title")
                source = article.get("source", {}).get("name", "Unknown")
                print(f"   {i}. [{source}] {title[:70]}...")
            
            print("\n✅ PASSED: Successfully fetched top headlines")
            return True
        else:
            print("⚠️  WARNING: No articles returned")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_category_news():
    """Test fetching news by category"""
    print("\n" + "=" * 60)
    print("TEST 4: Category-based News Fetching")
    print("=" * 60)
    
    categories = ["technology", "science", "health", "business"]
    results = {}
    
    for category in categories:
        try:
            params = {
                "country": "us",
                "category": category,
                "pageSize": 3,
                "apiKey": NEWS_API_KEY
            }
            
            response = requests.get(NEWS_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            article_count = len(data.get("articles", []))
            results[category] = article_count
            
            print(f"   {category.capitalize()}: {article_count} articles")
            
        except Exception as e:
            print(f"   {category.capitalize()}: ❌ Error - {e}")
            results[category] = 0
    
    total = sum(results.values())
    if total > 0:
        print(f"\n✅ PASSED: Fetched {total} articles across {len(categories)} categories")
        return True
    else:
        print("\n❌ FAILED: No articles fetched from any category")
        return False


def test_multi_country():
    """Test fetching news from multiple countries"""
    print("\n" + "=" * 60)
    print("TEST 5: Multi-Country News Fetching")
    print("=" * 60)
    
    countries = ["us", "gb", "de"]
    results = {}
    
    for country in countries:
        try:
            params = {
                "country": country,
                "pageSize": 3,
                "apiKey": NEWS_API_KEY
            }
            
            response = requests.get(NEWS_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            article_count = len(data.get("articles", []))
            results[country] = article_count
            
            print(f"   {country.upper()}: {article_count} articles")
            
        except Exception as e:
            print(f"   {country.upper()}: ❌ Error - {e}")
            results[country] = 0
    
    total = sum(results.values())
    if total > 0:
        print(f"\n✅ PASSED: Fetched {total} articles from {len(countries)} countries")
        return True
    else:
        print("\n❌ FAILED: No articles fetched from any country")
        return False


def test_article_structure():
    """Test article data structure"""
    print("\n" + "=" * 60)
    print("TEST 6: Article Data Structure Validation")
    print("=" * 60)
    
    try:
        params = {
            "country": "us",
            "pageSize": 1,
            "apiKey": NEWS_API_KEY
        }
        
        response = requests.get(NEWS_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        
        if not articles:
            print("⚠️  WARNING: No articles to validate")
            return False
        
        article = articles[0]
        required_fields = ["title", "description", "url", "publishedAt", "source"]
        
        print("   Checking required fields:")
        all_present = True
        for field in required_fields:
            present = field in article and article[field] is not None
            status = "✓" if present else "✗"
            print(f"   {status} {field}: {type(article.get(field)).__name__ if present else 'missing'}")
            if not present:
                all_present = False
        
        if all_present:
            print("\n✅ PASSED: All required fields present")
            print("\n   Sample Article:")
            print(f"   Title: {article.get('title', '')[:60]}...")
            print(f"   Source: {article.get('source', {}).get('name', 'Unknown')}")
            print(f"   Published: {article.get('publishedAt', 'Unknown')}")
            return True
        else:
            print("\n⚠️  WARNING: Some fields missing")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_rate_limits():
    """Test rate limit handling"""
    print("\n" + "=" * 60)
    print("TEST 7: Rate Limit Check")
    print("=" * 60)
    
    print("   Making 3 rapid requests to check rate limiting...")
    
    for i in range(3):
        try:
            params = {
                "country": "us",
                "pageSize": 1,
                "apiKey": NEWS_API_KEY
            }
            
            response = requests.get(NEWS_BASE_URL, params=params, timeout=10)
            
            if response.status_code == 429:
                print(f"   Request {i+1}: ⚠️  Rate limited")
                print("\n⚠️  WARNING: Rate limit hit - consider adding delays between requests")
                return False
            elif response.status_code == 200:
                print(f"   Request {i+1}: ✓ Success")
            else:
                print(f"   Request {i+1}: Status {response.status_code}")
                
        except Exception as e:
            print(f"   Request {i+1}: ❌ Error - {e}")
            return False
    
    print("\n✅ PASSED: No rate limiting detected (within limits)")
    return True


def run_all_tests():
    """Run all tests and provide summary"""
    print("\n" + "=" * 60)
    print("NEWS API TEST SUITE")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("API Key Configuration", test_api_key),
        ("API Status", test_api_status),
        ("Top Headlines", test_top_headlines),
        ("Category News", test_category_news),
        ("Multi-Country", test_multi_country),
        ("Article Structure", test_article_structure),
        ("Rate Limits", test_rate_limits),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
