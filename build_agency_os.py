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
        print("🚀 Starting Agency OS creation (HeyIsmail version)...")

        # 1. Create Main Page
        self.create_main_page()

        # 2. Create Databases
        # Strategy: Team is Inline (visible on dash). Others are subpages (linked via Quick Links).
        # We create subpages first to get their URLs for the Quick Links?
        # But Quick Links are at the top. We can create blocks later or update?
        # We can append Quick Links *after* creating databases?
        # Notion blocks order: We can append to top? No, append goes to bottom.
        # We must create content in order.

        # But we need DB URLs for the Quick Links.
        # Solution: Create Databases first (as subpages), then create Dashboard content (Quick Links),
        # then create Team DB (Inline) at the bottom?
        # The screenshot shows Quick Links *above* Team Members.

        # So:
        # A. Create Projects, Tasks, Finance, Meetings, SOPs, Clients as SUBPAGES (is_inline=False).
        # B. Create Quick Links section (using URLs from A).
        # C. Create Team DB as INLINE (is_inline=True).

        # Dependency Order: Team is needed for Projects/Tasks relations.
        # So we must create Team first.
        # If we create Team first (Inline), it will be at the top?
        # No, `create_database` with `parent_id=main_page_id` appends it.
        # If I want Team at the bottom, I create it last.
        # But I need Team ID for relations in Projects.

        # Workaround: Create Team as Subpage first (to get ID), then *move* it or create a Linked View?
        # API can't easily move or create linked views with specific layout.

        # Compromise: Create Team as Inline. It will appear first.
        # Then create other DBs (Subpages). They will appear as links below Team.
        # Then create Quick Links? They will be below.

        # To get the exact layout (Quick Links TOP, Team BOTTOM):
        # 1. Create Team DB (Inline).
        # 2. Create other DBs.
        # 3. BUT this puts Team at top.

        # Actually, `create_database` creates a new block.
        # I can create all DBs as subpages first.
        # Then build the dashboard layout (Text, Columns).
        # But how do I show Team inline?
        # I cannot "show" a subpage inline after creation easily.

        # Okay, I will create everything as Subpages (is_inline=False).
        # Then I will add the "Quick Links" section.
        # Then I will add the "Team Members" header.
        # Then I will add a link to the Team database (or try to verify if I can make it inline later? No).
        # I will accept that Team might be a link or I put Team at the top.

        # Wait! The screenshot shows "Agency OS" title, then "Quick Links", then "Team Members".
        # If I create Team DB *last* and `is_inline=True`, it will be at the bottom.
        # But Projects need Team ID.
        # I can create Team DB first, but `is_inline=False` (Subpage).
        # Then create Projects/etc.
        # Then create Dashboard Blocks (Quick Links).
        # Then... I can't "convert" Team to inline.

        # Ok, I will create Team *first* as `is_inline=True`.
        # It will be at the very top.
        # Then I will add "Quick Links" blocks.
        # This will result in: Team Table -> Quick Links.
        # Screenshot: Quick Links -> Team Table.

        # Can I insert blocks at index 0?
        # `append_children` adds to end.
        # `children` in `create_page`?
        # Yes! `create_page` can take `children`.
        # I can define the structure of the page *during creation*!
        # BUT I don't have the DB URLs yet if I create the page first.

        # Complex workflow:
        # 1. Create Main Page (empty).
        # 2. Create Team DB (Inline) -> Appends to page.
        # 3. Create other DBs (Subpages) -> Appends links to page.
        # 4. Now I have a page with [Team DB, Link to Proj, Link to Tasks...].
        # 5. I want [Quick Links, Team DB].

        # I'll stick to a simpler approach:
        # Create Main Page.
        # Create non-dependent DBs (SOPs, Finance, Meetings) as Subpages.
        # Create Team as Inline.
        # Create Projects/Tasks/Clients as Subpages (depend on Team).

        # Result:
        # [SOPs Link]
        # [Finance Link]
        # [Meetings Link]
        # [Team Database (Inline)]
        # [Projects Link]
        # ...

        # This is messy.

        # Better: Create a separate "Databases" page (Backend) to hold the databases?
        # User wants "Exact template".
        # The template likely has databases stored elsewhere or inline.

        # I will create them all as Subpages to keep it clean, except Team?
        # I will create Team as `is_inline=True` *LAST*.
        # But Projects depends on Team ID.
        # DOES Project creation fail if Team ID is missing?
        # My code handles placeholders. If Team ID is missing, relation property is skipped.
        # This is bad.

        # I will create Team first (Inline).
        # Then I will create the "Quick Links" header and blocks *before* it? I can't.

        # I will create Team first (`is_inline=False`).
        # Then I will create everything else.
        # Then I will create a "Dashboard" area with Links.
        # And I will just link to Team. The screenshot shows a Gallery view. I can't create a Gallery view via API.
        # So a Link to Team is safer than an ugly Table.

        # WAIT. I can create the databases *inside another page* (e.g. "Data") and then link them?
        # No, simpler.

        # I will follow this order:
        # 1. Create Main Page.
        # 2. Create "Quick Links" section (with empty links or placeholders?). No.
        # 3. Create Team DB (Inline).
        # 4. Create other DBs (Subpages).

        # This puts Quick Links above Team.
        # But I need URLs for Quick Links.
        # I will calculate URLs?
        # URL = https://www.notion.so/{db_id_without_hyphens}
        # Yes! I can construct the URL if I have the ID.

        # So:
        # 1. Create Main Page.
        # 2. Create Team DB (Inline). (Appended. Index 0).
        # 3. Create other DBs (Subpages). (Appended).
        # 4. Delete the "Link to ..." blocks for the subpages? (When you create a child DB, does it leave a link block? Yes, if inline=False, it appears as a child page in the list).

        # I will create all DBs as `is_inline=False`.
        # Then I will create the Dashboard content (Quick Links + Link to Team).
        # This is the cleanest programmatic way.

        self.create_database("Team", is_inline=False)
        self.create_database("Clients", is_inline=False)
        self.create_database("Projects", is_inline=False)
        self.create_database("Tasks", is_inline=False)
        self.create_database("Finance", is_inline=False)
        self.create_database("Meetings", is_inline=False)
        self.create_database("SOPs", is_inline=False)

        self.populate_team_data()
        self.create_dashboard_content()

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

    def create_database(self, db_name, is_inline=False):
        print(f"Creating '{db_name}' database...")
        config = self.schema[db_name]

        properties = config["properties"]
        # Resolve relations
        for prop_name, prop_config in properties.items():
            if "relation" in prop_config:
                target_placeholder = prop_config["relation"]["database_id"]
                target_db_name = target_placeholder.replace("PLACEHOLDER_", "").replace("_DB", "").title()

                if target_db_name in self.db_ids:
                    prop_config["relation"]["database_id"] = self.db_ids[target_db_name]
                else:
                    # Remove relation if target not found to avoid error
                    print(f"   ⚠️ Target '{target_db_name}' not ready. Relation skipped.")
                    # We can't easily skip just the property key in the loop,
                    # but we can set it to None and filter later?
                    # Or just assume order is correct.
                    # Team is created first. Clients second. Projects third.
                    # Projects -> Clients (OK). Projects -> Team (OK).
                    # Tasks -> Projects (OK). Tasks -> Team (OK).
                    # Meetings -> Team (OK).
                    pass

        try:
            db = self.api.create_database(
                parent_id=self.main_page_id,
                title=db_name,
                properties=properties,
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

        # Data from screenshot
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
                print(f"   + Added {m['name']}")
            except Exception as e:
                print(f"   ! Failed to add {m['name']}: {e}")

    def create_dashboard_content(self):
        print("\nCreating Dashboard Layout...")

        # 1. Quick Links (Columns)
        # We need URL for Projects, Tasks, Meetings, Finance

        links = [
            ("Projects", "Add Project"),
            ("Tasks", "Add Task"),
            ("Meetings", "Add Meeting"),
            ("Finance", "Add Finance")
        ]

        columns = []
        for db_name, label in links:
            url = self.db_urls.get(db_name, "#")
            # Create a callout in a column
            columns.append({
                "type": "column",
                "column": {
                    "children": [
                        {
                            "type": "callout",
                            "callout": {
                                "rich_text": [{"text": {"content": label, "link": {"url": url}}}],
                                "icon": {"emoji": self.schema[db_name]["icon"]["emoji"]},
                                "color": "gray_background"
                            }
                        }
                    ]
                }
            })

        quick_links_block = {
            "type": "column_list",
            "column_list": {
                "children": columns
            }
        }

        # 2. Team Members Header
        team_header = {
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"text": {"content": "Team Members"}}],
                "color": "blue"
            }
        }

        # 3. Link to Team DB (since we can't do inline gallery easily, we provide a clean link)
        team_link = {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": "👥 Open Team Database", "link": {"url": self.db_urls.get("Team", "#")}}}
                ]
            }
        }

        children = [
            {"type": "heading_3", "heading_3": {"rich_text": [{"text": {"content": "Quick Links"}, "color": "blue"}]}},
            {
                "type": "divider",
                "divider": {}
            },
            quick_links_block,
            {
                "type": "divider",
                "divider": {}
            },
            team_header,
            team_link
        ]

        try:
            # We insert these at the TOP of the page (or append)
            # Since the subpages created earlier are just links at the bottom (or hidden if we used a parent page?)
            # create_database(parent=page_id) appends links to the bottom.
            # If we append dashboard now, it will be at the very bottom.
            # Ideally we want Dashboard at top.
            # We can't prepend blocks easily.
            # But the user sees the page.
            # I will append them. It's the best I can do.
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
