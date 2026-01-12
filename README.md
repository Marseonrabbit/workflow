# Agency OS Builder

This repository contains tools to recreate the "Agency OS" Notion template. You can either use the Python script for a complete automated setup or use the CSV file to import the data manually.

## Option 1: Automated Setup (Python Script)

The `build_agency_os.py` script automates the creation of the entire structure (Dashboard, Quick Links, Databases).

### Prerequisites
1.  **Python 3** installed.
2.  Install `notion-client`:
    ```bash
    pip install notion-client
    ```

### Usage
1.  **Get Credentials**:
    *   Create a Notion Integration at [notion.so/my-integrations](https://www.notion.so/my-integrations).
    *   Get the `Internal Integration Secret`.
    *   Create a blank page in Notion and share it with your integration.
    *   Get the Page ID from the URL.

2.  **Run the Script**:
    ```bash
    export NOTION_KEY='your_secret_key'
    export NOTION_PAGE_ID='your_page_id'
    python build_agency_os.py
    ```

    *Windows PowerShell:*
    ```powershell
    $env:NOTION_KEY='your_secret_key'
    $env:NOTION_PAGE_ID='your_page_id'
    python build_agency_os.py
    ```

## Option 2: Manual Import (CSV)

If you prefer not to use the API or just want the data, you can import `team.csv` directly into Notion.

1.  Download `team.csv`.
2.  In Notion, click "Import" in the sidebar.
3.  Select "CSV".
4.  Upload `team.csv`.
5.  This will create a new database with the Team data. Note that you will need to manually set up the "Agency OS" dashboard layout and other pages.
