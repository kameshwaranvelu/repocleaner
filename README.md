# repoCleaner

A utility to clean stale GitHub repositories and branches. It helps manage your repositories by identifying and deleting branches that have not had any commits in the past year (customizable time window).

## Features

- Reads a list of GitHub repositories from `masterRepoList.txt`.
- Identifies stale branches based on the latest commit date.
- Asks for user consent before deleting stale branches.
- Generates a summary report of deleted branches and repository recommendations.
- Logs actions and errors for auditing purposes.

## Setup

### Prerequisites

- Python 3.6+ is required.
- A GitHub personal access token (PAT) for authentication. Set it in your environment as `GITHUB_TOKEN`.
- Install requirement text file
- clone repo
- Run repocleaner file


