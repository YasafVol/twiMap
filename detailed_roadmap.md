# twiMap Detailed Roadmap

*Philosophy: **Data First.** We validate the hardest part (LLM Text Extraction) before building the "nice to have" frontend.*

---

## Phase 1: The Raw Material
**Goal:** Secure the dataset locally.

### 1.1 Chapter Scraper
- [ ] **Script:** `scrape_chapters.py`
    - iterate through the Table of Contents.
    - fetch HTML, strip ads/nav.
    - **Output:** Flat folder structure: `data/raw/Vol_01/ch_1.00.txt`.

### 1.2 Validation
- [ ] Ensure all ~1200+ chapters are present.
- [ ] Basic spot checks for encoding issues.

---

## Phase 2: The Proof of Concept (LLM Pipeline)
**Goal:** Prove we can turn text into useful data.

### 2.1 The Pipeline
- [ ] **Chunker:** Split 20k word chapters into 2k word "scenes".
- [ ] **Prompt Engineering:**
    - Develop the "X-Ray" prompt (Summary, Characters, Event Type).
- [ ] **Prototype:**
    - Run on **1 Chapter** (Manual review).
    - Run on **10 Chapters** (Batch test).
    - Run on **Volume 1** (Full stress test).

### 2.2 Output
- [ ] Validated JSON files for Volume 1: `data/processed/Vol_01/ch_1.00.json`.

---

## Phase 3: The Context (Wiki Ingestion)
**Goal:** Get the canonical truth to cross-reference with our LLM data.

### 3.1 Wiki Scraper
- [ ] **Script:** `scrape_wiki.py`
    - Target: Characters, Locations, Classes.
    - **Output:** `data/wiki/characters.json` (Text only, no complex processing yet).

---

## Phase 4: The Schema
**Goal:** Define how this data lives in a database.

### 4.1 modeling
- [ ] **ER Diagram:**
    - `Chapter` (with raw text path).
    - `Scene` (the atomic unit of the graph).
    - `Character` (Canonical ID from Wiki).
    - `Appearance` (Link between Character and Scene).

---

## Phase 5: The Infrastructure
**Goal:** Move from JSON files to a real DB.

### 5.1 Deployment
- [ ] **Database:** Setup PostgreSQL to host the schema.
- [ ] **Ingestion Script:**
    - Load Wiki Data (First).
    - Load Processed LLM Data (Second, linking to Wiki IDs).

---

## Phase 6: Minimal UI
**Goal:** A read-only interface to browse the data.

### 6.1 Frontend
- [ ] **Tech:** Next.js.
- [ ] **Views:**
    - **Timeline:** List of scenes in order.
    - **Search:** Simple text search over summaries.

---

## Phase 7: The Graph
**Goal:** Visualizing connections.

### 7.1 Graph Logic
- [ ] **Edges:** `Character` -> `Scene` -> `Location`.
- [ ] **UI:** Interactive network visualization using a library like `react-force-graph`.

---

## Phase 8: Scale
**Goal:** Process the rest of the 12M words.

### 8.1 Batch Job
- [ ] Run the Phase 2 pipeline on Volumes 2-10 (Likely overnight jobs).
- [ ] Ingest results into DB.
