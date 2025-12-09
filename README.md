# twiMap

**twiMap** is an ambitious project to build a comprehensive, LLM-powered knowledge graph for the web serial "The Wandering Inn" (~12M+ words).

## Project Goal
Create a traversable visual map and timeline of characters, locations, and events.
- **Phase 1 (Foundation):** Text Extraction & Canonical Entity Lists.
- **Phase 2 (Prototype):** Proof of Concept (LLM Extraction Pipeline).
- **Phase 3+:** Database, API, and Frontend.

## Setup
1. **Clone Repo:**
   ```bash
   git clone https://github.com/YasafVol/twiMap.git
   cd twiMap
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: You'll need `openai` or `google-generativeai` later).*

## Usage

### 1. Scrape Chapters
Download raw text from wanderinginn.com.
```bash
python3 scrape_chapters.py
```
*Outputs to `data/raw/Vol_XX/`.*

### 2. Scrape Wiki Data
Fetch canonical characters and locations for validation.
```bash
python3 scrape_wiki.py
```
*Outputs to `data/wiki/`.*

### 3. Chunk Text
Split chapters into manageable scenes for LLM processing.
```bash
python3 chunk_chapters.py
```
*Outputs to `data/processed/Vol_XX/chunks.json`.*

### 4. Extract Entities (Upcoming)
Run the LLM pipeline to extract structured data.
```bash
python3 extract_entities.py
```

## Directory Structure
- `data/raw/`: Original chapter text and volume indices.
- `data/wiki/`: Canonical character/location lists.
- `data/processed/`: Chunked scenes ready for processing.
