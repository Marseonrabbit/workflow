# Agency OS Builder

This repository contains Python scripts to build the "Agency OS" Notion template.

## Files

*   `build_agency_os.py`: The main script that builds the Agency OS structure (Dashboard + Databases).
*   `notion_api.py`: A custom helper class for Notion API interactions (used by the builder).
*   `agency_os_schema.json`: Configuration file defining the database schemas.
*   `find_page.py`: A utility to help find a parent page ID if you don't have one (requires `notion-client`).

## Setup

1.  **Dependencies**:
    *   `build_agency_os.py` uses the standard library (`urllib`) and `notion_api.py`. No install required.
    *   `find_page.py` (optional) requires `notion-client`:
        ```bash
        pip install notion-client
        ```

2.  **Environment Variables**:
    You need your Notion Integration Secret (Key) and the Parent Page ID where you want to build the template.

    **Linux/macOS:**
    ```bash
    export NOTION_KEY='your_secret_key'
    export NOTION_PAGE_ID='your_parent_page_id'
    ```

    **Windows:**
    ```cmd
    set NOTION_KEY=your_secret_key
    set NOTION_PAGE_ID=your_parent_page_id
    ```

## Usage

Run the builder script:
```bash
python build_agency_os.py
```

This will:
1.  Read the schema from `agency_os_schema.json`.
2.  Create a main page "Agency OS".
3.  Create interconnected sub-databases (Team, Clients, Projects, Tasks, Finance, SOPs).
4.  Generate a dashboard with quick access links.

## Schema Configuration

You can modify `agency_os_schema.json` to change properties, options, or icons for the databases before running the build.
