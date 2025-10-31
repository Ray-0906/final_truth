# Prompting Improvements Applied

This document describes the best practices applied to the News Info Verification agent based on the article: [How to build your agent: 11 prompting techniques for better AI agents](https://www.augmentcode.com/blog/how-to-build-your-agent-11-prompting-techniques-for-better-ai-agents)

## Summary of Changes

We refactored all agent instructions following these principles from the article:

### 1. **Focus on Context First** ✅
**Before:** Minimal context, just task description
```python
instruction="""Call lookup_fact_checks with the user's claim.
Return the exact JSON response - do not modify it."""
```

**After:** Complete environment and resource description
```python
instruction="""You are a fact-check database specialist with access to the lookup_fact_checks tool.

**YOUR TASK:**
Search fact-check databases for previous verifications of the user's claim.

**TOOL BEHAVIOR:**
Searches Google Fact Check Tools API for fact-check articles from major organizations:
- Snopes, PolitiFact, FactCheck.org, AFP Fact Check, Reuters Fact Check, etc.
- Results include claim text, rating (TRUE/FALSE/MIXED), and review URLs
..."""
```

**Impact:** Agents understand their role, available resources, and expected outcomes.

---

### 2. **Present a Complete Picture of the World** ✅
**Applied to:** Root agent, all worker agents, all merger agents

**Key additions:**
- "You are [role] with access to [tools]"
- "Your environment: [context about what they're processing]"
- "Your resources: [list of available tools/agents]"
- "Tool behavior: [what the tool does and returns]"

**Example (Root Agent):**
```python
instruction="""You are an AI content verification router with access to three specialized verification agents.

**YOUR RESOURCES:**
You have access to these verification agents (as tools):
- NewsCheckAgent: Verifies current events by checking news APIs, fact-check databases, and web research
- FactCheckAgent: Verifies general factual claims through fact-check registries and research
- ScamCheckAgent: Detects scams by analyzing URLs, known patterns, and manipulation tactics

**YOUR ENVIRONMENT:**
- You are processing user-submitted claims that may be true, false, scams, or misleading
- Each agent runs a complete verification pipeline (parallel workers + merger)
- Tool calls will return structured Markdown reports with verdict, confidence, and evidence
..."""
```

---

### 3. **Be Consistent Across Prompt Components** ✅
**Applied to:** Tool definitions, instructions, error messages

**Consistency maintained:**
- All workers return JSON: `{"status": "success"|"error", "data": {...}}`
- All mergers receive state variables with consistent naming
- Error handling language matches across workers and mergers
- URL preservation rule stated explicitly in every merger
- Stop conditions phrased consistently

**Example:**
```python
# Worker instruction
"If tool returns status='error', return that response exactly."

# Merger instruction  
"If a worker has status='error', note it in Analysis Notes but don't fail"
```

---

### 4. **Be Thorough** ✅
**Applied to:** All merger agents, classification logic

**Before:** Short, vague instructions (4-5 lines)

**After:** Comprehensive guides (50-100 lines) covering:
- Input data structure
- Output format with examples
- Decision logic (verdict determination)
- Scoring rubrics (confidence calculation)
- Error handling scenarios
- Edge cases and conflicts
- What NOT to do

**Example (Fact Merger):**
- Full Markdown template with placeholders
- Verdict determination logic (5 verdict types explained)
- Confidence scoring rubric (5 ranges with criteria)
- Category classification (6 categories defined)
- 7 critical rules enumerated
- Error handling for partial/complete failures

---

### 5. **Consider Tool Calling Limitations** ✅
**Applied to:** Error handling in all workers

**Key insight from article:**
> "Models will often call tools in incorrect ways... It is best to validate the input, and return a tool output that explains the error in case of failure. The model will generally recover."

**Our implementation:**
```python
**ERROR HANDLING:**
If tool returns status='error', return that response exactly. Common errors:
- API rate limit exceeded
- Invalid claim format
- Network connectivity issues

The merger will work with whatever data is available.
```

**Also applied:**
- Workers don't try to fix tool errors
- Mergers gracefully handle missing/error data
- All error messages returned as tool outputs (not exceptions)
- Clear examples of what errors look like

---

### 6. **Avoid Overfitting to Specific Examples** ✅
**Applied to:** Classification rules in root agent

**Before:** Too many specific examples
```python
- "Cyclone hit Andhra Pradesh"
- "Woman died in village"  
- "Celebrity died yesterday"
```

**After:** General patterns with 1-2 examples per category
```python
1. **News claims** → NewsCheckAgent
   - Time-sensitive: breaking news, recent events, current incidents
   - Named events: disasters, political announcements, media coverage
   - Examples: "Cyclone hit Andhra Pradesh", "Celebrity died yesterday"
```

**Rationale:** Too many examples cause models to overfit and reject valid inputs that don't match the examples exactly.

---

### 7. **Models Pay More Attention to the End** ✅
**Applied to:** Critical stop conditions, rules at end of prompts

**Pattern used throughout:**
```python
instruction="""[Context and task description]

[Detailed workflow]

[Output format]

**CRITICAL RULES:** [Most important rules here]
- Rule 1
- Rule 2

**STOP CONDITION:**  [Termination signal at the very end]
Your job is complete when... Do not continue after this point.
"""
```

**Why:** The article states user messages and end of prompts get highest attention. We put stop signals and critical rules at the end.

---

### 8. **Be Aware of Prompt Caching** ✅
**Applied to:** Static structure in instructions

**Implementation:**
- All instructions are static (no dynamic timestamps, state)
- State variables referenced by key names, not values
- Instructions don't change during session
- Tool definitions are stable

**Example:**
```python
# Good - static reference
f"""The session state contains these two worker outputs:
- {{{STATE_KEYS.FACT_PRIMARY}}}: Fact-check database results
- {{{STATE_KEYS.FACT_PERPLEXITY}}}: Web research results"""

# Bad - would invalidate cache
f"""Current time: {datetime.now()} - The session state..."""
```

---

### 9. **Explicit Stop Conditions to Avoid Loops** ✅
**Applied to:** Root agent and all workers

**The Problem (from article):**
> "Router prompt keeps re-running because it never emits a terminal message"

**Our Solution:**
```python
**STOP CONDITION:**
Your job is complete when you have received and returned ONE agent's verification report. 
Do not continue after this point.
```

**Also added:**
- "Do not loop"
- "Do not re-classify after getting a response"  
- "Return immediately after tool response"
- "This is a single-pass operation"

---

### 10. **Align the Model with User's Perspective** ✅
**Applied to:** Root agent classification, merger reports

**Implementation:**
- Classification examples match real user claims
- Output format is user-facing Markdown (not technical JSON)
- Risk levels explained in user-friendly terms
- Recommended actions phrased as user guidance

**Example (Scam Merger):**
```markdown
### Recommended Actions
- Do NOT click links, do NOT send money, report to authorities, block sender
- Avoid interaction, verify through official channels, report suspicious activity
```

---

### 11. **Error Handling as Tool Outputs** ✅
**Applied to:** All workers and mergers

**Pattern:**
```python
# Workers
"If tool returns status='error', return that response exactly. Do not try to fix it."

# Mergers  
"If ALL workers returned errors:
```markdown
## [Type] Report
**Verdict:** unverified
**Confidence:** 0.0
...
### Error Summary
* Worker 1: [error message]
* Worker 2: [error message]
```"
```

**No exceptions raised** - all errors communicated through tool output interface.

---

## Files Modified

### Root Agent
- `agent.py`: Complete rewrite with environment description, resources, classification logic, explicit stop condition

### News Lane
- `lanes/news_lane.py`:
  - `api_worker`: Added query extraction rules, examples, error handling
  - `fact_worker`: Added tool behavior description, ratings explanation
  - `perplexity_worker`: Added tool behavior, error scenarios
  - `news_merger`: 90-line comprehensive instruction with format, logic, scoring, rules

### Fact Lane
- `lanes/fact_lane.py`:
  - `primary_worker`: Added database description, rating types, error handling
  - `perplexity_worker`: Added research scope, expected output, error scenarios
  - `fact_merger`: 110-line comprehensive instruction with verdict logic, confidence scoring, category classification

### Scam Lane
- `lanes/scam_lane.py`:
  - `link_worker`: Added threat level interpretation, VirusTotal behavior, URL extraction logic
  - `perplexity_worker`: Added scam type taxonomy, pattern matching description
  - `sentiment_worker`: Added manipulation tactic taxonomy, sentiment scoring explanation
  - `scam_merger`: 130-line comprehensive instruction with threat assessment, risk levels, recommended actions

---

## Expected Improvements

### 1. **Reduced Infinite Loops**
- Explicit stop conditions prevent re-prompting
- Root agent knows when job is complete

### 2. **Better Error Recovery**
- Workers return errors as data, not exceptions
- Mergers handle partial failures gracefully
- Users get informative error reports

### 3. **More Consistent Outputs**
- Detailed format specifications with examples
- Consistent verdict/confidence/category structures
- Standardized Markdown templates

### 4. **Improved Classification**
- Clear decision trees with general patterns
- Less overfitting to specific examples
- Better handling of ambiguous cases

### 5. **Faster Execution**
- Prompt caching effective (static instructions)
- Workers stop immediately after tool call
- No unnecessary re-analysis

### 6. **Higher Quality Reports**
- Comprehensive coverage of all data sources
- Cross-referencing between workers
- Clear confidence scoring methodology
- User-friendly recommendations

---

## Testing Recommendations

1. **Loop Prevention:** Test that root agent stops after one tool call
2. **Error Handling:** Test with API keys disabled to verify error reports
3. **Classification:** Test edge cases (ambiguous claims, multiple categories)
4. **Partial Failures:** Test with one worker failing, two workers failing
5. **Confidence Scoring:** Verify confidence aligns with verdict strength
6. **Format Compliance:** Check all outputs match Markdown templates

---

## References

- **Article:** [How to build your agent: 11 prompting techniques for better AI agents](https://www.augmentcode.com/blog/how-to-build-your-agent-11-prompting-techniques-for-better-ai-agents)
- **Author:** Guy Gur-Ari (Augment Code)
- **Key Insight:** "Mastering prompt engineering is less about tricks and more about disciplined communication: give the agent complete, consistent context; validate its actions the way you would an untrusted colleague; and iterate empirically."

---

## Metrics to Track

- **Loop incidents:** Should be zero with explicit stop conditions
- **Error recovery rate:** Percentage of errors handled gracefully vs crashes
- **Output format compliance:** Percentage of outputs matching Markdown template
- **Confidence accuracy:** Correlation between confidence score and verdict correctness
- **Response time:** Should be similar (caching helps, thoroughness increases tokens)

---

*Document created: 2025-10-31*
*Last updated: 2025-10-31*
