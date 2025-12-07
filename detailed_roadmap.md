# twiMap Detailed Roadmap (v2)

*Philosophy: **Data First & Quality Controlled.** We validate the hardest part (LLM Text Extraction) using a controlled vocabulary from the Wiki.*

---

## Phase 1: Foundation (Week 1)
**Goal:** Secure the raw text and the "Canonical Truth" (Wiki data).

### 1.1 Chapter Scraper
- [ ] **Script:** `scrape_chapters.py`
    - iterate through the Table of Contents.
    - **Output:** `data/raw/Vol_01/ch_1.00.txt`.

### 1.2 Wiki Scraper (The Context Layer)
- [ ] **Script:** `scrape_wiki.py`
    - Target: Characters, Locations, Classes.
    - **Output:** `data/wiki/characters.json` (List of known entities).
- [ ] **Entity Normalization:**
    - Create a "Canonical Lookup" to help the LLM fix typos ("Erin Solstace" -> "Erin Solstice").

---

## Phase 2: The Proof of Concept (Weeks 2-3)
**Goal:** Prove we can turn text into high-quality data.

### 2.1 The Pipeline
- [ ] **Chunker:** Handle special formatting (POVs, long blocks).
- [ ] **Prompt Engineering:**
    - **Input:** 2k word chunk + List of known Characters (from Phase 1).
    - **Output:** JSON with normalized names.

### 2.2 Tooling (The Admin UI)
*Crucial: We cannot review 12M words via JSON files.*
- [ ] **Review Interface:**
    - Simple local web page to show: Left (Raw Text) | Right (LLM Extract).
    - [Approve] / [Edit] buttons.

### 2.3 Validation
- [ ] **Experiment:** Run on 1 complex chapter (e.g., 1.00).
- [ ] **Volume 1 Batch:** Processing ~40-50 chapters.
- [ ] **Quality Gate:**
    - >95% Character Identification Accuracy.
    - <5% Hallucinated Events.

---

## Phase 3: Minimal Data Layer (Week 4)
**Goal:** Store the clean data in a queryable format.

### 3.1 Schema (v1)
*Keep it simple.*
- [ ] **Tables:** `chapters`, `scenes`, `characters`.
- [ ] **Storage:** PostgreSQL.

### 3.2 API
- [ ] **Rest API:** Simple endpoints to fetch data for the frontend.
    - `GET /chapters`
    - `GET /search?q=...`

---

## Phase 4: Minimal UI (Weeks 5-6)
**Goal:** A read-only interface to browse the data.

### 4.1 Frontend
- [ ] **Tech:** Next.js.
- [ ] **Views:**
    - **Timeline:** List of scenes in order.
    - **Search:** Simple full-text search.

---

## Phase 5: Scale
**Goal:** Process the rest of the 12M words.

### 5.1 Batch Job
- [ ] Run the verified pipeline on Volumes 2-10.
- [ ] Ingest results into DB.

---

## Technical Stack Choices
- **Language:** TypeScript / Python (for scripting).
- **DB:** PostgreSQL.
- **Search:** Postgres Full-Text (Start simple).
- **LLM:** GPT-4o-mini (Cost efficient) + Caching.
