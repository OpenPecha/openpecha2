from pathlib import Path

from stam import AnnotationStore, Offset, Selector

from stam_annotator.annotation_store import (
    Annotation_Store,
    convert_opf_for_pre_stam_format,
)
from stam_annotator.config import OPF_DIR
from stam_annotator.enums import KeyEnum
from stam_annotator.load_yaml import load_opf_annotations_from_yaml
from stam_annotator.opf_loader import create_opf_annotation_instance
from stam_annotator.utility import save_annotation_store


def create_annotationstore(id: str):
    return AnnotationStore(id=id)


def create_resource(store: AnnotationStore, resource_id: str, text: str):
    return store.add_resource(id=resource_id, text=text)


def create_dataset(store: AnnotationStore, id: str, key: KeyEnum):
    dataset = store.add_dataset(id=id)
    dataset.add_key(key.value)
    return dataset


def create_annotation(store: AnnotationStore, id: str, target: Selector, data: dict):
    return store.annotate(id=id, target=target, data=data)


def opf_annotation_store_to_stam(annotation_store: Annotation_Store):
    # Create annotation store
    store = create_annotationstore(id=annotation_store.store_id)
    # Create resource

    for resource in annotation_store.resources:
        create_resource(
            store=store, resource_id=resource.resource_id, text=resource.text
        )
    # Create dataset
    data_set = annotation_store.datasets[0]
    dataset = create_dataset(
        store=store, id=data_set.data_set_id, key=data_set.data_set_key
    )
    # Create annotation
    for annotation in annotation_store.annotations:
        annotation_data = annotation.annotation_data
        data = dataset.add_data(
            annotation_data.annotation_data_key.value,
            annotation_data.annotation_data_value.value,
            annotation_data.annotation_data_id,
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


def opf_to_stam_pipeline(
    opf_yml_file_path: Path, resource_file_path: Path, annotation_type_key: KeyEnum
):
    opf_data_dict = load_opf_annotations_from_yaml(opf_yml_file_path)
    opf_obj = create_opf_annotation_instance(opf_data_dict)

    opf_annotation_store = convert_opf_for_pre_stam_format(
        opf_obj, annotation_type_key, resource_file_path
    )
    opf_stam = opf_annotation_store_to_stam(annotation_store=opf_annotation_store)
    return opf_stam


if __name__ == "__main__":
    # Define your file paths and other parameters
    resource_file_path = OPF_DIR / "v001.txt"
    opf_yaml_file_path = OPF_DIR / "Author.yml"

    annotation_type_key = KeyEnum.structure_type
    opf_stam = opf_to_stam_pipeline(
        opf_yaml_file_path, resource_file_path, annotation_type_key
    )

    output_file_path = OPF_DIR / "Author.json"
    save_annotation_store(opf_stam, output_file_path)