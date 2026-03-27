import json
import csv
import os
import zipfile
import shutil

SCHEMA_FILE = "agency_os_schema.json"
OUTPUT_DIR = "agency_os_csvs"
ZIP_FILENAME = "agency_os_import.zip"

def create_csvs():
    if not os.path.exists(SCHEMA_FILE):
        print(f"Error: Schema file {SCHEMA_FILE} not found.")
        return

    with open(SCHEMA_FILE, "r") as f:
        schema = json.load(f)

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    created_files = []

    for db_name, config in schema.items():
        filename = os.path.join(OUTPUT_DIR, f"{db_name}.csv")
        properties = config.get("properties", {})

        # Extract headers (property names)
        headers = list(properties.keys())

        # Prepare data
        rows = []

        # Helper to map data to row based on headers
        def make_row(data_dict):
            return [data_dict.get(h, "") for h in headers]

        # Special handling for Team data
        if db_name == "Team":
            members = [
                {"Name": "Sara", "Role": "Graphic Designer", "Email": "heyelgarouri@gmail.com", "Current Project": "Design a Post for noon"},
                {"Name": "Rayan", "Role": "Ui Designer", "Email": "heyelgarouri@gmail.com", "Current Project": "Design a Post for noon"},
                {"Name": "Ismail", "Role": "Ux designer", "Email": "heyelgarouri@gmail.com", "Current Project": "UX Design for a Mobile Bank"},
                {"Name": "Adrain", "Role": "Website's Designer", "Email": "heyelgarouri@gmail.com", "Current Project": "UX Design for a Mobile Bank"},
                {"Name": "Mark", "Role": "Ux designer", "Email": "heyelgarouri@gmail.com", "Current Project": "Design A e-commerce website Shopify"},
                {"Name": "Heyismail", "Role": "Ceo", "Email": "heyelgarouri@gmail.com", "Current Project": "Design A e-commerce website Shopify"}
            ]
            for m in members:
                rows.append(make_row(m))

        elif db_name == "Clients":
             # Name, Status, Contact Person, Email, Phone, Industry, Value, Last Contact
             rows.append(make_row({
                 "Name": "Sample Client", "Status": "Active", "Contact Person": "John Doe",
                 "Email": "client@example.com", "Phone": "555-0123", "Industry": "Tech",
                 "Value": "5000", "Last Contact": "2023-10-27"
             }))

        elif db_name == "Projects":
             # Name, Status, Client, Priority, Timeline, Team Lead
             rows.append(make_row({
                 "Name": "Website Redesign", "Status": "In Progress", "Priority": "High",
                 "Timeline": "2023-11-01"
             }))

        elif db_name == "Finance":
             # Name, Type, Amount, Date, Category, Invoice Status
             rows.append(make_row({
                 "Name": "Q3 Retainer", "Type": "Income", "Amount": "1000",
                 "Date": "2023-10-01", "Category": "Retainer", "Invoice Status": "Paid"
             }))

        elif db_name == "Content Calendar":
            # Title, Status, Channel, Publish Date, URL
            rows.append(make_row({
                "Title": "Launch Post", "Status": "Drafting", "Channel": "LinkedIn",
                "Publish Date": "2023-11-15", "URL": "https://linkedin.com"
            }))

        elif db_name == "Resources":
            # Name, Type, Link, Cost
            rows.append(make_row({
                "Name": "Notion", "Type": "Tool", "Link": "https://notion.so", "Cost": "10"
            }))

        elif db_name == "Assets":
            # Name, Type, Link, File Type
            rows.append(make_row({
                "Name": "Company Logo", "Type": "Logo", "Link": "https://drive.google.com/...", "File Type": "SVG"
            }))

        elif db_name == "Services":
            # Name, Price, Description, Type
            rows.append(make_row({
                "Name": "Website Design", "Price": "5000", "Description": "Full website design in Figma", "Type": "One-off"
            }))

        # Write to CSV
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(rows)

        created_files.append(filename)
        print(f"Created {filename}")

    # Create Zip
    with zipfile.ZipFile(ZIP_FILENAME, 'w') as zipf:
        for file in created_files:
            zipf.write(file, os.path.basename(file))

    print(f"\n✅ Successfully created {ZIP_FILENAME} with {len(created_files)} CSV files.")
    print("You can now import these CSV files into Notion to build your Agency OS.")

if __name__ == "__main__":
    create_csvs()
