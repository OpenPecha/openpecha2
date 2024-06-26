import json
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Union
from uuid import uuid4

from stam import AnnotationStore


def get_uuid():
    return uuid4().hex


def sort_dict_by_path_strings(input_dict):
    sorted_keys = sorted(input_dict.keys(), key=lambda x: str(x))
    sorted_dict = OrderedDict((key, input_dict[key]) for key in sorted_keys)
    return sorted_dict


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


def add_base_path_to_stam_annotation_files(base_path: Path):
    for file in base_path.rglob("*.opf.json"):
        with file.open() as f:
            json_data = json.load(f)

        include_path = json_data["resources"][0]["@include"]
        json_data["resources"][0]["@include"] = str(base_path / include_path)

        with file.open("w") as f:
            json.dump(json_data, f, indent=2)
