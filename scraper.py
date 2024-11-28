import os
import csv
import json
from github import Github

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

import requests
from bs4 import BeautifulSoup

def scrape_page(url, os_version):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Adjust this based on the structure of the webpage
    updates_table = soup.find('table')  # Find the first table
    if not updates_table:
        print(f"No table found on {url}")
        return []

    rows = updates_table.find_all('tr')
    data = []

    for row in rows[1:]:  # Skip the header row
        cells = row.find_all('td')
        if len(cells) < 5:  # Adjust based on the number of expected columns
            continue

        data.append({
            "Date": cells[0].text.strip(),
            "KB Number": cells[1].text.strip(),
            "OS Build": cells[2].text.strip(),
            "OS Version": os_version,
            "Notes": cells[3].text.strip() if len(cells) > 3 else ""
        })

    return data


def update_github_file(repo, file_path, new_data):
    try:
        # Try to fetch the file (if it exists)
        file = repo.get_contents(kb_updates.csv)
        existing_content = file.decoded_content.decode("utf-8")
        
        # Append new data to existing content
        existing_data = list(csv.DictReader(existing_content.splitlines()))
        all_data = existing_data + new_data
    except Exception as e:
        # File not found (create a new file)
        all_data = new_data

    # Ensure no duplicate rows
    unique_data = {tuple(item.items()): item for item in all_data}.values()

    # Write CSV content
    csv_output = "Date,KB Number,OS Build,OS Version,Notes\n" + "\n".join(
        [",".join(item.values()) for item in unique_data]
    )

    # Update or create the file on GitHub
    commit_message = "Update Windows updates data"
    if "file" in locals():
        repo.update_file(file_path, commit_message, csv_output, file.sha)
    else:
        repo.create_file(file_path, commit_message, csv_output)

def main():
    config = load_config()

    # Use GITHUB_TOKEN from the environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable not found. Ensure it's set in the workflow.")

    repo_name = config["repo_name"]
    output_file_path = config["output_file_path"]
    pages = config["pages"]

    g = Github(github_token)
    repo = g.get_repo(repo_name)

    all_scraped_data = []
    for page_name, page_info in pages.items():
        url = page_info["url"]
        print(f"Scraping updates from {url} for {page_name}")
        scraped_data = scrape_page(url, page_name)
        all_scraped_data.extend(scraped_data)

    update_github_file(repo, output_file_path, all_scraped_data)

if __name__ == "__main__":
    main()
