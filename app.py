import os
import requests
from openai import OpenAI

# The OpenAI API key is read from an environment variable.
# In Google Colab, set it in the Secrets panel as OPENAI_API_KEY.
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def ask_ai(question: str) -> str:
    """Send a question to the AI API and return its answer."""
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=question
    )
    return response.output_text

def publish_to_github(repo_name: str, description: str, files: dict[str, str]) -> str:
    """
    Create a public GitHub repository and upload files using a GitHub Personal
    Access Token (PAT). `files` maps file paths to their text contents.
    """
    token = os.environ["GITHUB_TOKEN"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Create the repository under the account that owns the token.
    # auto_init is set to False to prevent automatic README.md creation conflicts.
    response = requests.post(
        "https://api.github.com/user/repos",
        headers=headers,
        json={
            "name": repo_name,
            "description": description,
            "private": False,
            "auto_init": False,
        },
        timeout=30,
    )
    if response.status_code == 422:
        raise RuntimeError(
            f"Repository '{repo_name}' may already exist. Choose a new name."
        )
    response.raise_for_status()
    repo = response.json()
    owner = repo["owner"]["login"]
    repo_name = repo["name"]

    # Upload each file through GitHub's Contents API.
    for path, content in files.items():
        upload = requests.put(
            f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}",
            headers=headers,
            json={
                "message": f"Add {path}",
                "content": __import__("base64").b64encode(
                    content.encode("utf-8")
                ).decode("ascii"),
            },
            timeout=30,
        )
        upload.raise_for_status()

    return repo["html_url"]
