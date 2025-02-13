import os
import requests
from datetime import datetime, timedelta
import logging
import json

# Set up logging
logging.basicConfig(filename='repoCleaner.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# GitHub personal access token (use environment variable for security)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise EnvironmentError("GitHub token not set. Please set the GITHUB_TOKEN environment variable.")

# Function to read repositories from the master repo list file
def read_repositories(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except Exception as e:
        logging.error(f"Error reading repo list file {file_path}: {e}")
        raise

# Get branches for a repository
def get_branches(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/branches'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logging.error(f"Error fetching branches for {repo}: {response.json()}")
        return []
    
    return response.json()

# Get latest commit date for a branch
def get_latest_commit(owner, repo, branch):
    url = f'https://api.github.com/repos/{owner}/{repo}/commits/{branch}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logging.error(f"Error fetching commit data for {branch} in {repo}: {response.json()}")
        return None
    
    commit_data = response.json()
    commit_date = commit_data['commit']['committer']['date']
    return datetime.fromisoformat(commit_date[:-1])  # Remove 'Z' from the timestamp

# Identify stale branches (older than 1 year)
def get_stale_branches(owner, repo, tw):
    branches = get_branches(owner, repo)
    stale_branches = []
    
    for branch in branches:
        commit_date = get_latest_commit(owner, repo, branch['name'])
        if commit_date and commit_date < tw:
            stale_branches.append(branch['name'])
    
    return stale_branches

# Delete a branch
def delete_branch(owner, repo, branch):
    url = f'https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        logging.info(f"Successfully deleted branch {branch} in repo {repo}.")
        return True
    else:
        logging.error(f"Failed to delete branch {branch} in repo {repo}: {response.json()}")
        return False

# Main function to run repoCleaner logic
def repo_cleaner(file_path):
    repos = read_repositories(file_path)
    one_year_ago = datetime.now() - timedelta(days=365)  # Time window = 1 year

    for repo_url in repos:
        # Extract the owner and repo name from the URL
        owner, repo = repo_url.split('/')[-2], repo_url.split('/')[-1]
        logging.info(f"Processing repository {repo}...")

        stale_branches = get_stale_branches(owner, repo, one_year_ago)
        
        if stale_branches:
            print(f"Repo: {repo}")
            print("Stale branches:")
            for idx, branch in enumerate(stale_branches, start=1):
                print(f"{idx}. {branch}")

            # Ask user to confirm deletion
            to_delete = []
            for branch in stale_branches:
                consent = input(f"Do you want to delete branch {branch}? (Y/N): ")
                if consent.lower() == 'y':
                    to_delete.append(branch)
            
            if to_delete:
                print(f"Deleting branches: {', '.join(to_delete)}")
                for branch in to_delete:
                    if delete_branch(owner, repo, branch):
                        print(f"Deleted branch: {branch}")
                    else:
                        print(f"Failed to delete branch: {branch}")
            else:
                print("No branches were deleted.")
        else:
            print(f"Repo: {repo} has no stale branches.")
        
        print(f"Finished processing {repo}.")
    
    # Generate summary after the operation
    generate_summary(repos)

# Generate executive summary
def generate_summary(repos):
    summary = {"deleted_branches": [], "recommendations": []}
    for repo_url in repos:
        owner, repo = repo_url.split('/')[-2], repo_url.split('/')[-1]
        with open('repoCleaner_summary.json', 'w') as summary_file:
            json.dump(summary, summary_file, indent=4)
    
    print("Executive Summary has been generated. Check 'repoCleaner_summary.json'.")

if __name__ == "__main__":
    repo_cleaner('masterRepoList.txt')
