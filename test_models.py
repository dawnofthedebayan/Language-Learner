#!/usr/bin/env python3
"""Test script to verify all OpenRouter models are working"""

import httpx
import time
from config import OPENROUTER_API_KEY, OPENROUTER_MODELS_TEXT_AVAILABLE

def test_model(model_name: str) -> dict:
    """Test a single model with a simple prompt"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "German Language Learner - Model Test",
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "Sag 'Hallo' auf Deutsch."}
        ],
        "max_tokens": 50,
    }
    
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract response
            content = data["choices"][0]["message"]["content"]
            
            return {
                "status": "✅ SUCCESS",
                "model": model_name,
                "response": content.strip()[:100],  # First 100 chars
                "error": None
            }
            
    except httpx.HTTPStatusError as e:
        return {
            "status": "❌ FAILED",
            "model": model_name,
            "response": None,
            "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"
        }
    except Exception as e:
        return {
            "status": "❌ FAILED",
            "model": model_name,
            "response": None,
            "error": str(e)[:200]
        }

def main():
    print("=" * 80)
    print("Testing OpenRouter Models")
    print("=" * 80)
    print(f"\nTesting {len(OPENROUTER_MODELS_TEXT_AVAILABLE)} models...\n")
    
    results = []
    
    for i, model in enumerate(OPENROUTER_MODELS_TEXT_AVAILABLE, 1):
        print(f"[{i}/{len(OPENROUTER_MODELS_TEXT_AVAILABLE)}] Testing: {model}")
        result = test_model(model)
        results.append(result)
        
        print(f"    {result['status']}")
        if result['response']:
            print(f"    Response: {result['response']}")
        if result['error']:
            print(f"    Error: {result['error']}")
        print()
        
        # Small delay to avoid rate limits
        if i < len(OPENROUTER_MODELS_TEXT_AVAILABLE):
            time.sleep(2)
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r['status'] == "✅ SUCCESS")
    failed_count = len(results) - success_count
    
    print(f"\n✅ Successful: {success_count}/{len(results)}")
    print(f"❌ Failed: {failed_count}/{len(results)}")
    
    if failed_count > 0:
        print("\nFailed models:")
        for r in results:
            if r['status'] == "❌ FAILED":
                print(f"  - {r['model']}")
                print(f"    {r['error']}")
    
    print("\n" + "=" * 80)
    
    # Return exit code
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit(main())
