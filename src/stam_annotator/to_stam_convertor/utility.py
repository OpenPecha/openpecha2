import json
from datetime import datetime
from json import JSONEncoder
from pathlib import Path
from typing import Dict, List, Union

import stam
import yaml
from github import Github, GithubException
from stam import Annotations


def make_local_folder(destination_folder: Path) -> Path:
    destination_folder.mkdir(parents=True, exist_ok=True)
    return destination_folder


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


def get_folder_structure(path: Path):
    base_path = Path(path)
    grouped_files: Dict[Path, List] = {}

    for file in base_path.rglob("*"):
        if ".git" not in file.parts:
            # Group files and folders by their parent directory
            file_tag_pair = (file.name, "file" if file.is_file() else "folder")
            if file.parent not in grouped_files:
                grouped_files[file.parent] = [file_tag_pair]
            else:
                grouped_files[file.parent].append(file_tag_pair)

    return grouped_files


def replace_parent_folder_name(path: Path, old_name: str, new_name: str) -> Path:
    """Replace the parent folder name of the path with the new name"""

    parts = path.parts
    layers_dir = "layers"
    """if there are folders(volume name) presented in layers dir, then the path is trimmed"""
    if layers_dir in parts:
        index = parts.index(layers_dir)
        trimmed_path = Path(*parts[: index + 1])
    else:
        trimmed_path = path

    return Path(str(trimmed_path).replace(old_name, new_name))


def convert_yml_file_to_json(yml_file_path: Path, json_output_path: Path):
    yml_content = yml_file_path.read_text(encoding="utf-8")
    converted_json = json.dumps(
        yaml.safe_load(yml_content), indent=4, cls=CustomEncoder
    )
    json_output_path.write_text(converted_json)


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # Format the date however you like
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)


def convert_opf_stam_annotation_to_dictionary(
    annotations: Annotations, include_payload: bool = True
) -> Dict:
    """
    This function converts the annotation object to a dictionary.
    """
    annotation_dict = {}
    for annotation in annotations:
        # get the text to which this annotation refers (if any)
        text = str(annotation) if not isinstance(annotation, stam.StamError) else "n/a"
        for data in annotation:
            annotation_dict[annotation.id()] = {
                "id": annotation.id(),
                "key": data.key().id(),
                "value": str(data.value()),
                "text": text,
            }
            if include_payload:
                payload_dictionary = {}
                for annot in annotation.annotations():
                    for data in annot:
                        payload_dictionary[data.key().id()] = {
                            "id": annot.id(),
                            "value": str(data.value()),
                        }
                annotation_dict[annotation.id()]["payload"] = payload_dictionary
    return annotation_dict
