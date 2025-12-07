import requests
from bs4 import BeautifulSoup
import os
import time
import random
import re
import json

BASE_URL = "https://wanderinginn.com/table-of-contents/"
DATA_DIR = "data/raw"

def clean_filename(title):
    # Remove invalid characters and replace spaces with underscores
    clean = re.sub(r'[<>:"/\\|?*]', '', title)
    return clean.replace(" ", "_").strip()

def get_soup(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'TWI-Scraper-Bot/1.0'})
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_chapter(url, volume_dir, chapter_title):
    filename = clean_filename(chapter_title) + ".txt"
    filepath = os.path.join(volume_dir, filename)

    if os.path.exists(filepath):
        print(f"  [SKIP] Exists: {filename}")
        return

    print(f"  [DOWNLOADING] {chapter_title}...")
    soup = get_soup(url)
    if not soup:
        return

    # TWI content is usually in #reader-content or .entry-content
    content_div = soup.find(id="reader-content")
    if not content_div:
        content_div = soup.find("div", class_="entry-content")
        
    if not content_div:
        # Try generic article
        content_div = soup.find("article", class_="twi-article")

    if not content_div:
        print(f"  [ERROR] No content found for {url}. Dumping to debug_chapter.html")
        with open("debug_chapter.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        return

    # Get text
    text = content_div.get_text(separator="\n", strip=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    
    # Be polite
    time.sleep(random.uniform(1.0, 3.0))

def main():
    print("Starting TWI Scraper...")
    soup = get_soup(BASE_URL)
    if not soup:
        return

    # The TOC structure is a bit messy, but generally headings denote volumes
    # This is a naive heuristic: find header, then find next sibling paragraph with links
    
    # Actually, TWI TOC usually has Volume headers and then a list of links.
    # Let's try to iterate through the main content area.
    
    # Directly find book wrappers in the global soup
    book_wrappers = soup.find_all("div", class_="book-wrapper")
    if not book_wrappers:
        print("Could not find any book wrappers. HTML structure might have changed.")
        return

    for book in book_wrappers:
        book_num = book.get("data-book-number", "Unknown")
        
        # User requested extraction of Volume 1 only for now
        if book_num != "1":
            continue

        vol_name = f"Vol_{book_num.zfill(2)}"
        
        print(f"Processing {vol_name}...")
        
        # Create directory
        vol_dir = os.path.join(DATA_DIR, vol_name)
        os.makedirs(vol_dir, exist_ok=True)
        
        # Track chapter metadata for index
        chapter_metadata = []
        
        # Find chapters
        chapters = book.find_all("div", class_="chapter-entry")
        for i, chapter in enumerate(chapters, 1):
            web_cell = chapter.find("div", class_="body-web")
            if not web_cell: 
                continue
                
            link = web_cell.find("a")
            if not link:
                continue
                
            href = link.get('href')
            title = link.get_text().strip()
            filename = clean_filename(title) + ".txt"
            
            # Save metadata
            chapter_info = {
                "order": i,
                "title": title,
                "filename": filename,
                "url": href
            }
            chapter_metadata.append(chapter_info)
            
            scrape_chapter(href, vol_dir, title)
            
            # Optional: Simple restart capability
            # If file exists, scrape_chapter already skips it.

        # Save index.json for this volume
        index_path = os.path.join(vol_dir, "index.json")
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(chapter_metadata, f, indent=2, ensure_ascii=False)
        print(f"Saved volume index to {index_path}")


if __name__ == "__main__":
    main()
