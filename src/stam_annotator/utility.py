import json
import subprocess
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Union
from uuid import uuid4

from stam import AnnotationStore


def get_filename_without_extension(file_path: Union[str, Path]):
    return Path(str(file_path)).stem


def is_json_file_path(file_path: Path) -> bool:
    return file_path.suffix == ".json"


def get_uuid():
    return uuid4().hex


def sort_dict_by_path_strings(input_dict):
    sorted_keys = sorted(input_dict.keys(), key=lambda x: str(x))
    sorted_dict = OrderedDict((key, input_dict[key]) for key in sorted_keys)
    return sorted_dict


def read_json_to_dict(file_path: Path) -> Dict:
    if not is_json_file_path(file_path):
        raise ValueError(f"The file path must lead to a JSON file. Given: {file_path}")
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


def replace_key(dictionary, old_key, new_key):
    if old_key in dictionary:
        dictionary[new_key] = dictionary.pop(old_key)


def save_annotation_store(
    store: AnnotationStore, output_file_path: Union[str, Path], base_dir: Path
):
    output_file_path = Path(output_file_path)
    json_stam = json.loads(store.to_json_string())
    json_stam = modify_file_path_in_json(json_stam, base_dir)
    with open(output_file_path, "w") as f:
        json.dump(json_stam, f, indent=4)


def modify_file_path_in_json(json_data: Dict, base_directory) -> Dict:
    include_path = json_data["resources"][0]["@include"]

    base_directory = str(base_directory)
    if include_path.startswith(base_directory):
        modified_path = include_path[len(base_directory) :].lstrip("/")  # noqa
    else:
        modified_path = include_path
    json_data["resources"][0]["@include"] = modified_path
    return json_data


def save_json_file(data: Dict, output_file_path: Union[str, Path]):
    output_file_path = Path(output_file_path)
    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=4)


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
