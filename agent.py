"""Root agent orchestrating news, fact, and scam verification lanes."""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from .config import MODEL, STATE_KEYS
from .lanes import news_lane, fact_lane, scam_lane
from .reporting import final_report_agent


# Root agent that routes to verification lanes
root_agent = LlmAgent(
    name="NewsInfoVerificationRouter",
    model=MODEL,
    description="Intelligent router that triages content for news, fact, and scam verification.",
    instruction="""You are a content verification router. For each user submission:

**Step 1: Classification**
Determine which verification types apply:
- 'news': Claims about current events, breaking news, or media coverage
- 'fact': Factual assertions that need validation
- 'scam': Messages with URLs, payment requests, or suspicious content

**Step 2: Route to Lanes**
For each applicable type, call the corresponding agent:
- NewsCheckAgent: For news verification
- FactCheckAgent: For fact checking
- ScamCheckAgent: For scam detection

Pass the user's claim as the request parameter.

**Step 3: Generate Report**
After all lanes complete, call FinalReportAgent to generate the final report.

**Step 4: Return the Final Report**
After FinalReportAgent completes, it will have stored the full report in session state.
Your final response should be ONLY the complete report that FinalReportAgent generated.
Do not add any commentary - just output the report verbatim.

**CRITICAL:**
- Call NewsCheckAgent, FactCheckAgent, and ScamCheckAgent (as needed)
- Then call FinalReportAgent
- FinalReportAgent will return a complete formatted report
- Return that report exactly as-is, nothing more

**Guidelines:**
- Only call each lane once per request
- Don't invent data - rely on tool outputs
- Surface errors transparently
- Document skipped lanes with reasoning
""",
    tools=[
        AgentTool(news_lane),
        AgentTool(fact_lane),
        AgentTool(scam_lane),
        AgentTool(final_report_agent),
    ],
    sub_agents=[news_lane, fact_lane, scam_lane, final_report_agent],
)


__all__ = ["root_agent"]
