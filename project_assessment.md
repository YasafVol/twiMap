# twiMap Project Assessment

## Executive Summary

**Project Scope:** Build an LLM-powered knowledge graph and exploration interface for The Wandering Inn web serial (~12-15M words, 1200+ chapters, 1200+ characters).

**Verdict:** ✅ **Ambitious but achievable** with the right scoping and risk mitigation.

**Key Insight:** Your "Data-First" execution order is strategically sound. It validates the hardest unknowns (LLM extraction quality) before over-investing in infrastructure.

---

## Alignment Check: Project Plan vs Roadmap

### ✅ Strong Alignment
- Both documents correctly prioritize **LLM validation** before full-scale engineering
- Private use model eliminates copyright risk
- Phased approach allows for iteration

### ⚠️ Minor Gaps to Address
1. **Wiki scraping timing:** Original plan suggested scraping wiki *before* schema. Your roadmap has it as Phase 3. 
   - **Recommendation:** Move to **Phase 1.3** (before LLM testing). Reason: You need canonical entity lists (characters, locations) to feed into the LLM prompt as a "controlled vocabulary".

2. **Schema definition:** Roadmap Phase 4 feels late for this.
   - **Recommendation:** Draft a **lightweight v1 schema in Phase 2** (just enough to store LLM outputs). Iterate as you learn.

---

## Risk Analysis

### 🔴 Critical Risks

#### 1. **LLM Output Quality (Highest Risk)**
**Problem:** LLMs hallucinate. With 1200+ characters, expect:
- Misspelled names ("Erin Solstace" instead of "Erin Solstice")
- Invented events
- Inconsistent tagging across chapters

**Mitigation:**
- ✅ Your plan already includes manual review UI (good!)
- Add: **Entity normalization layer** (fuzzy matching against Wiki canonical list)
- Add: **Confidence scores** in LLM output so you can flag low-confidence extractions

#### 2. **Cost ($$$)**
**Problem:** 12M words × chunking × multiple LLM passes = expensive.

**Back-of-envelope:**
- 12M words ≈ 16M tokens (input)
- Split into ~2k word scenes: 6,000 scenes
- Per-scene extraction: ~3k tokens in, ~500 tokens out
- **Total:** ~21M input tokens, ~3M output tokens

At GPT-4o-mini pricing ($0.15/$0.60 per 1M tokens):
- Input: 21M × $0.15 = **~$3.15**
- Output: 3M × $0.60 = **~$1.80**
- **Total: ~$5 for the full corpus** (surprisingly cheap!)

At Claude 3.5 Haiku ($1/$5 per 1M tokens):
- **Total: ~$36**

