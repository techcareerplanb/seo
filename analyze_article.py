#!/usr/bin/env python3
"""
Comprehensive Article Analysis
Analyzes an existing article using all SEO analysis modules
"""

import sys
import os
import json
from datetime import datetime

# Add data_sources to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_sources'))

from modules.search_intent_analyzer import SearchIntentAnalyzer
from modules.keyword_analyzer import KeywordAnalyzer
from modules.readability_scorer import ReadabilityScorer
from modules.seo_quality_rater import SEOQualityRater

def analyze_article(
    content: str,
    primary_keyword: str,
    secondary_keywords: list = None,
    url: str = None
):
    """Run comprehensive analysis on article"""

    print("=" * 70)
    print("COMPREHENSIVE ARTICLE ANALYSIS")
    print("=" * 70)
    print()

    results = {
        'url': url,
        'analyzed_at': datetime.now().isoformat(),
        'word_count': len(content.split()),
        'primary_keyword': primary_keyword
    }

    # 1. Search Intent Analysis
    print("1. SEARCH INTENT ANALYSIS")
    print("-" * 70)
    intent_analyzer = SearchIntentAnalyzer()
    intent_result = intent_analyzer.analyze(primary_keyword)

    print(f"Keyword: {intent_result['keyword']}")
    print(f"Primary Intent: {intent_result['primary_intent'].upper()}")
    print(f"Confidence: {intent_result['confidence'][intent_result['primary_intent']]:.1f}%")

    if intent_result.get('signals_detected'):
        print("\nSignals Detected:")
        for intent_type, signals in intent_result['signals_detected'].items():
            if signals:
                print(f"  {intent_type.title()}:")
                for signal in signals:
                    print(f"    - {signal}")

    print("\nRecommendations:")
    for rec in intent_result['recommendations'][:3]:
        print(f"  • {rec}")

    results['search_intent'] = intent_result
    print()

    # 2. Keyword Analysis
    print("2. KEYWORD ANALYSIS")
    print("-" * 70)
    keyword_analyzer = KeywordAnalyzer()
    keyword_result = keyword_analyzer.analyze(
        content,
        primary_keyword,
        secondary_keywords or [],
        target_density=1.5
    )

    pk = keyword_result['primary_keyword']
    print(f"Primary Keyword: {pk['keyword']}")
    print(f"Occurrences: {pk['total_occurrences']} (Exact: {pk['exact_matches']})")
    print(f"Density: {pk['density']}% (Target: {pk['target_density']}%)")
    print(f"Status: {pk['density_status'].upper().replace('_', ' ')}")

    print("\nCritical Placements:")
    for key, value in pk['critical_placements'].items():
        status = "✓" if value == True or (isinstance(value, str) and value != "0/0") else "✗"
        print(f"  {status} {key.replace('_', ' ').title()}: {value}")

    print(f"\nKeyword Stuffing Risk: {keyword_result['keyword_stuffing']['risk_level'].upper()}")
    if keyword_result['keyword_stuffing']['warnings']:
        for warning in keyword_result['keyword_stuffing']['warnings']:
            print(f"  ⚠ {warning}")

    if keyword_result.get('topic_clusters', {}).get('clusters_found', 0) > 0:
        print(f"\nTopic Clusters Found: {keyword_result['topic_clusters']['clusters_found']}")
        for cluster in keyword_result['topic_clusters']['clusters'][:3]:
            print(f"  Cluster {cluster['cluster_id']}: {', '.join(cluster['top_terms'][:3])}")

    print("\nTop LSI Keywords:")
    for lsi in keyword_result.get('lsi_keywords', [])[:10]:
        print(f"  • {lsi}")

    if secondary_keywords and keyword_result.get('secondary_keywords'):
        print(f"\nSecondary Keywords Analysis:")
        for i, sk in enumerate(keyword_result['secondary_keywords']):
            kw = secondary_keywords[i] if i < len(secondary_keywords) else 'Unknown'
            occ = sk.get('total_occurrences', 0)
            dens = sk.get('density', 0)
            print(f"  • {kw}: {occ} occurrences ({dens}%)")

    results['keyword_analysis'] = keyword_result
    print()

    # 3. Readability Analysis
    print("3. READABILITY ANALYSIS")
    print("-" * 70)
    readability_scorer = ReadabilityScorer()
    readability_result = readability_scorer.analyze(content)

    metrics = readability_result.get('readability_metrics', {})
    structure = readability_result.get('structure_analysis', {})
    complexity = readability_result.get('complexity_analysis', {})

    print(f"Overall Score: {readability_result.get('overall_score', 0)}/100")
    print(f"Grade: {readability_result.get('grade', 'N/A')}")

    print(f"\nFlesch Reading Ease: {metrics.get('flesch_reading_ease', 0):.1f}")
    print(f"Flesch-Kincaid Grade: {metrics.get('flesch_kincaid_grade', 0):.1f}")

    if structure.get('sentences'):
        print(f"\nSentence Metrics:")
        print(f"  Count: {structure['sentences']['count']}")
        print(f"  Average Length: {structure['sentences']['avg_length']:.1f} words")
        if structure['sentences'].get('max_length'):
            print(f"  Longest: {structure['sentences']['max_length']} words")

    if structure.get('paragraphs'):
        print(f"\nParagraph Metrics:")
        print(f"  Count: {structure['paragraphs']['count']}")
        print(f"  Average Length: {structure['paragraphs']['avg_length']:.1f} words")

    if complexity.get('passive_voice'):
        print(f"\nPassive Voice: {complexity['passive_voice'].get('percentage', 0):.1f}%")

    if readability_result.get('recommendations'):
        print("\nRecommendations:")
        for rec in readability_result['recommendations'][:5]:
            print(f"  • {rec}")

    results['readability'] = readability_result
    print()

    # 4. SEO Quality Rating
    print("4. SEO QUALITY RATING")
    print("-" * 70)
    seo_rater = SEOQualityRater()

    # Prepare meta data (in real scenario, this would be extracted from HTML)
    meta_data = {
        'title': 'IIIT Hyderabad vs IIT Hyderabad: Regional Clash 2025 – Which One Should You Choose?',
        'description': 'Compare IIIT Hyderabad vs IIT Hyderabad 2025 — placements, fees, rankings & research scope. Find which top institute suits you best.',
        'url': url or 'https://careerplanb.co/iiit-hyderabad-vs-iit-hyderabad-2025/'
    }

    seo_result = seo_rater.rate(
        content=content,
        primary_keyword=primary_keyword,
        meta_title=meta_data['title'],
        meta_description=meta_data['description'],
        secondary_keywords=secondary_keywords
    )

    print(f"Overall SEO Score: {seo_result['overall_score']}/100")
    print(f"Grade: {seo_result['grade']}")

    print("\nCategory Scores:")
    for category, score in seo_result['category_scores'].items():
        print(f"  {category.replace('_', ' ').title()}: {score}/100")

    if seo_result.get('suggestions'):
        print("\nSuggestions:")
        for sug in seo_result['suggestions'][:5]:
            print(f"  • {sug}")

    if seo_result.get('warnings'):
        print("\nWarnings:")
        for warning in seo_result['warnings'][:5]:
            print(f"  ⚠ {warning}")

    if seo_result.get('critical_issues'):
        print("\nCritical Issues:")
        for issue in seo_result['critical_issues']:
            print(f"  ✗ {issue}")

    results['seo_quality'] = seo_result
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Word Count: {results['word_count']}")
    print(f"SEO Score: {seo_result['overall_score']}/100 ({seo_result['grade']})")
    print(f"Readability: {readability_result.get('overall_score', 0)}/100 ({readability_result.get('grade', 'N/A')})")
    print(f"Keyword Density: {pk['density']}% ({pk['density_status'].replace('_', ' ').title()})")
    print(f"Search Intent Match: {intent_result['primary_intent'].title()}")
    print()

    return results


if __name__ == "__main__":
    # Read content from temp file
    with open('/tmp/iiit-iit-content.txt', 'r') as f:
        content = f.read()

    # Analyze
    results = analyze_article(
        content=content,
        primary_keyword="IIIT Hyderabad vs IIT Hyderabad",
        secondary_keywords=["NIRF ranking", "placements", "campus infrastructure"],
        url="https://careerplanb.co/iiit-hyderabad-vs-iit-hyderabad-2025/"
    )

    # Save results
    output_file = 'output/article-analysis-results.json'
    os.makedirs('output', exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"✅ Detailed results saved to: {output_file}")
