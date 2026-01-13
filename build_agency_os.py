import os
import sys
import json
import time
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
        print("🚀 Starting Agency OS creation (Modern UI Version)...")

        # 1. Create Main Page
        self.create_main_page()

        # 2. Create Databases
        # We create them as subpages (is_inline=False) to keep the dashboard clean.
        # We will link to them in the dashboard layout.

        # Order matters for relations, but we handle placeholders.
        # Suggested order: Team -> Clients -> Projects -> Tasks -> Others
        build_order = [
            "Team", "Clients", "Projects", "Tasks", "Finance",
            "Meetings", "SOPs", "Content Calendar", "Resources",
            "Assets", "Services"
        ]

        for db_name in build_order:
            # Check if schema exists for this db (in case schema file is older than list)
            if db_name in self.schema:
                self.create_database(db_name, is_inline=False)
            else:
                print(f"⚠️ Schema for '{db_name}' not found. Skipping.")

        # 3. Populate Sample Data (Team)
        self.populate_team_data()

        # 4. Create Dashboard Layout
        self.create_dashboard_content()

        print("\n🎉 Agency OS creation complete!")
        print(f"🔗 Open your new OS: https://www.notion.so/{self.main_page_id.replace('-', '')}")

    def create_main_page(self):
        print("Creating 'Agency OS' page...")
        try:
            # Modern Cover and Icon
            cover = {"type": "external", "external": {"url": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=80"}}
            icon = {"type": "emoji", "emoji": "⚡"}

            resp = self.api.create_page(self.parent_page_id, "Agency OS", icon=icon)

            self.main_page_id = resp["id"]
            print(f"✅ Created 'Agency OS' page: {self.main_page_id}")
        except Exception as e:
            print(f"❌ Failed to create main page: {e}")
            sys.exit(1)

    def create_database(self, db_name, is_inline=False):
        print(f"Creating '{db_name}' database...")
        config = self.schema[db_name]

        properties = config["properties"]
        # Resolve relations
        for prop_name, prop_config in properties.items():
            if "relation" in prop_config:
                target_placeholder = prop_config["relation"]["database_id"]
                # Extract target name from placeholder (e.g. PLACEHOLDER_CLIENTS_DB -> Clients)
                target_db_name = target_placeholder.replace("PLACEHOLDER_", "").replace("_DB", "").title().replace("_", " ")

                # Special case fixes if naming varies
                if target_db_name == "Team": target_db_name = "Team" # Matches

                if target_db_name in self.db_ids:
                    prop_config["relation"]["database_id"] = self.db_ids[target_db_name]
                else:
                    print(f"   ⚠️ Target '{target_db_name}' for relation in '{db_name}' not ready. Relation skipped.")
                    pass

        # Filter out broken relations
        clean_props = {}
        for k, v in properties.items():
            if "relation" in v and "PLACEHOLDER" in v["relation"]["database_id"]:
                continue
            clean_props[k] = v

        try:
            db = self.api.create_database(
                parent_id=self.main_page_id,
                title=db_name,
                properties=clean_props,
                is_inline=is_inline,
                icon=config.get("icon")
            )
            self.db_ids[db_name] = db["id"]
            self.db_urls[db_name] = db.get("url")
            print(f"   ✅ Created '{db_name}' database.")
        except Exception as e:
            print(f"   ❌ Failed to create '{db_name}': {e}")

    def populate_team_data(self):
        print("Populating Team Members...")
        db_id = self.db_ids.get("Team")
        if not db_id:
            return

        members = [
            {"name": "Sara", "role": "Graphic Designer", "email": "heyelgarouri@gmail.com", "project": "Design a Post for noon"},
            {"name": "Rayan", "role": "Ui Designer", "email": "heyelgarouri@gmail.com", "project": "Design a Post for noon"},
            {"name": "Ismail", "role": "Ux designer", "email": "heyelgarouri@gmail.com", "project": "UX Design for a Mobile Bank"},
            {"name": "Adrain", "role": "Website's Designer", "email": "heyelgarouri@gmail.com", "project": "UX Design for a Mobile Bank"},
            {"name": "Mark", "role": "Ux designer", "email": "heyelgarouri@gmail.com", "project": "Design A e-commerce website Shopify"},
            {"name": "Heyismail", "role": "Ceo", "email": "heyelgarouri@gmail.com", "project": "Design A e-commerce website Shopify"}
        ]

        for m in members:
            props = {
                "Name": {"title": [{"text": {"content": m["name"]}}]},
                "Role": {"select": {"name": m["role"]}},
                "Email": {"email": m["email"]},
                "Current Project": {"rich_text": [{"text": {"content": m["project"]}}]}
            }
            try:
                self.api.create_page(parent_id=None, database_id=db_id, properties=props)
            except Exception:
                pass

    def create_dashboard_content(self):
        print("\nCreating Modern Dashboard Layout...")

        # Structure:
        # 1. Quote / Welcome
        # 2. "Cockpit" (Quick Links to Management, Production, Knowledge)
        # 3. Quick Actions

        # Helper to get URL
        def get_url(name):
            return self.db_urls.get(name, "#")

        # --- Section 1: Hero ---
        hero_block = [
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "👋 Welcome back, Agency Owner"}}],
                    "color": "default"
                }
            },
            {
                "type": "quote",
                "quote": {
                    "rich_text": [{"text": {"content": "Design is not just what it looks like and feels like. Design is how it works."}}],
                    "color": "gray_background"
                }
            },
            {"type": "divider", "divider": {}}
        ]

        # --- Section 2: The Cockpit (3 Columns) ---

        # Col 1: Management
        col1_children = [
            {"type": "heading_3", "heading_3": {"rich_text": [{"text": {"content": "🏢 Management"}}], "color": "blue"}},
            self.create_nav_link("Clients", "👥 Client Base"),
            self.create_nav_link("Finance", "💰 Finance"),
            self.create_nav_link("Services", "🏷️ Services"),
            self.create_nav_link("Team", "👤 Team directory"),
        ]

        # Col 2: Production
        col2_children = [
            {"type": "heading_3", "heading_3": {"rich_text": [{"text": {"content": "🔨 Production"}}], "color": "orange"}},
            self.create_nav_link("Projects", "💼 Active Projects"),
            self.create_nav_link("Tasks", "✅ Task Board"),
            self.create_nav_link("Content Calendar", "🗓️ Content"),
        ]

        # Col 3: Knowledge
        col3_children = [
            {"type": "heading_3", "heading_3": {"rich_text": [{"text": {"content": "🧠 Knowledge"}}], "color": "purple"}},
            self.create_nav_link("SOPs", "📚 SOP Library"),
            self.create_nav_link("Resources", "🛠️ Tools & Resources"),
            self.create_nav_link("Assets", "🎨 Brand Assets"),
            self.create_nav_link("Meetings", "📅 Meeting Notes"),
        ]

        cockpit_block = {
            "type": "column_list",
            "column_list": {
                "children": [
                    {"type": "column", "column": {"children": col1_children}},
                    {"type": "column", "column": {"children": col2_children}},
                    {"type": "column", "column": {"children": col3_children}}
                ]
            }
        }

        # --- Section 3: Quick Actions (Callouts) ---
        actions_header = {
            "type": "heading_3",
            "heading_3": {"rich_text": [{"text": {"content": "⚡ Quick Actions"}}], "color": "yellow"}
        }

        # For quick actions, we usually want to open the database to add a new item.
        # Ideally, we'd have a button, but API cannot create buttons.
        # We'll use callouts that look like buttons.

        action_cols = {
            "type": "column_list",
            "column_list": {
                "children": [
                    {"type": "column", "column": {"children": [
                        self.create_callout("New Project", "💼", get_url("Projects"))
                    ]}},
                    {"type": "column", "column": {"children": [
                        self.create_callout("New Task", "✅", get_url("Tasks"))
                    ]}},
                    {"type": "column", "column": {"children": [
                        self.create_callout("New Client", "👤", get_url("Clients"))
                    ]}},
                    {"type": "column", "column": {"children": [
                        self.create_callout("New Invoice", "📄", get_url("Finance"))
                    ]}},
                ]
            }
        }

        children = hero_block + [cockpit_block, {"type": "divider", "divider": {}}, actions_header, action_cols]

        try:
            self.api.append_children(self.main_page_id, children)
            print("✅ Dashboard layout applied.")
        except Exception as e:
            print(f"❌ Failed to build dashboard: {e}")

    def create_nav_link(self, db_name, label):
        url = self.db_urls.get(db_name, "#")
        return {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"text": {"content": label, "link": {"url": url}}}
                ]
            }
        }

    def create_callout(self, text, emoji, url):
        return {
            "type": "callout",
            "callout": {
                "rich_text": [{"text": {"content": text, "link": {"url": url}}}],
                "icon": {"emoji": emoji},
                "color": "gray_background"
            }
        }

if __name__ == "__main__":
    key = os.environ.get("NOTION_KEY")
    page_id = os.environ.get("NOTION_PAGE_ID")

    if not key or not page_id:
        print("Error: Environment variables NOTION_KEY and NOTION_PAGE_ID must be set.")
        sys.exit(1)

    api = NotionAPI(key)
    builder = AgencyOSBuilder(api, page_id)
    builder.build()
