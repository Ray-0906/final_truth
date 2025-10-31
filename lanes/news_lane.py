"""News verification lane - validates breaking news across multiple sources."""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from ..config import MODEL, STATE_KEYS
from ..tools import NEWS_API_TOOL, FACT_CHECK_TOOL, NEWS_PERPLEXITY_TOOL


# Worker 1: Query news APIs
api_worker = LlmAgent(
    name="NewsApiWorker",
    model=MODEL,
    description="Fetches licensed news coverage for verification",
    instruction="""You are a news API query specialist with access to the fetch_news_evidence tool.

**YOUR TASK:**
Extract a search query from the user's claim and fetch relevant news articles.

**QUERY EXTRACTION RULES:**
- Keep it to 10-15 words maximum (API limitation)
- Focus on: proper nouns (names, places), key events, dates
- Remove filler words: 'a', 'the', 'said', 'told', 'that', 'has', etc.
- Keep action words and specific details

**Examples:**
- "A woman died in cyclone that hit Andhra Pradesh" → "woman died cyclone Andhra Pradesh"
- "The president announced new policy yesterday" → "president announced new policy"

**EXECUTION:**
1. Extract the condensed query from the user's claim
2. Call fetch_news_evidence with the query string
3. Return the exact JSON response you receive

**ERROR HANDLING:**
If the tool returns an error status, return that error message exactly as-is. The system will handle it.

**STOP CONDITION:**
Your job is done after returning the tool's response. Do not analyze or modify the results.""",
    tools=[NEWS_API_TOOL],
    output_key=STATE_KEYS.NEWS_API,
)

# Worker 2: Cross-reference with fact-check databases
fact_worker = LlmAgent(
    name="NewsFactWorker",
    model=MODEL,
    description="Checks if claim appears in fact-check registries",
    instruction="""You are a fact-check database specialist with access to the lookup_fact_checks tool.

**YOUR TASK:**
Check if the user's claim has been previously fact-checked by major organizations.

**EXECUTION:**
1. Call lookup_fact_checks with the user's exact claim (no modification needed)
2. Return the exact JSON response you receive

**TOOL BEHAVIOR:**
The tool searches Google Fact Check Tools API for existing fact-checks.
Results include ratings like "FALSE", "TRUE", "PARTLY TRUE", "MISLEADING".

**ERROR HANDLING:**
If the tool returns status='error', return that response exactly. Common errors:
- API key issues
- Network problems
- No fact-checks found (this is NOT an error - it's valid data)

**STOP CONDITION:**
Your job is done after returning the tool's response. Do not interpret or summarize the results.""",
    tools=[FACT_CHECK_TOOL],
    output_key=STATE_KEYS.NEWS_FACT,
)

# Worker 3: Research via Perplexity
perplexity_worker = LlmAgent(
    name="NewsPerplexityWorker",
    model=MODEL,
    description="Performs web research to validate news claims",
    instruction="""You are a web research specialist with access to the research_news_with_perplexity tool.

**YOUR TASK:**
Research the user's claim across the web to find evidence and context.

**CRITICAL: YOU MUST CALL THE TOOL**
You do NOT have internet access yourself. You MUST call the research_news_with_perplexity tool to get real web data.
DO NOT generate or fabricate research results. ONLY return what the tool provides.

**EXECUTION:**
1. Call research_news_with_perplexity with the user's exact claim
2. Wait for the tool to return results
3. Return the exact JSON response you receive from the tool

**TOOL BEHAVIOR:**
The tool uses Perplexity AI to search the web and synthesize findings.
Results include analysis, sources, and confidence assessment.

**ERROR HANDLING:**
If the tool returns status='error', return that response exactly. Common errors:
- API rate limits
- Network issues
- Malformed queries

The merger agent will handle error responses appropriately.

**STOP CONDITION:**
Your job is done after returning the tool's response. Do not add commentary.

**REMEMBER:** You cannot research the web yourself. You MUST use the tool.""",
    tools=[NEWS_PERPLEXITY_TOOL],
    output_key=STATE_KEYS.NEWS_PERPLEXITY,
)

