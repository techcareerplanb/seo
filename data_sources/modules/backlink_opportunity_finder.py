#!/usr/bin/env python3
"""
Backlink Opportunity Finder
Finds guest posting and "write for us" opportunities for link building
"""

import os
import re
from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment
load_dotenv('data_sources/config/.env')


class BacklinkOpportunityFinder:
    """Find guest posting opportunities for backlink building"""

    def __init__(self):
        self.login = os.getenv('DATAFORSEO_LOGIN')
        self.password = os.getenv('DATAFORSEO_PASSWORD')

        if not self.login or not self.password:
            raise ValueError("DataForSEO credentials not found in .env")

        self.base_url = "https://api.dataforseo.com/v3"
        self.session = requests.Session()
        self.session.auth = (self.login, self.password)

    def find_opportunities(
        self,
        keyword: str,
        location_code: int = 2356,  # India
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find guest posting opportunities for a keyword

        Args:
            keyword: Your niche keyword (e.g., "career counselling")
            location_code: Google location code (2356 = India, 2840 = USA)
            limit: Maximum results to return

        Returns:
            List of opportunities with details
        """
        opportunities = []

        # Search patterns to find "write for us" pages
        search_queries = [
            f'{keyword} inurl:write-for-us',
            f'{keyword} "write for us"',
            f'{keyword} "guest post"',
            f'{keyword} "contribute"',
            f'{keyword} "submit article"',
        ]

        print(f"Searching for backlink opportunities for: {keyword}")
        print(f"Location: {location_code}")
        print()

        for query in search_queries:
            print(f"Searching: {query}")
            results = self._search_serp(query, location_code, limit=20)

            for result in results:
                # Extract opportunity details
                opp = self._extract_opportunity(result, keyword)
                if opp and opp not in opportunities:
                    opportunities.append(opp)

            print(f"  Found {len(results)} results")

        # Deduplicate by domain
        seen_domains = set()
        unique_opps = []
        for opp in opportunities:
            domain = opp['domain']
            if domain not in seen_domains:
                seen_domains.add(domain)
                unique_opps.append(opp)

        print()
        print(f"Total unique opportunities found: {len(unique_opps)}")

        # Sort by opportunity score
        unique_opps.sort(key=lambda x: x.get('score', 0), reverse=True)

        return unique_opps[:limit]

    def _search_serp(
        self,
        query: str,
        location_code: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search Google SERP via DataForSEO"""

        endpoint = f"{self.base_url}/serp/google/organic/live/advanced"

        data = [{
            "keyword": query,
            "location_code": location_code,
            "language_code": "en",
            "device": "desktop",
            "os": "windows",
            "depth": limit
        }]

        try:
            response = self.session.post(endpoint, json=data)
            response.raise_for_status()

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

                    return organic

            return []

        except Exception as e:
            print(f"Error searching SERP: {e}")
            return []

    def _extract_opportunity(
        self,
        serp_result: Dict[str, Any],
        keyword: str
    ) -> Dict[str, Any]:
        """Extract opportunity details from SERP result"""

        url = serp_result.get('url', '')
        title = serp_result.get('title', '')
        description = serp_result.get('description', '')
        domain = serp_result.get('domain', '')

        # Skip non-relevant results
        if not self._is_write_for_us_page(url, title, description):
            return None

        # Extract domain metrics if available
        rank_group = serp_result.get('rank_group', 0)
        rank_absolute = serp_result.get('rank_absolute', 0)

        # Calculate opportunity score
        score = self._calculate_opportunity_score(
            rank_absolute=rank_absolute,
            domain=domain,
            url=url
        )

        opportunity = {
            'website': self._extract_website_name(domain, title),
            'domain': domain,
            'url': url,
            'write_for_us_page': url,
            'category': self._categorize_opportunity(keyword, title, description),
            'audience': self._determine_audience(domain, description),
            'score': score,
            'rank': rank_absolute,
            'title': title,
            'description': description,

            # These would be extracted by visiting the page
            'min_words': 'Check page',
            'links_allowed': 'Check page',
            'free_or_paid': 'Check page',
            'contact': 'Check page',
            'notes': f'Rank #{rank_absolute} for "{keyword}"'
        }

        return opportunity

    def _is_write_for_us_page(
        self,
        url: str,
        title: str,
        description: str
    ) -> bool:
        """Check if this is actually a write for us page"""

        indicators = [
            'write for us',
            'write-for-us',
            'guest post',
            'submit article',
            'contribute',
            'become a contributor',
            'submission guidelines',
        ]

        text = f"{url.lower()} {title.lower()} {description.lower()}"

        return any(indicator in text for indicator in indicators)

    def _extract_website_name(
        self,
        domain: str,
        title: str
    ) -> str:
        """Extract clean website name"""

        # Try to get name from title
        if '-' in title:
            name = title.split('-')[0].strip()
            if len(name) < 50:
                return name

        # Fallback to domain
        clean_domain = domain.replace('www.', '').replace('.com', '').replace('.in', '')
        return clean_domain.title()

    def _categorize_opportunity(
        self,
        keyword: str,
        title: str,
        description: str
    ) -> str:
        """Categorize the opportunity by niche"""

        text = f"{keyword} {title} {description}".lower()

        categories = {
            'Admissions / College': ['admission', 'college', 'university', 'application'],
            'Career Counselling': ['career', 'counselling', 'guidance', 'jobs'],
            'Exam / Competitive': ['exam', 'test', 'competitive', 'entrance', 'jee', 'neet'],
            'EdTech / Online Learning': ['edtech', 'online learning', 'e-learning', 'digital'],
            'Study Abroad': ['study abroad', 'international', 'overseas'],
            'Parenting / School': ['parenting', 'parent', 'school', 'child'],
            'General Education': ['education', 'learning', 'teaching'],
        }

        for category, keywords_list in categories.items():
            if any(kw in text for kw in keywords_list):
                return category

        return 'General Education'

    def _determine_audience(
        self,
        domain: str,
        description: str
    ) -> str:
        """Determine target audience geography"""

        text = f"{domain} {description}".lower()

        if any(indicator in text for indicator in ['.in', 'india', 'indian']):
            return 'India'
        elif any(indicator in text for indicator in ['.uk', 'britain', 'british']):
            return 'UK'
        elif any(indicator in text for indicator in ['.com', 'us', 'america']):
            return 'US/Global'
        else:
            return 'Global'

    def _calculate_opportunity_score(
        self,
        rank_absolute: int,
        domain: str,
        url: str
    ) -> int:
        """Calculate opportunity score (0-100)"""

        score = 50  # Base score

        # Better ranking = higher score
        if rank_absolute <= 3:
            score += 30
        elif rank_absolute <= 10:
            score += 20
        elif rank_absolute <= 20:
            score += 10

        # Known high-authority domains
        high_authority = [
            'shiksha.com', 'careers360.com', 'collegedunia.com',
            'elearningindustry.com', 'edutopia.org', 'leverageedu.com'
        ]

        if any(auth_domain in domain for auth_domain in high_authority):
            score += 20

        return min(score, 100)

    def export_to_markdown(
        self,
        opportunities: List[Dict[str, Any]],
        keyword: str,
        output_dir: str = 'output'
    ) -> str:
        """Export opportunities to markdown table"""

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"{output_dir}/backlink-opportunities-{keyword.replace(' ', '-')}-{timestamp}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Guest Posting Opportunities: {keyword}\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total opportunities found: {len(opportunities)}\n\n")

            f.write("## Summary\n\n")
            f.write("| # | Website | Category | Audience | Score | Rank |\n")
            f.write("|---|---------|----------|----------|-------|------|\n")

            for i, opp in enumerate(opportunities, 1):
                f.write(
                    f"| {i} | [{opp['website']}]({opp['url']}) | "
                    f"{opp['category']} | {opp['audience']} | "
                    f"{opp['score']}/100 | #{opp['rank']} |\n"
                )

            f.write("\n## Detailed Opportunities\n\n")

            for i, opp in enumerate(opportunities, 1):
                f.write(f"### {i}. {opp['website']}\n\n")
                f.write(f"- **URL:** {opp['url']}\n")
                f.write(f"- **Category:** {opp['category']}\n")
                f.write(f"- **Audience:** {opp['audience']}\n")
                f.write(f"- **Score:** {opp['score']}/100\n")
                f.write(f"- **Google Rank:** #{opp['rank']}\n")
                f.write(f"- **Description:** {opp['description']}\n")
                f.write(f"- **Min Words:** {opp['min_words']}\n")
                f.write(f"- **Links Allowed:** {opp['links_allowed']}\n")
                f.write(f"- **Free/Paid:** {opp['free_or_paid']}\n")
                f.write(f"- **Contact:** {opp['contact']}\n")
                f.write(f"- **Notes:** {opp['notes']}\n\n")

        return filename


def main():
    """CLI interface for testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python backlink_opportunity_finder.py [keyword]")
        print("Example: python backlink_opportunity_finder.py 'career counselling'")
        sys.exit(1)

    keyword = ' '.join(sys.argv[1:])

    finder = BacklinkOpportunityFinder()
    opportunities = finder.find_opportunities(keyword, limit=50)

    if opportunities:
        filename = finder.export_to_markdown(opportunities, keyword)
        print(f"\n✅ Results saved to: {filename}")
        print(f"\nTop 5 opportunities:")
        print()

        for i, opp in enumerate(opportunities[:5], 1):
            print(f"{i}. {opp['website']} (Score: {opp['score']}/100)")
            print(f"   {opp['url']}")
            print(f"   Category: {opp['category']} | Audience: {opp['audience']}")
            print()
    else:
        print("❌ No opportunities found")


if __name__ == "__main__":
    main()
