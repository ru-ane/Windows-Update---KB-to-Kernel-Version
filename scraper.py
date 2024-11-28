import os
import csv
import json
from github import Github

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup
import re

def scrape_page(url, os_version):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all anchor tags with the specified class
    links = soup.find_all('a', class_='supLeftNavLink')
    data = []

    # Regular expression to extract the KB number and OS build
    kb_pattern = re.compile(r'KB\d+')  # Matches 'KB' followed by digits
    build_pattern = re.compile(r'OS Build \d+\.\d+')  # Matches 'OS Build' followed by numbers

    for link in links:
        text = link.text.strip()
        href = link.get('href', '')

        # Extract the date, KB number, OS build, and notes from the link text
        date_match = re.match(r'^[A-Za-z]+\s+\d{1,2},\s+\d{4}', text)
        kb_match = kb_pattern.search(text)
        build_match = build_pattern.search(text)

        date = date_match.group(0) if date_match else "Unknown"
        kb_number = kb_match.group(0) if kb_match else "Unknown"
        os_build = build_match.group(0).replace("OS Build ", "") if build_match else "Unknown"
        notes = text.split('—', 1)[-1].strip() if '—' in text else text

        # Append the extracted data as a dictionary
        data.append({
            "Date": date,
            "KB Number": kb_number,
            "OS Build": os_build,
            "OS Version": os_version,
            "Notes": notes
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
