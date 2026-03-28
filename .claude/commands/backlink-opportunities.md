# Backlink Opportunities Research

Find "write for us" guest posting opportunities for link building.

## Usage

```bash
/backlink-opportunities [your keyword]
```

## Examples

```bash
/backlink-opportunities career counselling
/backlink-opportunities engineering education
/backlink-opportunities college admissions
```

## What It Does

Searches for guest posting opportunities using the pattern:
- `[keyword] inurl:write-for-us`
- `[keyword] "write for us"`
- `[keyword] "guest post"`
- `[keyword] "contribute"`

Then extracts and organizes:
1. Website name and URL
2. Write for us page URL
3. Category/niche
4. Target audience
5. Minimum word count requirements
6. Links allowed (dofollow/nofollow)
7. Free or paid opportunities
8. Contact information
9. Additional notes (DA, traffic, approval time)

## Output

Creates a detailed CSV/Markdown table in:
`output/backlink-opportunities-[keyword]-[date].md`

With sortable data:
- Website authority (DA/DR)
- Relevance to your niche
- Link quality (dofollow/nofollow)
- Difficulty (word count, requirements)
- Response time estimates

## Requirements

- DataForSEO API (for SERP searches)
- Web scraping capabilities (built-in)
- Keyword parameter

## Agent Workflow

1. **Search Phase:**
   - Query DataForSEO SERP API with search operators
   - Collect top 50-100 results
   - Filter for actual "write for us" pages

2. **Extraction Phase:**
   - Visit each "write for us" page
   - Extract submission guidelines
   - Parse requirements (word count, links, etc.)
   - Find contact information

3. **Analysis Phase:**
   - Check domain authority
   - Assess relevance to your niche
   - Categorize by industry/topic
   - Estimate difficulty

4. **Output Phase:**
   - Generate sortable table
   - Rank by opportunity score
   - Include all contact details
   - Add actionable notes

## Opportunity Score Factors

- Domain Authority (30%)
- Relevance to niche (25%)
- Link quality (20%)
- Ease of approval (15%)
- Traffic estimate (10%)

## Use Cases

1. **Link Building Campaign:**
   - Find 50+ guest post opportunities
   - Filter by niche and quality
   - Create outreach list

2. **Competitor Backlink Replication:**
   - See where competitors guest post
   - Find similar opportunities
   - Build same links

3. **Niche Authority Building:**
   - Target high-authority sites
   - Build topical relevance
   - Establish expertise

## Notes

- Cost: ~$0.10-0.50 per search (DataForSEO SERP API)
- Results cached for 30 days
- Exports to CSV for outreach tools
- Includes email templates for pitching
