"""News verification lane - validates breaking news across multiple sources."""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from ..config import MODEL, STATE_KEYS
from ..tools import NEWS_API_TOOL, FACT_CHECK_TOOL, NEWS_PERPLEXITY_TOOL


# Worker 1: Query news APIs
api_worker = LlmAgent(
    name="NewsApiWorker",
    model=MODEL,
    description="Fetches licensed news coverage for verification",
    instruction="""Extract the key entities and terms from the user's claim (max 10-15 words).
Remove filler words like 'a', 'the', 'said', 'told', etc.
Focus on: names, places, events, dates.

Then call fetch_news_evidence with the condensed query.
Return the exact JSON response.""",
    tools=[NEWS_API_TOOL],
    output_key=STATE_KEYS.NEWS_API,
)

# Worker 2: Cross-reference with fact-check databases
fact_worker = LlmAgent(
    name="NewsFactWorker",
    model=MODEL,
    description="Checks if claim appears in fact-check registries",
    instruction="""Call lookup_fact_checks with the user's claim.
Return the exact JSON response - do not modify it.""",
    tools=[FACT_CHECK_TOOL],
    output_key=STATE_KEYS.NEWS_FACT,
)

# Worker 3: Research via Perplexity
perplexity_worker = LlmAgent(
    name="NewsPerplexityWorker",
    model=MODEL,
    description="Performs web research to validate news claims",
    instruction="""Call research_news_with_perplexity with the user's claim.
Return the exact JSON response - do not modify it.""",
    tools=[NEWS_PERPLEXITY_TOOL],
    output_key=STATE_KEYS.NEWS_PERPLEXITY,
)

# Merger agent
news_merger = LlmAgent(
    name="NewsMerger",
    model=MODEL,
    description="Synthesizes news verification data into structured report",
    instruction=f"""Consolidate news verification results from:
- {{{STATE_KEYS.NEWS_API}}}
- {{{STATE_KEYS.NEWS_FACT}}}
- {{{STATE_KEYS.NEWS_PERPLEXITY}}}

Output Markdown in this format:

## News Verification
- verdict: true|false|mixed|unknown
- confidence: 0.0-1.0
- coverage_level: widespread|limited|none

### Key Findings
* Finding from api worker
* Finding from fact worker  
* Finding from perplexity worker

### Sources
1. Outlet Name - Full URL
2. Outlet Name - Full URL

**Rules:**
- Preserve exact URLs from worker data
- If any worker has status='error', note it
- Deduplicate sources by URL
- Mark conflicting information explicitly
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
