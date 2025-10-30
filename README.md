# News Information Verification Agent v2

**Improved multi-agent system for verifying news, facts, and detecting scams using Google ADK.**

## 🎯 What's New in v2

This is a complete rewrite following ADK best practices with significant architectural improvements:

### Key Improvements

1. **Factory Pattern**
   - All agents created via `create_*()` factory functions
   - Easier testing and configuration management
   - Clear separation of agent construction from usage

2. **Simplified Tool Signatures**
   - All tool functions use `func(request: str) -> dict` signature
   - Compatible with ADK's automatic function calling
   - No complex type annotations that break ADK parser

3. **Cleaner Instructions**
   - State templating with `{STATE_KEY}` syntax
   - More explicit instructions for each agent
   - Better defined output formats (Markdown structured)

4. **Consistent Architecture**
   - All lanes follow same pattern: Sequential(Parallel(workers), Merger)
   - Predictable data flow across all verification types
   - Easier to maintain and extend

5. **Better Error Handling**
   - All tool functions return `{"status": "success"|"error"}` dict
   - Agents explicitly handle error states
   - No silent failures

6. **Improved Code Organization**
   ```
   news_info_verification_v2/
   ├── config.py              # Centralized configuration
   ├── agent.py               # Root agent factory
   ├── lanes/                 # Verification lanes
   │   ├── news_lane.py       # News verification
   │   ├── fact_lane.py       # Fact checking
   │   └── scam_lane.py       # Scam detection
   ├── tools/                 # FunctionTool wrappers
   │   ├── news_tools.py
   │   ├── fact_tools.py
   │   └── scam_tools.py
   ├── services/              # HTTP clients (external APIs)
   │   ├── gnews_client.py
   │   ├── factcheck_client.py
   │   ├── virustotal_client.py
   │   └── perplexity_client.py
   └── reporting/
       └── final_report.py    # Final synthesis agent
   ```

## 🏗️ Architecture

### Agent Hierarchy

```
RootAgent (LlmAgent)
├── NewsCheckAgent (SequentialAgent)
│   ├── NewsWorkerFanout (ParallelAgent)
│   │   ├── NewsApiWorker
│   │   ├── NewsFactWorker
│   │   └── NewsPerplexityWorker
│   └── NewsMerger
├── FactCheckAgent (SequentialAgent)
│   ├── FactWorkerFanout (ParallelAgent)
│   │   ├── FactPrimaryWorker
│   │   └── FactPerplexityWorker
│   └── FactMerger
├── ScamCheckAgent (SequentialAgent)
│   ├── ScamWorkerFanout (ParallelAgent)
│   │   ├── ScamLinkWorker
│   │   ├── ScamPerplexityWorker
│   │   └── ScamSentimentWorker
│   └── ScamMerger
└── FinalReportAgent
```

### Data Flow

1. **User Input** → RootAgent (routes to appropriate lanes)
2. **Parallel Fanout** → Each lane runs 2-3 workers concurrently
3. **Workers** → Call external APIs, write to session state
4. **Mergers** → Synthesize worker results into structured summaries
5. **Final Report** → Consolidates all lane summaries
6. **Output** → Comprehensive Markdown report returned to user

### Session State Keys

```python
@dataclass
class StateKeys:
    # News lane
    NEWS_API: str = "news_api_results"
    NEWS_FACT: str = "news_fact_results"
    NEWS_PERPLEXITY: str = "news_perplexity_results"
    NEWS_SUMMARY: str = "news_summary"
    
    # Fact lane
    FACT_PRIMARY: str = "fact_primary_results"
    FACT_PERPLEXITY: str = "fact_perplexity_results"
    FACT_SUMMARY: str = "fact_summary"
    
    # Scam lane
    SCAM_LINK: str = "scam_link_results"
    SCAM_PERPLEXITY: str = "scam_perplexity_results"
    SCAM_SENTIMENT: str = "scam_sentiment_results"
    SCAM_SUMMARY: str = "scam_summary"
    
    # Final output
    FINAL_REPORT: str = "final_report"
```

## 🚀 Setup

### Prerequisites

- Python 3.10+
- Google ADK (`google-adk`)
- API keys for external services

### Environment Variables

Create a `.env` file:

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# External APIs (at least one per lane recommended)
GNEWS_API_KEY=your_gnews_key
FACTCHECK_API_KEY=your_google_factcheck_key
VIRUSTOTAL_API_KEY=your_virustotal_key
PERPLEXITY_API_KEY=your_perplexity_key
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or manually
pip install google-adk requests python-dotenv
```

## 📖 Usage

### Basic Example

```python
from news_info_verification_v2 import create_root_agent

# Create agent
agent = create_root_agent()

# Verify a claim
response = agent.execute(
    "Is it true that coffee reduces cancer risk?"
)

print(response)
```

### With Session State

```python
from google.adk.core import Session

agent = create_root_agent()
session = Session()

# Execute with session
response = agent.execute(
    "Check if this news is real: 'New study shows...'",
    session=session
)

