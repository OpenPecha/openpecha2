import logging
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from stam import AnnotationStore, Offset, Selector

from openpecha2.config import AnnotationGroupEnum
from openpecha2.exceptions import CustomDataValidationError
from openpecha2.utils.opa_opf_loader import load_opf_annotations_from_yaml
from openpecha2.utils.opf import create_opf_annotation_instance
from openpecha2.utils.stam_formatter import (
    Annotation_Store,
    convert_opf_for_pre_stam_format,
)


def get_uuid():
    return uuid4().hex


def create_annotationstore(id: str):
    return AnnotationStore(id=id)


def create_resource(store: AnnotationStore, resource_id: str, resource_file_path: Path):
    return store.add_resource(id=resource_id, filename=str(resource_file_path))


def create_dataset(store: AnnotationStore, id: str, key: AnnotationGroupEnum):
    dataset = store.add_dataset(id=id)
    dataset.add_key(key.value)
    return dataset


def create_annotation(
    store: AnnotationStore, id: str, target: Selector, data: List[Dict]
):
    return store.annotate(id=id, target=target, data=data)


def opf_annotation_store_to_stam(annotation_store: Annotation_Store):
    # Create annotation store
    store = create_annotationstore(id=annotation_store.store_id)
    # Create resource

    for resource in annotation_store.resources:
        create_resource(
            store=store, resource_id=resource.id_, resource_file_path=resource.file_path
        )
    # Create dataset
    data_set = annotation_store.datasets[0]
    dataset = create_dataset(
        store=store, id=data_set.data_set_id, key=data_set.data_set_key
    )
    # Create annotation
    for annotation in annotation_store.annotations:
        annotation_data = annotation.annotation_data
        data = [
            {
                "id": annotation_data.annotation_data_id,
                "key": annotation_data.annotation_data_key.value,
                "value": annotation_data.annotation_data_value.value,
                "set": dataset.id(),
            }
        ]
        if annotation.payloads:
            for key, value in annotation.payloads.items():
                data.append(
                    {"id": get_uuid(), "key": key, "value": value, "set": dataset.id()}
                )

        create_annotation(
            store=store,
            id=annotation.annotation_id,
            target=Selector.textselector(
                store.resource(id=annotation.resource_id),
                Offset.simple(annotation.span.start, annotation.span.end),
            ),
            data=data,
        )

    return store


logging.basicConfig(
    level=logging.ERROR,  # Set the log level to ERROR or the desired level
    filename="validation_errors.log",  # Specify the log file
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def opf_to_stam_pipeline(
    pecha_id: str,
    opf_yml_file_path: Path,
    resource_file_path: Path,
    annotation_type_key: AnnotationGroupEnum,
):
    opf_data_dict = load_opf_annotations_from_yaml(opf_yml_file_path)
    """if there are no annotations in the opf file, return None"""
    if not opf_data_dict["annotations"]:
        return None
    try:
        opf_obj = create_opf_annotation_instance(opf_data_dict)
    except CustomDataValidationError as e:
        logging.error(f"pecha id: {pecha_id}, {e.message}")
        raise CustomDataValidationError(f"pecha id: {pecha_id}, {e.message}")
    opf_annotation_store = convert_opf_for_pre_stam_format(
        opf_obj, annotation_type_key, resource_file_path
    )
    opf_stam = opf_annotation_store_to_stam(annotation_store=opf_annotation_store)
    return opf_stam
