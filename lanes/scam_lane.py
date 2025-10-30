"""Scam detection lane - identifies potential scams through multiple analysis angles."""

from __future__ import annotations

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from ..config import MODEL, STATE_KEYS
from ..tools import VIRUSTOTAL_TOOL, SCAM_PERPLEXITY_TOOL, SCAM_SENTIMENT_TOOL


# Worker 1: URL/link security scanning
link_worker = LlmAgent(
    name="ScamLinkWorker",
    model=MODEL,
    description="Scans URLs for malicious content and phishing",
    instruction="""Call scan_urls_with_virustotal with the user's input.
Return the exact JSON response - do not modify it.""",
    tools=[VIRUSTOTAL_TOOL],
    output_key=STATE_KEYS.SCAM_LINK,
)

# Worker 2: Perplexity research on scam patterns
perplexity_worker = LlmAgent(
    name="ScamPerplexityWorker",
    model=MODEL,
    description="Researches known scam patterns and reports",
    instruction="""Call research_scam_with_perplexity with the user's input.
Return the exact JSON response - do not modify it.""",
    tools=[SCAM_PERPLEXITY_TOOL],
    output_key=STATE_KEYS.SCAM_PERPLEXITY,
)

# Worker 3: Sentiment and urgency analysis
sentiment_worker = LlmAgent(
    name="ScamSentimentWorker",
    model=MODEL,
    description="Analyzes text for scam manipulation tactics",
    instruction="""Call analyze_scam_sentiment with the user's input.
Return the exact JSON response - do not modify it.""",
    tools=[SCAM_SENTIMENT_TOOL],
    output_key=STATE_KEYS.SCAM_SENTIMENT,
)

# Merger agent
scam_merger = LlmAgent(
    name="ScamMerger",
    model=MODEL,
    description="Synthesizes scam detection data into structured report",
    instruction=f"""Consolidate scam detection results from:
- {{{STATE_KEYS.SCAM_LINK}}}
- {{{STATE_KEYS.SCAM_PERPLEXITY}}}
- {{{STATE_KEYS.SCAM_SENTIMENT}}}

Output Markdown in this format:

## Scam Assessment
- verdict: scam|suspicious|legitimate|unknown
- confidence: 0.0-1.0
- risk_level: critical|high|medium|low

### Red Flags Detected
* Flag from link scanner (malicious URLs, phishing)
* Flag from perplexity (known scam patterns)
* Flag from sentiment analysis (urgency tactics, manipulation)

### URL Security Status
- domain.com: safe|malicious|suspicious (X/Y vendors flagged)
- otherdomain.com: safe|malicious|suspicious (X/Y vendors flagged)

### Manipulation Tactics
* Tactic name - evidence from sentiment worker
* Tactic name - evidence from sentiment worker

### Related Scam Reports
1. Report title - Source URL
2. Report title - Source URL

**Rules:**
- Preserve exact URLs and vendor counts from link worker
- If any worker has status='error', note it
- Cross-reference red flags across all workers
- Highlight urgency language and pressure tactics
- Include VirusTotal scan details (flagged vendors, analysis URLs)
""",
    output_key=STATE_KEYS.SCAM_SUMMARY,
)

# Parallel execution of all workers
scam_fanout = ParallelAgent(
    name="ScamWorkerFanout",
    description="Runs scam detection workers concurrently",
    sub_agents=[link_worker, perplexity_worker, sentiment_worker],
)

# Complete scam lane: fanout then merge
scam_lane = SequentialAgent(
    name="ScamCheckAgent",
    description="Complete scam detection pipeline",
    sub_agents=[scam_fanout, scam_merger],
)


__all__ = ["scam_lane"]


__all__ = ["create_scam_lane"]
