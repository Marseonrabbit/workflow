import json
import urllib.request
import urllib.error
import os

class NotionAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def _request(self, method, endpoint, payload=None):
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode('utf-8') if payload else None

        req = urllib.request.Request(url, data=data, headers=self.headers, method=method)

        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"❌ API Error ({e.code}): {error_body}")
            raise e

    def create_page(self, parent_id, title, icon=None):
        payload = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        }
        if icon:
            payload["icon"] = icon

        return self._request("POST", "/pages", payload)

    def create_database(self, parent_id, title, properties, is_inline=False, icon=None):
        payload = {
            "parent": {"type": "page_id", "page_id": parent_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "properties": properties,
            "is_inline": is_inline
        }
        if icon:
            payload["icon"] = icon

        return self._request("POST", "/databases", payload)

    def append_children(self, block_id, children):
        return self._request("PATCH", f"/blocks/{block_id}/children", {"children": children})

# Test the helper
if __name__ == "__main__":
    key = os.environ.get("NOTION_KEY")
    # Use the child page created earlier for testing
    parent = "2e63373b-e1bf-814b-91a8-e39d8ff15bc0"

    api = NotionAPI(key)
    print("Testing custom NotionAPI class...")
    try:
        db = api.create_database(
            parent,
            "Python Urllib DB",
            {
                "Name": {"title": {}},
                "TestProp": {"select": {"options": [{"name": "It Works!"}]}}
            }
        )
        if "properties" in db and "TestProp" in db["properties"]:
            print("✅ SUCCESS: Database created with properties using urllib.")
        else:
            print("❌ FAILURE: Properties missing.")
    except Exception as e:
        print(f"Test failed: {e}")
