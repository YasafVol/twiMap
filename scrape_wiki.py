import requests
import json
import os
import time

WIKI_API_URL = "https://wiki.wanderinginn.com/api.php"
DATA_DIR = "data/wiki"

def fetch_category_members(category_name):
    """
    Fetches all members of a given category from the MediaWiki API.
    Handles pagination via 'cmcontinue'.
    """
    members = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category_name,
        "cmlimit": "500",  # Max limit for standard users
        "format": "json",
        "cmtype": "page"   # Only fetch pages, not subcategories or files
    }

    print(f"Fetching members for {category_name}...")
    
    while True:
        try:
            response = requests.get(WIKI_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "query" in data and "categorymembers" in data["query"]:
                for member in data["query"]["categorymembers"]:
                    members.append({
                        "pageid": member["pageid"],
                        "title": member["title"],
                        # Construct a full URL for convenience
                        "url": f"https://wiki.wanderinginn.com/{member['title'].replace(' ', '_')}"
                    })
            
            # Check for continuation
            if "continue" in data:
                params["cmcontinue"] = data["continue"]["cmcontinue"]
                print(f"  ...fetched {len(members)} items so far. Continuing...")
                time.sleep(0.5) # Be polite
            else:
                break
                
        except Exception as e:
            print(f"Error fetching data: {e}")
            break
            
    print(f"Total members found for {category_name}: {len(members)}")
    return members

def save_json(data, filename):
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} items to {filepath}")

def main():
    # 1. Characters
    # "Category:Characters" is the main category, but it might contain subcategories.
    # For now, let's grab "Category:Characters" and potentially "Category:Named_Characters" if it exists,
    # or rely on the fact that TWI wiki usually puts chars in the top category or we might need recursion later.
    # Let's start simple with "Category:Characters".
    characters = fetch_category_members("Category:Characters")
    save_json(characters, "characters.json")

    # 2. Locations
    locations = fetch_category_members("Category:Locations")
    save_json(locations, "locations.json")
    
    # 3. Classes (Optional but good for entity extraction context)
    classes = fetch_category_members("Category:Classes")
    save_json(classes, "classes.json")

if __name__ == "__main__":
    main()
