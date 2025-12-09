import json
import os
import re

# Configuration
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
MAX_TOKENS_PER_CHUNK = 4000  # Rough estimate (~4 chars per token)
CHARS_PER_TOKEN = 4
MAX_CHARS = MAX_TOKENS_PER_CHUNK * CHARS_PER_TOKEN

def load_chapter(filepath):
    """Loads raw text from a chapter file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def split_into_scenes(text):
    """
    Splits text into scenes based on TWI conventions.
    Separators: 
    - <hr> (if HTML was kept, but we have raw text)
    - *** or * * *
    - ——— (long dash lines)
    - Double newlines with clear visual separators
    """
    # Regex for common scene separators in TWI
    # 1. 3 or more asterisks with optional spaces
    # 2. 3 or more dashes
    # 3. The specific "Next Chapter" text (usually at end, can be treated as a break or ignored)
    
    # We will use a placeholder for splitting
    separator_pattern = r"\n\s*(\*[\s\*]*\*|—+|–+|_hv_)\s*\n"
    
    # Pre-process some known weirdness if any found during inspection
    # For now, standard regex approach
    
    scenes = re.split(separator_pattern, text)
    
    # The split returns [scene1, separator1, scene2, separator2, ...]
    # We want to re-assemble or just take the scenes. 
    # TWI separators are usually just visual breaks. We can discard the separator itself 
    # or keep it as metadata. Let's discard for clean text, but maybe mark it.
    
    clean_scenes = []
    current_scene_parts = []
    
    for part in scenes:
        part = part.strip()
        # detecting if it is a separator match
        if re.match(r"^(\*[\s\*]*\*|—+|–+|_hv_)$", part):
            continue # Skip the separator text itself
            
        if part:
            clean_scenes.append(part)
            
    return clean_scenes

def chunk_text(text, max_chars=MAX_CHARS):
    """
    Further splits a long text (scene) into smaller chunks if it exceeds limits.
    Splits by paragraphs.
    """
    if len(text) <= max_chars:
        return [text]
        
    chunks = []
    paragraphs = text.split("\n")
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        # +1 for newline
        para_len = len(para) + 1 
        
        if current_length + para_len > max_chars:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_length = 0
                
            # If a single paragraph is massive (unlikely in TWI but possible), force split
            if para_len > max_chars:
                 # Naive character split for now, robust enough for POC
                 chunks.append(para) # Potentially exceeding limit, but rare
            else:
                current_chunk.append(para)
                current_length += para_len
        else:
            current_chunk.append(para)
            current_length += para_len
            
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    return chunks

def process_volume(vol_name):
    vol_path = os.path.join(RAW_DIR, vol_name)
    index_path = os.path.join(vol_path, "index.json")
    
    if not os.path.exists(index_path):
        print(f"No index.json found for {vol_name}. Skipping.")
        return

    print(f"Processing {vol_name}...")
    
    # Load index
    with open(index_path, "r", encoding="utf-8") as f:
        chapter_index = json.load(f)
        
    processed_vol_dir = os.path.join(PROCESSED_DIR, vol_name)
    os.makedirs(processed_vol_dir, exist_ok=True)
    
    all_chunks = []
    
    for chapter_meta in chapter_index:
        filename = chapter_meta.get("filename")
        if not filename: continue
        
        filepath = os.path.join(vol_path, filename)
        if not os.path.exists(filepath):
            print(f"  [WARN] File not found: {filename}")
            continue
            
        raw_text = load_chapter(filepath)
        
        # 1. Split into Scenes
        scenes = split_into_scenes(raw_text)
        
        # 2. Chunk Scenes if too large
        chapter_chunks = []
        for scene_idx, scene_text in enumerate(scenes):
            sub_chunks = chunk_text(scene_text)
            
            for sub_idx, chunk_content in enumerate(sub_chunks):
                chunk_id = f"{chapter_meta['order']}_{scene_idx}_{sub_idx}"
                
                chunk_data = {
                    "chunk_id": chunk_id,
                    "chapter_order": chapter_meta["order"],
                    "chapter_title": chapter_meta["title"],
                    "scene_index": scene_idx,
                    "sub_chunk_index": sub_idx,
                    "text": chunk_content,
                    "token_estimate": len(chunk_content) // CHARS_PER_TOKEN
                }
                chapter_chunks.append(chunk_data)
                all_chunks.append(chunk_data)
        
        print(f"  Processed {chapter_meta['title']}: {len(chapter_chunks)} chunks")

    # Save all chunks for this volume
    output_path = os.path.join(processed_vol_dir, "chunks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(all_chunks)} chunks to {output_path}")

def main():
    # Iterate over all raw volumes
    if not os.path.exists(RAW_DIR):
        print("Raw data directory not found.")
        return
        
    for item in sorted(os.listdir(RAW_DIR)):
        if item.startswith("Vol_") and os.path.isdir(os.path.join(RAW_DIR, item)):
            process_volume(item)

if __name__ == "__main__":
    main()
