"""Fact verification lane - validates factual claims through multiple sources."""

from __future__ import annotations

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from ..config import MODEL, STATE_KEYS
from ..tools import FACT_CHECK_TOOL, FACT_PERPLEXITY_TOOL


# Worker 1: Primary fact-check databases
primary_worker = LlmAgent(
    name="FactPrimaryWorker",
    model=MODEL,
    description="Queries major fact-checking registries",
    instruction="""Call lookup_fact_checks with the user's claim.
Return the exact JSON response - do not modify it.""",
    tools=[FACT_CHECK_TOOL],
    output_key=STATE_KEYS.FACT_PRIMARY,
)

# Worker 2: Deep research via Perplexity
perplexity_worker = LlmAgent(
    name="FactPerplexityWorker",
    model=MODEL,
    description="Performs web research to validate factual claims",
    instruction="""Call research_fact_with_perplexity with the user's claim.
Return the exact JSON response - do not modify it.""",
    tools=[FACT_PERPLEXITY_TOOL],
    output_key=STATE_KEYS.FACT_PERPLEXITY,
)

# Merger agent
fact_merger = LlmAgent(
    name="FactMerger",
    model=MODEL,
    description="Synthesizes fact-checking data into structured report",
    instruction=f"""Consolidate fact verification results from:
- {{{STATE_KEYS.FACT_PRIMARY}}}
- {{{STATE_KEYS.FACT_PERPLEXITY}}}

Output Markdown in this format:

## Fact Check
- verdict: true|false|partly_true|misleading|unknown
- confidence: 0.0-1.0
- claim_category: health|politics|science|economics|other

### Key Findings
* Finding from primary fact-check databases
* Finding from perplexity research

### Fact-Check Sources
1. Organization - Rating - Full URL
2. Organization - Rating - Full URL

### Supporting Evidence
* Evidence point with source URL
* Evidence point with source URL

**Rules:**
- Preserve exact URLs and ratings from worker data
- If any worker has status='error', note it
- Include claim review ratings (e.g., "FALSE", "MOSTLY TRUE")
- Cross-reference evidence from both workers
- Flag contradictions explicitly
""",
    output_key=STATE_KEYS.FACT_SUMMARY,
)

# Parallel execution of both workers
fact_fanout = ParallelAgent(
    name="FactWorkerFanout",
    description="Runs fact-checking workers concurrently",
    sub_agents=[primary_worker, perplexity_worker],
)

# Complete fact lane: fanout then merge
fact_lane = SequentialAgent(
    name="FactCheckAgent",
    description="Complete fact verification pipeline",
    sub_agents=[fact_fanout, fact_merger],
)


__all__ = ["fact_lane"]
