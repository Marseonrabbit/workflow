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

    def get_children(self, block_id):
        return self._request("GET", f"/blocks/{block_id}/children")

    def delete_block(self, block_id):
        return self._request("DELETE", f"/blocks/{block_id}")

# Test the helper
if __name__ == "__main__":
    pass
