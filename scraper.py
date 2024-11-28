import os
import pandas as pd
from github import Github
import requests
from bs4 import BeautifulSoup

# Function to update or create a file in the GitHub repo
def update_github_file(repo_name, file_path, token, new_data):
    g = Github(token)
    repo = g.get_repo(repo_name)

    try:
        # Attempt to fetch the existing file
        file = repo.get_contents(ru-ane/Windows-Update---KB-to-Kernel-Version)
        print(f"Found file at {ru-ane/Windows-Update---KB-to-Kernel-Version}. Updating...")
        
        # Read existing data
        existing_csv = pd.read_csv(file.download_url)
        
        # Prepare new data
        new_df = pd.DataFrame(new_data, columns=['Date', 'KB Number', 'OS Build', 'OS Version', 'Notes'])
        updated_df = pd.concat([existing_csv, new_df]).drop_duplicates()
        
        # Commit updated file
        repo.update_file(
            path=file_path,
            message="Update KB data",
            content=updated_df.to_csv(index=False),
            sha=file.sha,
        )
    except Exception as e:
        # Handle the case where the file does not exist
        if "404" in str(e):  # File not found
            print(f"File not found at {file_path}. Creating new file...")
            
            # Prepare new data
            new_df = pd.DataFrame(new_data, columns=['Date', 'KB Number', 'OS Build', 'OS Version', 'Notes'])
            
            # Commit new file
            repo.create_file(
                path=file_path,
                message="Create KB data file",
                content=new_df.to_csv(index=False),
            )
        else:
            # Raise unexpected errors
            raise e

# Function to scrape the webpage for data
def scrape_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Example: Replace with actual scraping logic
    # Assume we extract the following data
    scraped_data = [
        ["2024-11-21", "KB5046714", "19045.5198", "Windows 10", "Preview"],
        ["2024-11-12", "KB5046613", "19044.5131", "Windows 10", ""],
    ]
    return scraped_data

# Main logic
if __name__ == "__main__":
    # Replace with actual variables
    repo_name = "ru-ane/Windows-Update---KB-to-Kernel-Version"  # Example: "octocat/Hello-World"
    file_path = "data/kb_updates.csv"
    token = os.getenv("GITHUB_TOKEN")  # Ensure this is set in your environment
    url = "https://example.com/windows-updates"  # Replace with the real URL
    
    # Step 1: Scrape data
    scraped_data = scrape_webpage(url)
    
    # Step 2: Update the GitHub file
    update_github_file(repo_name, file_path, token, scraped_data)
