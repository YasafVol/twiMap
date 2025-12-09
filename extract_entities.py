import json
import os
import time
import random
from zhipuai import ZhipuAI
from typing import List, Dict, Any
from dotenv import load_dotenv

# Explicitly load from current directory to be safe
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# --- CONFIGURATION ---
DATA_DIR = "data/processed"
WIKI_DIR = "data/wiki"
OUTPUT_DIR = "data/processed"

# You will need to set this env var or pass it in
API_KEY = os.environ.get("GLM_API_KEY")

# --- MOCK DATA ---
MOCK_CHARACTERS = ["Erin Solstice", "Relc", "Klbkch", "Pisc", "Ceria Springwalker"]
MOCK_LOCATIONS = ["The Wandering Inn", "Liscor", "Floodplains"]

def mock_generate_content(chunk_text: str):
    """Generates deterministic mock data for testing."""
    chars = []
    # Simple heuristic to make it look real
    if "Erin" in chunk_text:
        chars.append({"name": "Erin Solstice", "type": "known", "confidence": 1.0, "context": "Protagonist"})
    if "Dragon" in chunk_text:
        chars.append({"name": "Dragon", "type": "new", "confidence": 0.9, "context": "Antagonist in cave"})
    if "Goblins" in chunk_text:
        chars.append({"name": "Goblins", "type": "known", "confidence": 0.8, "context": "Attackers"})
        
    return json.dumps({
        "characters": chars,
        "locations": [{"name": "The Wandering Inn"}]
    })

# Configure Client
if not API_KEY:
    print("WARNING: GLM_API_KEY not found. Defaulting to MOCK MODE.")
    USE_MOCK = True
    client = None
else:
    client = ZhipuAI(api_key=API_KEY)
    USE_MOCK = False # Can force this to True for debugging

MODEL_NAME = "glm-4.6" 

# --- UTILS ---

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_known_characters_list(char_data: List[Dict]) -> str:
    names = [c["title"] for c in char_data if "title" in c]
    return ", ".join(names)

def construct_prompt(chunk_text: str, known_characters: str) -> str:
    return f"""
    You are an expert Data Historian constructing a Knowledge Graph for "The Wandering Inn".
    
    TASK:
    Analyze the provided story snippet (SCENE) and extract all Characters present or mentioned.
    
    CONTEXT:
    We have a database of "KNOWN CHARACTERS" from the Wiki. 
    - If you find a name from this list, use the exact spelling.
    - If you find a NEW character not in the list, extract them but mark as "new".
    - Be careful with aliases (e.g., "The Necromancer" might be "Az’kerash"). Use the canonical name if clearly implied, or list the alias.
    
    KNOWN CHARACTERS (Reference):
    {known_characters[:100000]} 
    (List truncated if needed, GLM-4 has 128k context)

    SCENE TEXT:
    {chunk_text}

    OUTPUT FORMAT (JSON ONLY):
    {{
      "characters": [
        {{ "name": "Canonical Name", "type": "known|new", "confidence": 0.95, "context": "Brief reason (e.g. 'mentioned as The Necromancer')" }}
      ],
      "locations": [
        {{ "name": "Location Name" }}
      ]
    }}
    
    If no entities are found, return empty lists.
    """

def run_extraction_batch(volume_name, force_mock=False):
    is_mock = USE_MOCK or force_mock
    print(f"Starting extraction for {volume_name} (Mode: {'MOCK' if is_mock else MODEL_NAME})...")
    
    # 1. Load Data
    chunks_path = os.path.join(DATA_DIR, volume_name, "chunks.json")
    if not os.path.exists(chunks_path):
        print(f"Chunks not found for {volume_name}")
        return

    chunks = load_json(chunks_path)
    
    chars_path = os.path.join(WIKI_DIR, "characters.json")
    known_chars_data = load_json(chars_path)
    known_chars_str = get_known_characters_list(known_chars_data)
    
    output_path = os.path.join(OUTPUT_DIR, volume_name, "extracted_entities.json")
    
    # Load existing to resume if needed
    extracted_data = load_json(output_path)
    processed_ids = set(item["chunk_id"] for item in extracted_data)
    
    count = 0
    
    for chunk in chunks:
        # Chapter 1 filter
        if chunk.get("chapter_title") != "1.00" and not str(chunk.get("chapter_title")).startswith("1.00"):
                 continue

        # Resume check
        if chunk["chunk_id"] in processed_ids:
            continue
            
        print(f"Processing Chunk {chunk['chunk_id']} ({chunk['chapter_title']})...")
        
        prompt = construct_prompt(chunk["text"], known_chars_str)
        
        try:
            content = ""
            if is_mock:
                content = mock_generate_content(chunk["text"])
                time.sleep(0.1) # Fast!
            else:
                # Generate with GLM-4
                response = client.chat.completions.create(
                    model=MODEL_NAME, 
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    top_p=0.7,
                    temperature=0.1,
                    max_tokens=2000
                )
                content = response.choices[0].message.content
            
            # Basic cleanup if code blocks are returned
            if "```json" in content:
                content = content.replace("```json", "").replace("```", "")
            
            # Parse result
            try:
                result_json = json.loads(content)
            except json.JSONDecodeError:
                print("  [ERROR] Invalid JSON from LLM. Skipping.")
                result_json = {"error": "Invalid JSON", "raw": content}
                
            # Combine with metadata
            combined_record = {
                "chunk_id": chunk["chunk_id"],
                "chapter_order": chunk["chapter_order"],
                "scene_index": chunk["scene_index"],
                "extraction": result_json
            }
            
            extracted_data.append(combined_record)
            
            # Save incrementally (every 5 chunks)
            if len(extracted_data) % 5 == 0:
                save_json(extracted_data, output_path)
                print(f"  Saved progress ({len(extracted_data)} chunks).")
                
            # Rate limiting
            if not is_mock:
                time.sleep(1) 
            
            count += 1

        except Exception as e:
            print(f"  [ERROR] API Failure: {e}")
            if not is_mock:
                print("  Sleeping for 60s...")
                time.sleep(60)
            
    # Final save
    save_json(extracted_data, output_path)
    print("Done.")

if __name__ == "__main__":
    # You can force mock with a flag if needed, but for now defaulting logic:
    run_extraction_batch("Vol_01", force_mock=True)
