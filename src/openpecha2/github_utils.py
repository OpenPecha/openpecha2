import subprocess
from pathlib import Path
from typing import Union

from github import Github, GithubException


def clone_github_repo(
    org_name: str, repo_name: str, destination_folder: Path, token: str
):
    repo_path = destination_folder / repo_name
    if repo_path.exists() and list(repo_path.rglob("*")):
        pass  # Do nothing
    else:
        try:
            repo_url = f"https://github.com/{org_name}/{repo_name}.git"
            env = {"GIT_ASKPASS": "echo", "GIT_PASSWORD": token}
            subprocess.run(
                ["git", "clone", repo_url, str(repo_path)],
                check=True,
                capture_output=True,
                env=env,
            )
            print(f"[SUCCESS]: Repository {repo_name} cloned successfully.")

        except subprocess.CalledProcessError as e:
            print(f"[ERROR]: Error cloning {repo_name} repository: {e}")


def create_github_repo(org_name: str, repo_name: str, token: str) -> bool:
    try:
        g = Github(token)
        org = g.get_organization(org_name)
        org.create_repo(repo_name)
        print(f"[SUCCESS]: Repository {repo_name} created successfully")
        return True
    except:  # noqa
        print(f"[INFO]: Repo {repo_name} already exists")
        return False


def upload_files_to_github_repo(
    org_name: str,
    repo_name: str,
    project_path: Path,
    token: str,
    commit_message: Union[str, None] = None,
):
    g = Github(token)
    repo = g.get_organization(org_name).get_repo(repo_name)
    for file in project_path.rglob("*"):
        if file.is_dir():
            continue
        with open(file, encoding="utf-8") as f:
            data = f.read()
        """upload file to github repo """
        relative_file_path = file.relative_to(project_path)

        try:
            contents = repo.get_contents(str(relative_file_path), ref="main")
            # If file exists, update it
            file_commit_message = (
                commit_message if commit_message else f"Update {file.name}"
            )
            repo.update_file(
                contents.path, file_commit_message, data, contents.sha, branch="main"
            )
        except GithubException as e:
            if e.status == 404:
                # If file does not exist, create it
                file_commit_message = (
                    commit_message if commit_message else f"Create {file.name}"
                )
                repo.create_file(
                    str(relative_file_path), file_commit_message, data, branch="main"
                )
            else:
                # Handle other exceptions
                print(f"[ERROR]: Uploading file to github {relative_file_path}: {e}")
