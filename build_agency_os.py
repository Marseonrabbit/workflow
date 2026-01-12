import os
import sys
import json
from notion_api import NotionAPI

SCHEMA_FILE = "agency_os_schema.json"

class AgencyOSBuilder:
    def __init__(self, api, parent_page_id):
        self.api = api
        self.parent_page_id = parent_page_id
        self.main_page_id = None
        self.db_ids = {}
        self.db_urls = {}

        with open(SCHEMA_FILE, "r") as f:
            self.schema = json.load(f)

    def build(self):
        print("🚀 Starting Agency OS creation...")

        # 1. Create Main Page
        self.create_main_page()

        # 2. Create Databases (Order matters for relations, but we will patch relations later if needed?
        # Actually Notion requires the related DB to exist.
        # Dependency Order: Team -> Clients -> Projects -> Tasks.
        # Finance and SOPs are independent.

        self.create_database("Team")
        self.create_database("Clients")
        self.create_database("Projects")
        self.create_database("Tasks")
        self.create_database("Finance")
        self.create_database("SOPs")

        # 3. Create Dashboard content
        self.create_dashboard()

        print("\n🎉 Agency OS creation complete!")

    def create_main_page(self):
        print("Creating 'Agency OS' page...")
        try:
            resp = self.api.create_page(self.parent_page_id, "Agency OS", icon={"type": "emoji", "emoji": "⚡"})
            self.main_page_id = resp["id"]
            print(f"✅ Created 'Agency OS' page: {self.main_page_id}")
        except Exception as e:
            print(f"❌ Failed to create main page: {e}")
            sys.exit(1)

    def create_database(self, db_name):
        print(f"Creating '{db_name}' database...")
        config = self.schema[db_name]

        # Prepare properties, resolving placeholders
        properties = config["properties"]
        for prop_name, prop_config in properties.items():
            if "relation" in prop_config:
                target_placeholder = prop_config["relation"]["database_id"]
                target_db_name = target_placeholder.replace("PLACEHOLDER_", "").replace("_DB", "").title()

                # Check mapping (Team, Clients, Projects)
                if target_db_name == "Team" and "Team" in self.db_ids:
                    prop_config["relation"]["database_id"] = self.db_ids["Team"]
                elif target_db_name == "Clients" and "Clients" in self.db_ids:
                    prop_config["relation"]["database_id"] = self.db_ids["Clients"]
                elif target_db_name == "Projects" and "Projects" in self.db_ids:
                    prop_config["relation"]["database_id"] = self.db_ids["Projects"]
                else:
                    print(f"   ⚠️ Warning: Relation target '{target_db_name}' not found yet. Skipping relation.")
                    # Fallback to rich_text if relation fails? No, just skip the property or relation logic
                    # Notion API will error if ID is invalid.
                    # We will create without relation first if it's missing, but given the order, it should be fine.
                    # Exception: Tasks -> Assignee (Team) is fine. Tasks -> Project (Projects) is fine.
                    # Projects -> Client (Clients) is fine.
                    # Projects -> Team Lead (Team) is fine.
                    pass

        try:
            db = self.api.create_database(
                parent_id=self.main_page_id,
                title=db_name,
                properties=properties,
                is_inline=True, # Agency OS usually has inline databases on dashboard
                icon=config.get("icon")
            )
            self.db_ids[db_name] = db["id"]
            self.db_urls[db_name] = db.get("url")
            print(f"   ✅ Created '{db_name}' database.")
        except Exception as e:
            print(f"   ❌ Failed to create '{db_name}': {e}")
            # If relation failed, maybe try creating without relation?
            # For simplicity, we assume dependencies are met by order.

    def create_dashboard(self):
        print("\nCreating Dashboard Layout...")

        # Add a welcome header and some callouts
        children = [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"text": {"content": "Welcome to your Agency OS. Manage your projects, clients, and team here."}}],
                    "icon": {"emoji": "👋"},
                    "color": "gray_background"
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Quick Access"}}]
                }
            }
        ]

        # Create links to databases
        for name, url in self.db_urls.items():
            if url:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"text": {"content": f"🔗 Go to {name}", "link": {"url": url}}}
                        ]
                    }
                })

        try:
            self.api.append_children(self.main_page_id, children)
            print("✅ Dashboard elements added.")
        except Exception as e:
            print(f"❌ Failed to add dashboard elements: {e}")

if __name__ == "__main__":
    key = os.environ.get("NOTION_KEY")
    page_id = os.environ.get("NOTION_PAGE_ID")

    if not key or not page_id:
        print("Error: Environment variables NOTION_KEY and NOTION_PAGE_ID must be set.")
        sys.exit(1)

    api = NotionAPI(key)
    builder = AgencyOSBuilder(api, page_id)
    builder.build()
