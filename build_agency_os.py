import os
import sys
from notion_client import Client

class AgencyOSBuilder:
    def __init__(self, token, parent_page_id):
        self.client = Client(auth=token)
        self.parent_page_id = parent_page_id
        self.page_id = None
        self.urls = {}

    def build(self):
        print("🚀 Starting Agency OS creation...")
        self.create_main_page()
        self.create_sub_databases()
        self.add_quick_links()
        self.create_and_populate_team_db()
        print("\n🎉 Agency OS creation complete!")
        print(f"Go to: {self.urls.get('Agency OS')}")

    def create_main_page(self):
        print("Creating 'Agency OS' page...")
        try:
            agency_os_page = self.client.pages.create(
                parent={"page_id": self.parent_page_id},
                icon={"type": "emoji", "emoji": "💼"},
                properties={
                    "title": {
                        "title": [{"text": {"content": "Agency OS"}}]
                    }
                }
            )
            self.page_id = agency_os_page["id"]
            self.urls['Agency OS'] = agency_os_page['url']
            print(f"✅ Created 'Agency OS' page: {self.page_id}")
        except Exception as e:
            print(f"❌ Failed to create main page: {e}")
            raise e

    def create_sub_databases(self):
        # Create auxiliary databases as sub-pages
        db_configs = [
            {"name": "Projects", "emoji": "💼"},
            {"name": "Tasks", "emoji": "📋"},
            {"name": "Meetings", "emoji": "👥"},
            {"name": "Finance", "emoji": "💳"}
        ]

        print("\nCreating Sub-Databases...")
        for config in db_configs:
            name = config["name"]
            emoji = config["emoji"]

            try:
                db = self.client.databases.create(
                    parent={"page_id": self.page_id},
                    title=[{"type": "text", "text": {"content": name}}],
                    icon={"type": "emoji", "emoji": emoji},
                    properties={
                        "Name": {"title": {}}
                    },
                    is_inline=False
                )
                self.urls[name] = db["url"]
                print(f"   - Created '{name}' database.")
            except Exception as e:
                print(f"   ! Failed to create '{name}' database: {e}")

    def add_quick_links(self):
        print("\nAdding 'Quick Links' section...")

        # Build paragraph with links
        link_texts = []
        db_names = ["Projects", "Tasks", "Meetings", "Finance"]

        # We need to construct a list of text objects with links, separated by spacers
        rich_text = []
        for i, name in enumerate(db_names):
            if name in self.urls:
                # Add the link
                # Using specific emojis for the link text as well
                emoji_map = {"Projects": "💼", "Tasks": "📋", "Meetings": "👥", "Finance": "💳"}
                label = f"Add {name} {emoji_map.get(name, '')}"

                rich_text.append({
                    "text": {"content": label, "link": {"url": self.urls[name]}}
                })

                # Add spacer if not the last item
                if i < len(db_names) - 1:
                    rich_text.append({"text": {"content": "    "}})

        quick_links_blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Quick Links"}}],
                    "color": "blue"
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": rich_text
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Team Members"}}],
                    "color": "blue"
                }
            }
        ]

        try:
            self.client.blocks.children.append(
                block_id=self.page_id,
                children=quick_links_blocks
            )
            print("✅ Added Quick Links.")
        except Exception as e:
            print(f"❌ Failed to add Quick Links: {e}")

    def create_and_populate_team_db(self):
        print("\nCreating 'Team' database (Inline)...")
        try:
            team_db = self.client.databases.create(
                parent={"page_id": self.page_id},
                title=[{"type": "text", "text": {"content": "Team"}}],
                properties={
                    "Name": {"title": {}},
                    "Email": {"email": {}},
                    "Role": {
                        "select": {
                            "options": [
                                {"name": "Graphic Designer", "color": "purple"},
                                {"name": "UI Designer", "color": "orange"},
                                {"name": "UX Designer", "color": "yellow"},
                                {"name": "Website's Designer", "color": "pink"},
                                {"name": "CEO", "color": "red"}
                            ]
                        }
                    },
                    "Project": {"rich_text": {}},
                },
                is_inline=True
            )
            team_db_id = team_db["id"]
            print(f"✅ Created 'Team' database: {team_db_id}")

            self._populate_team_data(team_db_id)

        except Exception as e:
            print(f"❌ Failed to create/populate Team database: {e}")

    def _populate_team_data(self, db_id):
        team_members = [
            {"name": "Sara", "email": "heyelgarouri@gmail.com", "role": "Graphic Designer", "project": "Design a Post for noon"},
            {"name": "Rayan", "email": "heyelgarouri@gmail.com", "role": "UI Designer", "project": "Design a Post for noon"},
            {"name": "Ismail", "email": "heyelgarouri@gmail.com", "role": "UX Designer", "project": "UX Design for a Mobile Bank"},
            {"name": "Adrain", "email": "heyelgarouri@gmail.com", "role": "Website's Designer", "project": "UX Design for a Mobile Bank"},
            {"name": "Mark", "email": "heyelgarouri@gmail.com", "role": "UX Designer", "project": "Design A e-commerce website Shopify"},
            {"name": "Heyismail", "email": "heyelgarouri@gmail.com", "role": "CEO", "project": "Design A e-commerce website Shopify"},
        ]

        print("Populating 'Team' database...")
        for member in team_members:
            try:
                self.client.pages.create(
                    parent={"database_id": db_id},
                    properties={
                        "Name": {"title": [{"text": {"content": member["name"]}}]},
                        "Email": {"email": member["email"]},
                        "Role": {"select": {"name": member["role"]}},
                        "Project": {"rich_text": [{"text": {"content": member["project"]}}]}
                    }
                )
                print(f"   - Added {member['name']}")
            except Exception as e:
                print(f"   ! Failed to add {member['name']}: {e}")

if __name__ == "__main__":
    print("--- Notion Template Builder: Agency OS ---")
    key = os.environ.get("NOTION_KEY")
    page_id = os.environ.get("NOTION_PAGE_ID")

    if not key or not page_id:
        print("Error: Environment variables NOTION_KEY and NOTION_PAGE_ID must be set.")
        print("Usage:")
        print("  export NOTION_KEY='secret_...'")
        print("  export NOTION_PAGE_ID='...'")
        print("  python build_agency_os.py")
        sys.exit(1)

    builder = AgencyOSBuilder(key, page_id)
    try:
        builder.build()
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
