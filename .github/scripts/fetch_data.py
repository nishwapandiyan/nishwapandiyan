#!/usr/bin/env python3

"""
Fetch live GitHub repository data and merge with projects.json

User controlled:
- name
- repo
- logo
- description
- tags

Fetched automatically:
- stars
- languages
- last update time
"""

import json
import os
import sys
import urllib.request


USERNAME = "nishwapandiyan"

TOKEN = os.environ.get("GITHUB_TOKEN", "")


def github_api(url):

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USERNAME
    }

    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"


    request = urllib.request.Request(
        url,
        headers=headers
    )


    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)



def clean_repo(repo):

    repo = repo.strip()

    repo = repo.replace(
        "https://github.com/",
        ""
    )

    repo = repo.replace(
        "http://github.com/",
        ""
    )

    return repo.rstrip("/")



def main():

    with open("projects.json") as file:
        projects = json.load(file)


    for project in projects:

        repo = clean_repo(
            project.get("repo", "")
        )


        # If only repository name is given
        if "/" not in repo:
            repo = f"{USERNAME}/{repo}"


        project["repo"] = repo


        try:

            data = github_api(
                f"https://api.github.com/repos/{repo}"
            )


            project["stars"] = data.get(
                "stargazers_count",
                0
            )


            project["pushed_at"] = data.get(
                "pushed_at"
            )


            if not project.get("description"):

                project["description"] = (
                    data.get("description")
                    or ""
                )


            project["languages"] = github_api(
                f"https://api.github.com/repos/{repo}/languages"
            )


        except Exception as error:

            print(
                f"Warning: {repo} failed -> {error}",
                file=sys.stderr
            )


            project.setdefault(
                "stars",
                0
            )

            project.setdefault(
                "languages",
                {}
            )

            project.setdefault(
                "pushed_at",
                None
            )


    with open("merged.json","w") as file:

        json.dump(
            projects,
            file,
            indent=2
        )


    print(
        f"Successfully merged {len(projects)} projects"
    )



if __name__ == "__main__":
    main()
