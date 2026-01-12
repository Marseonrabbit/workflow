import os
from notion_client import Client

def find_target_page():
    key = os.environ.get("NOTION_KEY")
    client = Client(auth=key)

    # Search for a page named "Agency OS" first to update/append
    results = client.search(query="Agency OS", filter={"value": "page", "property": "object"}).get("results")
    if results:
        print(f"Found existing 'Agency OS' page: {results[0]['id']}")
        return results[0]['id']

    # Fallback: Find a suitable root page.
    # We'll look for "Untitled" pages or just the first one.
    results = client.search(filter={"value": "page", "property": "object"}).get("results")
    if results:
        # Prefer "Untitled" to avoid messing up named pages like "Second Brain"
        for page in results:
            title_prop = page.get("properties", {}).get("title", {}).get("title", [])
            title = title_prop[0].get("text", {}).get("content", "Untitled") if title_prop else "Untitled"
            if title == "Untitled":
                 print(f"Found 'Untitled' page to use as parent: {page['id']}")
                 return page['id']

        # If no Untitled, just take the first one
        print(f"Using first accessible page: {results[0]['id']}")
        return results[0]['id']

    return None

if __name__ == "__main__":
    page_id = find_target_page()
    if page_id:
        print(page_id)
