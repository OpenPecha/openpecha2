import json
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Union
from uuid import uuid4

import stam
import yaml
from stam import Annotations, AnnotationStore

from stam_annotator.config import AnnotationEnum
from stam_annotator.exceptions import CustomDataValidationError


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


def convert_none_to_null_in_annotations(data):
    """
    if a value is null in yml file, it will be converted to None in python.
    and None has no value to show in annotation, so this convert None to
    string type 'null'.
    """
    if "annotations" in data and isinstance(data["annotations"], dict):
        for key, value in data["annotations"].items():
            data["annotations"][key] = {
                k: "null" if v in [None, {}] else v for k, v in value.items()
            }
    return data


def replace_key(dictionary, old_key, new_key):
    if old_key in dictionary:
        dictionary[new_key] = dictionary.pop(old_key)


def get_enum_value_if_match_ignore_case(enum_class, string_to_check):
    string_to_check_lower = string_to_check.lower()
    for item in enum_class:
        if string_to_check_lower == item.value.lower():
            return item.value
    return False


def load_opf_annotations_from_yaml(yaml_file):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
        data = convert_none_to_null_in_annotations(data)

    """check if annotation type matches any enum value"""
    enum_matched_value = get_enum_value_if_match_ignore_case(
        AnnotationEnum, data["annotation_type"]
    )
    if enum_matched_value is False:
        raise CustomDataValidationError(
            f"annotation_type: {data['annotation_type']} is not valid. It must be one of {AnnotationEnum}"
        )

    """if annotation type matches with enum value but has different case,
        replace it with the enum value"""
    if enum_matched_value is not data["annotation_type"]:
        data["annotation_type"] = enum_matched_value

    """standardizing the data in yml files"""
    """in some cases, the value is 'revision' and in some cases it is 'rev'"""
    keys_to_replace = [("rev", "revision"), ("content", "annotations")]
    for old_key, new_key in keys_to_replace:
        if new_key not in data and old_key in data:
            replace_key(data, old_key, new_key)

    """annotations key is a list in some cases, convert it to dictionary"""
    if isinstance(data["annotations"], list) and len(data["annotations"]) == 1:
        annotation_id = get_uuid()
        data["annotations"] = {
            f"{annotation_id}": item for index, item in enumerate(data["annotations"])
        }
        return data

    """standardizing the annotation data in span"""
    for annotation in data["annotations"]:
        if "span" in annotation:
            keys_to_replace = [("start_char", "start"), ("end_char", "end")]
            for old_key, new_key in keys_to_replace:
                if new_key not in annotation["span"] and old_key in annotation["span"]:
                    replace_key(annotation["span"], old_key, new_key)

    if isinstance(data["annotations"], list):
        annotations = {}
        for _, annotation_data in enumerate(data["annotations"]):
            annotations[annotation_data["id"]] = annotation_data
            annotations[annotation_data["id"]].pop("id")
        data["annotations"] = annotations
        return data

    """Check if 'annotations' key exists in the data"""
    if "annotations" not in data:
        data["annotations"] = {}

    return data


def load_opa_annotations_from_yaml(yaml_file):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    return data


def save_annotation_store(
    store: AnnotationStore, output_file_path: Union[str, Path], base_dir: Path
):
    output_file_path = Path(output_file_path)

    # Check if the file extension is .json
    if not is_json_file_path(output_file_path):
        raise ValueError(
            f"The file path must lead to a JSON file. Given: {output_file_path}"
        )

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

    # Check if the file extension is .json
    if not is_json_file_path(output_file_path):
        raise ValueError(
            f"The file path must lead to a JSON file. Given: {output_file_path}"
        )

    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=4)


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
