# Agency OS Builder

This repository contains a Python script to verify access and build the "Agency OS" Notion template.

## Setup

1.  **Dependencies**:
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
1.  Create a main page "Agency OS".
2.  Create sub-databases (Projects, Tasks, Meetings, Finance).
3.  Add a Quick Links section.
4.  Create and populate a "Team" database.

## Finding your Page ID

You can find the Page ID in the URL of the Notion page you want to use as the parent.
Example: `https://www.notion.so/My-Page-1234567890abcdef1234567890abcdef`
The ID is `1234567890abcdef1234567890abcdef`.
