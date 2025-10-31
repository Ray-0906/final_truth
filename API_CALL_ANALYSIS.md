# API Call Analysis - News Verification Agent

## Analysis Date: October 31, 2025

---

## 📊 Current API Status

### ✅ Working APIs:

1. **GNews API** (`fetch_news_evidence`)
   - **Status:** ✅ WORKING CORRECTLY
   - **Evidence:** Tool is being called properly
   - **Example:**
     ```
     Tool call: fetch_news_evidence('Trump Asia pacts...')
     Result: {'status': 'success', 'articles': [...]}
     ```
   - **Output:** Successfully retrieved article from The Indian Express

2. **Google Fact Check API** (`check_factcheck_api`)
   - **Status:** ✅ WORKING CORRECTLY  
   - **Evidence:** Tool is being called properly
   - **Example:**
     ```
     Tool call: check_factcheck_api('Trump's visit to Asia...')
     Result: {'status': 'success', 'claims': []}
     ```
   - **Output:** API call successful (empty results are valid - means no fact-checks exist for this claim yet)

---

### ❌ Issue Found:

3. **Perplexity API** (`research_news_with_perplexity`, `research_fact_with_perplexity`, `research_scam_with_perplexity`)
   - **Status:** ❌ **NOT BEING CALLED**
   - **Problem:** LLM is bypassing the tool and generating fake responses
   - **Evidence from logs:**
     ```
     [NewsPerplexityWorker] said: ```json
     {
       "status": "success",
       "answer": "Several sources discuss Trump's policies...",
       "citations": [...]
     }
     ```
   - **What should happen:**
     ```
     [NewsPerplexityWorker] called tool `research_news_with_perplexity`
     [NewsPerplexityWorker] tool returned result: {...}
     ```
   - **Root Cause:** gemini-2.0-flash is smart enough to fabricate plausible-looking research instead of calling the actual API
   - **Risk:** The citations and research results are **HALLUCINATED**, not real

---

## 🔧 Fix Applied

### Updated All Perplexity Worker Instructions:

**Added explicit warnings:**
```
**CRITICAL: YOU MUST CALL THE TOOL**
You do NOT have internet access yourself. You MUST call the research_xxx_with_perplexity tool to get real web data.
DO NOT generate or fabricate research results. ONLY return what the tool provides.
```

**Added reminder:**
```
**REMEMBER:** You cannot research the web yourself. You MUST use the tool.
```

### Files Modified:
1. ✅ `lanes/news_lane.py` - NewsPerplexityWorker
2. ✅ `lanes/fact_lane.py` - FactPerplexityWorker  
3. ✅ `lanes/scam_lane.py` - ScamPerplexityWorker

---

## 🧪 Testing Required

### To verify the fix works:

1. **Restart the ADK server:**
   ```powershell
   cd c:\Users\astra\Desktop\ADk\news_info_verification_v2
   adk web
   ```

2. **Submit a test claim** (use the web UI or API)

3. **Check the logs for Perplexity workers** - You should now see:
   ```
   [NewsPerplexityWorker] called tool `research_news_with_perplexity` 
   with parameters: {'request': '...'}
   
   [NewsPerplexityWorker] `research_news_with_perplexity` tool returned result: {...}
   ```

4. **What you should NOT see:**
   ```
   [NewsPerplexityWorker] said: ```json {...}```
   ```

---

## 📈 Expected Behavior After Fix

### News Lane (all 3 workers should call tools):
| Worker | Tool Called | Expected |
|--------|-------------|----------|
| NewsApiWorker | ✅ `fetch_news_evidence` | GNews articles |
| NewsFactWorker | ✅ `check_factcheck_api` | Fact-check records |
| NewsPerplexityWorker | ✅ `research_news_with_perplexity` | **Real Perplexity research** |

### Fact Lane:
| Worker | Tool Called | Expected |
|--------|-------------|----------|
| FactPrimaryWorker | ✅ `check_factcheck_api` | Fact-check records |
| FactPerplexityWorker | ✅ `research_fact_with_perplexity` | **Real Perplexity research** |

### Scam Lane:
| Worker | Tool Called | Expected |
|--------|-------------|----------|
| ScamLinkWorker | ✅ `scan_urls_with_virustotal` | URL security scan |
| ScamPerplexityWorker | ✅ `research_scam_with_perplexity` | **Real Perplexity research** |
| ScamSentimentWorker | ✅ `analyze_scam_sentiment` | Manipulation tactics |

---

## 🔍 How to Verify Perplexity is Being Called

### Check 1: Environment Variable
Make sure you have a valid Perplexity API key in `.env`:
```bash
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxx
```

### Check 2: Look for Function Call in Logs
**CORRECT** (tool is called):
```
{"parts":[{"function_call":{"args":{"request":"..."},"name":"research_news_with_perplexity"}}],"role":"model"}
```

**WRONG** (tool is bypassed):
```
{"parts":[{"text":"```json\n{\"status\": \"success\", ..."}],"role":"model"}
```

### Check 3: Check for API Errors
If Perplexity API key is missing or invalid, you should see:
```json
{
  "status": "error",
  "error": "PERPLEXITY_API_KEY environment variable not set"
}
```

---

## 🎯 Summary

### Before Fix:
- ✅ GNews API: Working
- ✅ Fact Check API: Working  
- ❌ Perplexity API: **NOT being called** (LLM hallucinating responses)

### After Fix:
- ✅ GNews API: Working
- ✅ Fact Check API: Working
- ✅ Perplexity API: **Should now be called properly** (needs testing)

### Next Steps:
1. Restart `adk web`
2. Test with a claim
3. Verify logs show tool calls for all 3 Perplexity workers
4. Confirm responses contain real Perplexity data (not hallucinations)

---

*Generated: 2025-10-31*
*Issue: Perplexity workers bypassing tool calls*
*Fix: Added explicit instructions forcing tool usage*
