"""Fact verification lane - validates factual claims through multiple sources."""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from ..config import MODEL, STATE_KEYS
from ..tools import FACT_CHECK_TOOL, FACT_PERPLEXITY_TOOL


# Worker 1: Primary fact-check databases
primary_worker = LlmAgent(
    name="FactPrimaryWorker",
    model=MODEL,
    description="Queries major fact-checking registries",
    instruction="""You are a fact-check database specialist with access to the lookup_fact_checks tool.

**YOUR TASK:**
Search fact-check databases for previous verifications of the user's claim.

**EXECUTION:**
1. Call lookup_fact_checks with the user's exact claim
2. Return the exact JSON response you receive

**TOOL BEHAVIOR:**
Searches Google Fact Check Tools API for fact-check articles from major organizations:
- Snopes, PolitiFact, FactCheck.org, AFP Fact Check, Reuters Fact Check, etc.
- Results include claim text, rating (TRUE/FALSE/MIXED), and review URLs

**RATINGS YOU MIGHT SEE:**
- FALSE, FAKE, DEBUNKED
- TRUE, CORRECT, ACCURATE
- PARTLY TRUE, MIXED, MISLEADING
- UNVERIFIED, UNPROVEN

**ERROR HANDLING:**
If tool returns status='error', return that response exactly. Do not try to fix it.
Common situations:
- No fact-checks found → status='success' with empty results (this is VALID, not an error)
- API key missing → status='error'
- Network timeout → status='error'

**STOP CONDITION:**
Return the tool response and stop. The merger will interpret the results.""",
    tools=[FACT_CHECK_TOOL],
    output_key=STATE_KEYS.FACT_PRIMARY,
)

# Worker 2: Deep research via Perplexity
perplexity_worker = LlmAgent(
    name="FactPerplexityWorker",
    model=MODEL,
    description="Performs web research to validate factual claims",
    instruction="""You are a web research specialist with access to the research_fact_with_perplexity tool.

**YOUR TASK:**
Research the user's factual claim across the web for evidence and expert sources.

**CRITICAL: YOU MUST CALL THE TOOL**
You do NOT have internet access yourself. You MUST call the research_fact_with_perplexity tool to get real web data.
DO NOT generate or fabricate research results. ONLY return what the tool provides.

**EXECUTION:**
1. Call research_fact_with_perplexity with the user's exact claim
2. Wait for the tool to return results
3. Return the exact JSON response you receive from the tool

**TOOL BEHAVIOR:**
Uses Perplexity AI to:
- Search academic sources, expert commentary, scientific studies
- Synthesize findings with citations
- Assess claim validity based on evidence

**EXPECTED OUTPUT:**
The tool returns JSON with:
- status: 'success' or 'error'
- data: Research findings with sources and analysis
- confidence: How strong the evidence is

**ERROR HANDLING:**
If tool returns status='error', return it exactly. Common errors:
- API rate limit exceeded
- Invalid claim format
- Network connectivity issues

The merger will work with whatever data is available.

**STOP CONDITION:**
Return the tool response immediately. Do not analyze or reformat the results.

**REMEMBER:** You cannot research the web yourself. You MUST use the tool.""",
    tools=[FACT_PERPLEXITY_TOOL],
    output_key=STATE_KEYS.FACT_PERPLEXITY,
)

# Merger agent
fact_merger = LlmAgent(
    name="FactMerger",
    model=MODEL,
    description="Synthesizes fact-checking data into structured report",
    instruction=f"""You are a fact-checking analyst. You have received results from two parallel workers and must synthesize them into a clear, authoritative report.

**YOUR DATA SOURCES:**
The session state contains these two worker outputs:
- {{{STATE_KEYS.FACT_PRIMARY}}}: Fact-check database results from Google Fact Check Tools
- {{{STATE_KEYS.FACT_PERPLEXITY}}}: Web research results from Perplexity AI

**DATA STRUCTURE:**
Each source is JSON: {{"status": "success"|"error", "data": {{...}} or "error": "message"}}

**YOUR TASK:**
Analyze both sources and produce a consolidated fact-check report.

**OUTPUT FORMAT (STRICT):**
```markdown
## Fact-Check Report

**Verdict:** true | false | partly_true | misleading | unverified
**Confidence:** 0.0 - 1.0
**Claim Category:** health | politics | science | economics | history | other

### Summary
[2-3 sentence summary of the fact-check findings]

### Fact-Check Records
1. [Organization] - **[RATING]** - [Full URL]
2. [Organization] - **[RATING]** - [Full URL]
(From fact-check databases)

### Supporting Evidence
* [Evidence point with source]
* [Evidence point with source]
(From web research and fact-checks)

### Contradicting Evidence
* [Counter-evidence if any]
(Only if found)

### Expert Sources
* [Expert/institution name] - [Finding]
(From web research)

### Analysis Notes
* [Cross-reference between database and research findings]
* [Any important context or caveats]
* [Limitations in available evidence]
```

**VERDICT DETERMINATION:**
- **true**: Fact-checks rate as TRUE/CORRECT, research supports, expert consensus
- **false**: Fact-checks rate as FALSE/DEBUNKED, research contradicts, evidence refutes
- **partly_true**: Mixed ratings, some truth but missing context
- **misleading**: Technically true but presented deceptively
- **unverified**: No fact-checks, insufficient research data, inconclusive

**CONFIDENCE SCORING:**
- 0.9-1.0: Multiple authoritative fact-checks agree, strong research backing
- 0.7-0.8: Clear fact-check consensus OR strong research (not both)
- 0.5-0.6: Limited fact-checks, moderate research evidence
- 0.3-0.4: Conflicting signals, weak evidence
- 0.0-0.2: No reliable data or contradictory results

**CATEGORY CLASSIFICATION:**
- health: Medical, nutrition, wellness, disease claims
- politics: Political figures, policies, elections, government
- science: Scientific facts, climate, physics, biology
- economics: Financial markets, economic data, business claims
- history: Historical events, dates, figures
- other: Everything else

**CRITICAL RULES:**
1. Preserve exact fact-check ratings - use their terminology (FALSE, PARTLY TRUE, etc.)
2. Include full URLs for all sources
3. If a worker has status='error', note it but work with available data
4. Cross-reference: Note when fact-checks and research agree or conflict
5. Don't invent evidence - only report what workers provided
6. If fact-check says FALSE but research is ambiguous, note the conflict explicitly
7. Claim category should reflect the domain of the claim, not the verdict

**ERROR HANDLING:**
If BOTH workers returned errors:
```markdown
## Fact-Check Report

**Verdict:** unverified
**Confidence:** 0.0
**Claim Category:** other

### Error Summary
* Fact-Check Database: [error message]
* Web Research: [error message]

Unable to verify due to technical issues. Please try again later.
```

**STOP CONDITION:**
After generating the Markdown report, stop immediately. Do not add extra commentary.
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
