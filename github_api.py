from os import environ

from dotenv import load_dotenv
from github import Auth, Github # https://github.com/PyGithub/PyGithub

def get_github():
    load_dotenv()
    token = environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is not set")

    auth = Auth.Token(token)
    g = Github(auth=auth)
    return g
