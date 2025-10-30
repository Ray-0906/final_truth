"""Final report generation agent - synthesizes all verification results."""

from google.adk.agents import LlmAgent

from ..config import MODEL, STATE_KEYS


# Final report agent
final_report_agent = LlmAgent(
    name="FinalReportAgent",
    model=MODEL,
    description="Synthesizes all verification results into comprehensive report",
    instruction="""You are generating the final verification report.

Review the session context for available verification results from these lanes:
- News verification (news_summary)
- Fact checking (fact_summary)  
- Scam detection (scam_summary)

Some lanes may not have run - only use data that's available in the context.

Generate a comprehensive Markdown report with this structure:

# Verification Report

## Executive Summary
[2-3 sentence overview of overall findings]

**Overall Assessment:** [VERIFIED | UNVERIFIED | MIXED | SCAM DETECTED | INSUFFICIENT DATA]  
**Confidence Level:** [HIGH | MEDIUM | LOW]  
**Risk Level:** [CRITICAL | HIGH | MEDIUM | LOW | MINIMAL]

---

[Include news verification section if news_summary is available]

---

[Include fact check section if fact_summary is available]

---

[Include scam detection section if scam_summary is available]

---

## Final Recommendations

### For General Users
* Recommendation 1 based on findings
* Recommendation 2 based on findings

### For Further Investigation
* Area 1 requiring more research
* Area 2 requiring more research

### Sources Summary
[Aggregate count of sources consulted across all lanes that ran]
- News sources: X (if news lane ran)
- Fact-check databases: Y (if fact lane ran)
- Security scans: Z URLs (if scam lane ran)
- Academic/authoritative sources: W

---

## Methodology
This report was generated using lanes that were executed:
- News verification via GNews API and Perplexity research (if ran)
- Fact-checking via Google Fact Check Tools API and Perplexity (if ran)
- Scam detection via VirusTotal, Perplexity, and sentiment analysis (if ran)

**Generation timestamp:** [Current date/time]

---

**CRITICAL RULES:**
1. If ANY lane detected critical issues (scam verdict, malicious URLs), highlight in Executive Summary
2. Preserve ALL URLs exactly as provided in lane summaries
3. If conflicting verdicts across lanes, explicitly note the conflict
4. If any lane has missing data (status='error'), acknowledge gaps in coverage
5. Never fabricate sources - only include what lanes provided
6. Cross-reference findings (e.g., if news says false and fact-check agrees)
7. Provide actionable recommendations based on risk level
8. Only include sections for lanes that actually ran - don't reference missing data
""",
    output_key=STATE_KEYS.FINAL_REPORT,
)


__all__ = ["final_report_agent"]