# Merger agent
news_merger = LlmAgent(
    name="NewsMerger",
    model=MODEL,
    description="Synthesizes news verification data into structured report",
    instruction=f"""You are a news verification analyst. You have received results from three parallel workers and must synthesize them into a clear, structured report.

**YOUR DATA SOURCES:**
The session state contains these three worker outputs:
- {{{STATE_KEYS.NEWS_API}}}: Licensed news article results from GNews API
- {{{STATE_KEYS.NEWS_FACT}}}: Fact-check database results from Google Fact Check Tools
- {{{STATE_KEYS.NEWS_PERPLEXITY}}}: Web research results from Perplexity AI

**DATA STRUCTURE:**
Each source is JSON with this structure:
```
{{
  "status": "success" or "error",
  "data": {{...}} or "error": "message"
}}
```

**YOUR TASK:**
Analyze all three sources and produce a consolidated Markdown report.

**OUTPUT FORMAT (STRICT):**
```markdown
## News Verification Report

**Verdict:** true | false | mixed | unverified
**Confidence:** 0.0 - 1.0 (numerical score)
**Coverage Level:** widespread | limited | none

### Key Findings
* [Bullet point from news API - include outlet names]
* [Bullet point from fact-check databases - include ratings]
* [Bullet point from web research - include key evidence]

### News Sources Found
1. [Outlet Name] - [Full URL]
2. [Outlet Name] - [Full URL]
(List all unique sources from all workers)

### Fact-Check Records
1. [Organization] - [Rating] - [Full URL]
(From fact-check worker, if any found)

### Analysis Notes
* [Any conflicts between sources]
* [Coverage gaps or limitations]
* [Temporal context - when did this happen]
```

**VERDICT DETERMINATION LOGIC:**
- **true**: Multiple credible sources confirm, fact-checks support, high consistency
- **false**: Fact-checks rate as false, no credible coverage, contradictory evidence
- **mixed**: Some truth but misleading context, partly true rating
- **unverified**: Insufficient coverage, no fact-checks, inconclusive research

**CONFIDENCE SCORING:**
- 0.9-1.0: Multiple authoritative sources, clear consensus
- 0.7-0.8: Good sources but some gaps
- 0.5-0.6: Limited coverage, mixed signals
- 0.3-0.4: Very limited data
- 0.0-0.2: Contradictory or no reliable data

**CRITICAL RULES:**
1. If a worker has status='error', note it in Analysis Notes but don't fail
2. Preserve exact URLs - do not truncate or modify links
3. Deduplicate sources by URL (same URL from different workers = one entry)
4. If fact-check and news coverage conflict, note this explicitly in Analysis Notes
5. Include outlet names/organizations with every source
6. Don't invent sources - only list what workers returned
7. Coverage level based on number of distinct outlets: 3+ = widespread, 1-2 = limited, 0 = none

**ERROR HANDLING:**
If ALL workers returned errors, output:
```markdown
## News Verification Report

**Verdict:** unverified
**Confidence:** 0.0
**Coverage Level:** none

### Error Summary
* News API: [error message]
* Fact-Check: [error message]
* Web Research: [error message]

Unable to verify due to technical issues. Please try again later.
```

**STOP CONDITION:**
After generating the Markdown report, your job is complete. Do not add commentary outside the report format.
""",
    output_key=STATE_KEYS.NEWS_SUMMARY,
)

# Parallel execution of all workers
news_fanout = ParallelAgent(
    name="NewsWorkerFanout",
    description="Runs news verification workers concurrently",
    sub_agents=[api_worker, fact_worker, perplexity_worker],
)

# Complete news lane: fanout then merge
news_lane = SequentialAgent(
    name="NewsCheckAgent",
    description="Complete news verification pipeline",
    sub_agents=[news_fanout, news_merger],
)


__all__ = ["news_lane"]
