#!/usr/bin/env python3
"""
Get SERP competitors for content length comparison
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv('data_sources/config/.env')

# Add data_sources to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_sources'))

from modules.dataforseo import DataForSEO
from modules.content_length_comparator import ContentLengthComparator

def get_competitors(keyword, your_word_count):
    """Get SERP competitors and compare content length"""

    print(f"Fetching SERP data for: {keyword}")
    print()

    # Initialize DataForSEO
    dfs = DataForSEO()

    # Get SERP results
    try:
        # Get ranking data
        rankings = dfs.get_rankings(
            domain="careerplanb.co",
            keywords=[keyword],
            location_code=2356  # India
        )

        if rankings:
            print(f"Your Position: #{rankings[0].get('position', 'Not in top 100')}")
            print()
    except Exception as e:
        print(f"Could not get ranking: {e}")
        print()

    # Get top organic results
    try:
        # Use SERP API to get top results
        import requests
        from dotenv import load_dotenv

        load_dotenv('data_sources/config/.env')

        login = os.getenv('DATAFORSEO_LOGIN')
        password = os.getenv('DATAFORSEO_PASSWORD')

        session = requests.Session()
        session.auth = (login, password)

        endpoint = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"

        data = [{
            "keyword": keyword,
            "location_code": 2356,  # India
            "language_code": "en",
            "device": "desktop",
            "depth": 20
        }]

        response = session.post(endpoint, json=data)
        result = response.json()

        if result.get('status_code') == 20000:
            task = result['tasks'][0]
            if task.get('status_code') == 20000:
                items = task['result'][0].get('items', [])

                # Filter for organic results only
                organic = [
                    item for item in items
                    if item.get('type') == 'organic'
                ]

                print(f"Found {len(organic)} organic results")
                print()

                # Extract URLs for comparison
                serp_results = []
                for i, item in enumerate(organic[:10], 1):
                    serp_results.append({
                        'url': item.get('url', ''),
                        'domain': item.get('domain', ''),
                        'title': item.get('title', '')
                    })
                    print(f"{i}. {item.get('domain', '')} - {item.get('title', '')[:60]}...")

                print()
                print("Analyzing competitor content length...")
                print()

                # Compare content length
                comparator = ContentLengthComparator()
                comparison = comparator.analyze(
                    keyword=keyword,
                    your_word_count=your_word_count,
                    serp_results=serp_results,
                    fetch_content=True
                )

                if 'error' not in comparison:
                    stats = comparison['statistics']
                    rec = comparison['recommendation']

                    print("COMPETITOR CONTENT LENGTH ANALYSIS")
                    print("=" * 60)
                    print(f"Your Word Count: {your_word_count}")
                    print()
                    print(f"Competitor Statistics:")
                    print(f"  Minimum: {stats['min']} words")
                    print(f"  Median: {stats['median']} words")
                    print(f"  Average: {stats['mean']} words")
                    print(f"  75th Percentile: {stats['percentile_75']} words")
                    print(f"  Maximum: {stats['max']} words")
                    print()
                    print(f"Recommendation:")
                    print(f"  Minimum Length: {rec['recommended_min']} words")
                    print(f"  Optimal Length: {rec['recommended_optimal']} words")
                    print(f"  Maximum Length: {rec['recommended_max']} words")
                    print()
                    print(f"Your Status: {rec['your_status'].upper()}")
                    print(f"  {rec['message']}")
                    print()

                    if comparison.get('competitive_analysis', {}).get('comparison'):
                        comp = comparison['competitive_analysis']['comparison']
                        print(f"Competition Analysis:")
                        print(f"  You're longer than {comp['shorter_than_you']} competitors")
                        print(f"  You're shorter than {comp['longer_than_you']} competitors")
                        print(f"  Percentile: {comp['percentile']}th")
                        print()

                    return comparison
                else:
                    print(f"Error: {comparison.get('error')}")
                    return None

        return None

    except Exception as e:
        print(f"Error fetching SERP data: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = get_competitors(
        keyword="IIIT Hyderabad vs IIT Hyderabad",
        your_word_count=645
    )

    if result:
        # Save to file
        import json
        with open('output/serp-comparison.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("✅ Results saved to: output/serp-comparison.json")