# Access intermediate results
news_summary = session.state.get("news_summary")
fact_summary = session.state.get("fact_summary")
scam_summary = session.state.get("scam_summary")
```

### Custom Configuration

```python
from news_info_verification_v2 import create_root_agent

# Use different model
agent = create_root_agent(model="gemini-1.5-pro")

# Or build custom agent composition
from news_info_verification_v2.lanes import (
    create_news_lane,
    create_fact_lane,
)

news_agent = create_news_lane(model="gemini-1.5-flash")
fact_agent = create_fact_lane(model="gemini-2.0-flash")
```

## 🧪 Testing

### Tool Testing

```python
from news_info_verification_v2.tools import fetch_news_evidence

# Test news API tool
result = fetch_news_evidence("climate change")
assert result["status"] == "success"
print(result["articles"])
```

### Agent Testing

```python
from news_info_verification_v2.lanes import create_news_lane

news_agent = create_news_lane()
response = news_agent.execute("Test news claim")
```

## 🔧 Extending

### Adding a New Tool

```python
# In tools/custom_tools.py
def my_custom_tool(request: str) -> dict:
    """Custom verification logic."""
    try:
        # Your implementation
        return {
            "status": "success",
            "data": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }

# Wrap in FunctionTool
from google.adk.tools import FunctionTool
MY_CUSTOM_TOOL = FunctionTool(my_custom_tool)
```

### Adding a New Lane

```python
# In lanes/custom_lane.py
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from ..config import MODEL, STATE_KEYS
from ..tools import MY_CUSTOM_TOOL

def create_custom_lane(model: str = MODEL) -> SequentialAgent:
    worker = LlmAgent(
        name="CustomWorker",
        model=model,
        instruction="Call my_custom_tool with the request",
        tools=[MY_CUSTOM_TOOL],
        output_key="custom_worker_result",
    )
    
    merger = LlmAgent(
        name="CustomMerger",
        model=model,
        instruction="Synthesize {custom_worker_result}",
        output_key="custom_summary",
    )
    
    return SequentialAgent(
        name="CustomLane",
        sub_agents=[worker, merger],
    )
```

Then add to root agent in `agent.py`:

```python
from .lanes import create_news_lane, create_fact_lane, create_scam_lane, create_custom_lane

def create_root_agent(model: str = MODEL) -> LlmAgent:
    news_lane = create_news_lane(model)
    fact_lane = create_fact_lane(model)
    scam_lane = create_scam_lane(model)
    custom_lane = create_custom_lane(model)  # Add here
    
    return LlmAgent(
        # ... add custom_lane_agent_tool to tools list
    )
```

## 📊 API Service Details

### GNews API
- **Purpose:** Licensed news article search
- **Endpoint:** `gnews.io/api/v4/search`
- **Rate Limit:** 100 requests/day (free tier)

### Google Fact Check Tools API
- **Purpose:** Fact-check database lookup
- **Endpoint:** `factchecktools.googleapis.com/v1alpha1/claims:search`
- **Rate Limit:** Based on Google Cloud quotas

### VirusTotal API
- **Purpose:** URL security scanning
- **Endpoint:** `www.virustotal.com/api/v3`
- **Rate Limit:** 4 requests/minute (free tier)

### Perplexity API
- **Purpose:** AI-powered web research
- **Endpoint:** `api.perplexity.ai/chat/completions`
- **Rate Limit:** Based on subscription tier

## 🐛 Troubleshooting

### "Could not parse function declaration"
- Ensure tool functions use only `request: str` parameter
- No complex type annotations (ToolContext, custom classes)
- Return type must be `dict`

### "API key not set"
- Check `.env` file is in project root
- Verify environment variable names match exactly
- Load dotenv: `from dotenv import load_dotenv; load_dotenv()`

### Missing intermediate results
- Verify `output_key` is set on worker agents
- Check session state keys match STATE_KEYS config
- Ensure agents are in sub_agents list of parent

## 📝 Best Practices

1. **Always use factory functions** - Don't instantiate agents directly
2. **Keep tool signatures simple** - Only `request: str` parameter
3. **Return structured dicts** - Always include `status` field
4. **Use state templating** - `{STATE_KEY}` in instructions
5. **Handle errors gracefully** - Try/except in all tool functions
6. **Document state keys** - Update STATE_KEYS when adding lanes
7. **Test tools independently** - Before integrating into agents

## 🔗 Resources

- [Google ADK Documentation](https://github.com/google/adk-toolkit)
- [ADK Concepts Guide](../llms-full.txt)
- [Original Implementation](../news_info_verification/)

## 📄 License

Same as parent project.

## 🤝 Contributing

When adding features:
1. Follow factory pattern for agents
2. Keep tool signatures simple (ADK compatible)
3. Update STATE_KEYS in config.py
4. Add tests for new tools
5. Document in this README

---

**Generated by ADK v1.0.0 | Gemini 2.0 Flash**