**Mitigation:**
- Start with cheaper models (GPT-4o-mini, Haiku)
- Cache aggressively (don't re-run on schema tweaks; post-process the JSON)
- Batch API calls to lower costs

#### 3. **Time Investment**
**Problem:** This is a multi-month project, not a weekend hack.

**Estimated timelines:**
- Phase 1 (Scraping): 1-2 days
- Phase 2 (LLM Prototype + Vol 1): 1-2 weeks (including prompt tuning)
- Phase 3 (Wiki): 2-3 days
- Phase 4 (Schema): 1 week
- Phase 5 (DB): 3-4 days
- Phase 6 (UI): 2-3 weeks
- Phase 7 (Graph): 1 week
- Phase 8 (Scale): 1 week

**Total: 2-3 months of focused part-time work**

---

### 🟡 Medium Risks

#### 4. **Chunking Heuristics**
The Wandering Inn has unusual formatting (long dialogue blocks, POV shifts mid-chapter).

**Mitigation:**
- Test chunker on 5-10 diverse chapters manually
- Consider keeping `<hr>` tags and "---" separators as strong scene boundaries

#### 5. **Spoiler Propagation**
A character appearing in Ch 100 might spoil events from Ch 50.

**Mitigation:**
- Implement `earliest_spoiler_chapter` tracking at the entity relationship level, not just the entity
- Example: "Ryoka is alive" isn't a spoiler, but "Ryoka and Erin meet" is a Ch 1 spoiler, while "Ryoka meets Flos" is a Vol 7 spoiler

---

### 🟢 Low Risks
- **Tech stack:** Next.js + Postgres + pgvector is battle-tested
- **Data availability:** Wiki and TOC are well-maintained

---

## Strategic Recommendations

### 1. **Reorder Phase 3 → Phase 1.3**
Scrape the wiki *before* running the LLM. Use it to:
- Build a canonical entity lookup (characters, locations, classes)
- Feed this as context to the LLM prompt: "Here are known characters. Match names to this list."

### 2. **Start Schema in Phase 2**
Don't wait until Phase 4. Create a minimal schema for:
```sql
chapters(id, volume, title, url, raw_text_path)
scenes(id, chapter_id, index, raw_text, llm_output_json)
```
This lets you store LLM outputs immediately and defer the "fancy" relational model.

### 3. **Add a "Quality Gate" to Phase 2**
Before moving to Phase 8 (scaling), define success metrics for Volume 1:
- ✅ 95%+ of named characters correctly identified
- ✅ Less than 5% hallucinated events (baseline: manual spot-checks)
- ✅ POV detection accuracy >90%

If you don't hit these, iterate on the prompt/chunker before scaling.

### 4. **Prototype the Hardest Part First**
Pick **one complex chapter** with:
- Multiple POVs
- Battle scene + political scene + downtime
- 10+ named characters

Run it through the pipeline manually. If this works well, the rest will follow.

**Suggested test chapter:** Volume 1, Chapter 1.00 (has Erin's arrival, multiple location shifts, introduces core mechanics)

### 5. **Build the Admin Review UI Early**
Phase 2 needs a **review interface** before you process 100 chapters. Simple UI:
```
[Raw Text]               [LLM Output]
Scene 3 of Ch 1.01       {
Erin walked into...        "summary": "...",
                           "characters": [...],
                         }
                         [Approve] [Edit] [Reject]
```

---

## Technical Debt Watch

Things you can **defer** to stay lean:

- ❌ GraphQL API (use simple REST for prototyping)
- ❌ Vector search (defer to Phase 8)
- ❌ Meilisearch (start with Postgres full-text search)
- ❌ Neo4j (use Postgres with edge tables first)

Things you **cannot** defer:
- ✅ Entity normalization
- ✅ Manual review tooling
- ✅ Caching layer for LLM responses
- ✅ Spoiler tracking (core to UX)

---

## Suggested Roadmap v2

### Phase 1: Foundation (Week 1)
1.1. Scrape all chapters → `data/raw/`  
1.2. Scrape wiki → `data/wiki/characters.json`  
1.3. Create canonical entity lookup

### Phase 2: The Prototype (Weeks 2-3)
2.1. Build chunker  
2.2. Design LLM prompt with controlled vocabulary  
2.3. Test on **1 complex chapter** (manual review)  
2.4. Build admin review UI  
2.5. Run on **Volume 1** (100-200 chapters)

**Exit Criteria:** 90%+ extraction quality on Vol 1

### Phase 3: Minimal Schema (Week 4)
3.1. Define schema v1 (just enough to query)  
3.2. Load Vol 1 into Postgres  
3.3. Build basic REST API (2-3 endpoints)

### Phase 4: Minimal UI (Weeks 5-6)
4.1. Next.js setup  
4.2. Chapter list + Scene viewer  
4.3. Basic search

### Phase 5: Scale (Week 7)
5.1. Batch process remaining volumes  
5.2. Ingest into DB

### Phase 6: Graph (Week 8)
6.1. Build edge tables  
6.2. Character network UI

---

## Conclusion

**Go/No-Go:** ✅ **GO**

This is a **tractable 2-3 month project** if you:
1. Validate LLM quality on Volume 1 before scaling
2. Build the admin review UI early
3. Keep infrastructure simple (defer GraphQL, vector search, etc.)

**Biggest wildcard:** LLM extraction accuracy. Everything else is just engineering.

If Phase 2 goes well, the rest is a victory lap.
