import json
import csv
import os
import zipfile

SCHEMA_FILE = "agency_os_schema.json"
OUTPUT_DIR = "agency_os_csvs"
ZIP_FILE = "agency_os_import.zip"

def create_csvs():
    with open(SCHEMA_FILE, "r") as f:
        schema = json.load(f)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Prepare Team Data
    team_data = [
        {"Name": "Sara", "Role": "Graphic Designer", "Email": "heyelgarouri@gmail.com", "Current Project": "Design a Post for noon"},
        {"Name": "Rayan", "Role": "Ui Designer", "Email": "heyelgarouri@gmail.com", "Current Project": "Design a Post for noon"},
        {"Name": "Ismail", "Role": "Ux designer", "Email": "heyelgarouri@gmail.com", "Current Project": "UX Design for a Mobile Bank"},
        {"Name": "Adrain", "Role": "Website's Designer", "Email": "heyelgarouri@gmail.com", "Current Project": "UX Design for a Mobile Bank"},
        {"Name": "Mark", "Role": "Ux designer", "Email": "heyelgarouri@gmail.com", "Current Project": "Design A e-commerce website Shopify"},
        {"Name": "Heyismail", "Role": "Ceo", "Email": "heyelgarouri@gmail.com", "Current Project": "Design A e-commerce website Shopify"}
    ]

    files_to_zip = []

    for db_name, config in schema.items():
        properties = config["properties"]
        headers = list(properties.keys())

        # Ensure 'Name' (title) is first if possible
        if "Name" in headers:
            headers.remove("Name")
            headers.insert(0, "Name")

        csv_filename = os.path.join(OUTPUT_DIR, f"{db_name}.csv")

        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            if db_name == "Team":
                for row in team_data:
                    # Filter row to match headers
                    row_to_write = {k: v for k, v in row.items() if k in headers}
                    writer.writerow(row_to_write)

        print(f"Created {csv_filename}")
        files_to_zip.append(csv_filename)

    # Create Zip
    with zipfile.ZipFile(ZIP_FILE, 'w') as zipf:
        for file in files_to_zip:
            zipf.write(file, os.path.basename(file))

    print(f"Successfully created {ZIP_FILE}")

if __name__ == "__main__":
    create_csvs()
