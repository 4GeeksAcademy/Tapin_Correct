# Organization Values Extraction Prompt

Use this prompt with a research agent or LLM to analyze organization websites and extract their core values for the Tapin matching system.

## Prompt Template

```
Analyze the following organization/event information and identify which of these core values align with their mission and work:

**Available Values:**
1. Community Building - Strengthening local communities and bringing people together
2. Environmental Sustainability - Protecting the environment and promoting sustainable practices
3. Education & Learning - Promoting literacy, learning, and educational opportunities
4. Health & Wellness - Supporting physical and mental health for all
5. Equality & Justice - Fighting for human rights, equality, and social justice
6. Poverty Alleviation - Fighting poverty and supporting those in need
7. Youth Empowerment - Supporting and empowering young people
8. Elder Care - Supporting and caring for senior citizens
9. Animal Welfare - Protecting and caring for animals
10. Arts & Culture - Promoting arts, culture, and creative expression
11. Innovation & Technology - Using technology and innovation for social good
12. Disaster Relief - Responding to emergencies and disasters
13. Hunger Relief - Fighting hunger and food insecurity
14. Women Empowerment - Supporting women's rights and empowerment
15. Diversity & Inclusion - Promoting diversity, inclusion, and belonging

**Organization Information:**
- Name: {organization_name}
- Description: {description}
- Category: {category}
- Website URL: {url}

**Instructions:**
1. Analyze the organization's mission, description, and activities
2. Identify 2-5 core values that best represent their work
3. Return ONLY the value IDs (e.g., community, environment, education) as a comma-separated list
4. Prioritize values that are central to their mission, not peripheral activities

**Output Format:**
Return only the value IDs, comma-separated, with no other text:
Example: community,youth,education

{organization_info}
```

## Usage Example

For an organization like "Boston Food Bank":
- Description: "We provide emergency food assistance and work to end hunger in our community"
- Category: "Social Services"

The research agent would return:
```
hunger,poverty,community
```

## Integration with Backend

This prompt can be used in `google_search.py` when enriching web search results:

```python
def extract_values_from_organization(org_name, description, category, url):
    """
    Use LLM to extract values from organization information
    """
    prompt = f'''
    Analyze this organization and identify core values...
    Organization: {org_name}
    Description: {description}
    Category: {category}
    '''

    # Call LLM API (OpenAI, Anthropic, etc.)
    response = llm_client.complete(prompt)

    # Parse comma-separated value IDs
    value_ids = [v.strip() for v in response.split(',')]

    return value_ids
```

## Automated Enrichment

The values can be automatically extracted and added to events when:
1. Scraping web search results for volunteer opportunities
2. Users create new organization listings
3. Importing events from external sources
4. Batch processing existing database records

This ensures consistent value tagging across all organizations and events in the Tapin platform.
