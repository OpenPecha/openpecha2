import yaml

from stam_annotator.config import AnnotationEnum
from stam_annotator.exceptions import CustomDataValidationError
from stam_annotator.utility import get_uuid, replace_key


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


def get_enum_value_if_match_ignore_case(enum_class, string_to_check):
    string_to_check_lower = string_to_check.lower()
    for item in enum_class:
        if string_to_check_lower == item.value.lower():
            return item.value
    return False
