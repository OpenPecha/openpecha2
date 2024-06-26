import json
from pathlib import Path

from github import Github, GithubException

from stam_annotator.exceptions import RepoDoesNotExist


def check_repo_exists(token, org_name, repo_name):
    g = Github(token)
    try:
        org = g.get_organization(org_name)
        org.get_repo(repo_name)
    except GithubException:
        raise RepoDoesNotExist(org_name, repo_name)


def add_base_path_to_stam_annotation_files(base_path: Path):
    for file in base_path.rglob("*.opf.json"):
        with file.open() as f:
            json_data = json.load(f)

        include_path = json_data["resources"][0]["@include"]
        json_data["resources"][0]["@include"] = str(base_path / include_path)

        with file.open("w") as f:
            json.dump(json_data, f, indent=2)
