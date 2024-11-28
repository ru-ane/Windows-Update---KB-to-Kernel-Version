import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from github import Github

# Scraper function
def scrape_kb_updates(url, os_version):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Replace with correct selectors based on the webpage structure
    updates = soup.find_all('update_entry_selector')  # Replace with actual selector
    data = []
    for update in updates:
        date = update.find('date_selector').text  # Replace with actual selector
        kb = update.find('kb_selector').text  # Replace with actual selector
        os_builds = update.find('os_build_selector').text.split(', ')  # Split multiple builds
        notes = update.find('notes_selector').text if update.find('notes_selector') else ''
        for os_build in os_builds:
            data.append((date, kb, os_build, os_version, notes))
    return data

# Update CSV file and push to GitHub
def update_github_file(repo_name, file_path, token, new_data):
    g = Github(token)
    repo = g.get_repo(repo_name)
    file = repo.get_contents(file_path)

    # Read the existing file
    existing_csv = pd.read_csv(file.download_url)
    new_df = pd.DataFrame(new_data, columns=['Date', 'KB Number', 'OS Build', 'OS Version', 'Notes'])
    updated_df = pd.concat([existing_csv, new_df]).drop_duplicates()

    # Commit changes back to GitHub
    repo.update_file(
        path=file_path,
        message="Update KB data",
        content=updated_df.to_csv(index=False),
        sha=file.sha,
    )

# Main function
def main():
    with open('config.json') as f:
        config = json.load(f)

    token = config['wu_token']
    repo_name = config['repo_name']
    
    for os_version, details in config['pages'].items():
        scraped_data = scrape_kb_updates(details['url'], os_version)
        update_github_file(repo_name, details['file_path'], token, scraped_data)

if __name__ == "__main__":
    main()
