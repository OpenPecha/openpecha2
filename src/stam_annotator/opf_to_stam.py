from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from stam import AnnotationStore, Offset, Selector

from stam_annotator.annotation_store import (
    Annotation_Store,
    convert_opf_for_pre_stam_format,
)
from stam_annotator.definations import CUR_DIR, OPF_EN_DIR, KeyEnum
from stam_annotator.opf_loader import create_opf_annotation_instance
from stam_annotator.utility import (
    get_files_from_opf_repo,
    load_opf_annotations_from_yaml,
    save_annotation_store,
)


def get_uuid():
    return uuid4().hex


def create_annotationstore(id: str):
    return AnnotationStore(id=id)


def create_resource(store: AnnotationStore, resource_id: str, text: str):
    return store.add_resource(id=resource_id, text=text)


def create_dataset(store: AnnotationStore, id: str, key: KeyEnum):
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
        stam_annotation = create_annotation(
            store=store,
            id=annotation.annotation_id,
            target=Selector.textselector(
                store.resource(id=annotation.resource_id),
                Offset.simple(annotation.span.start, annotation.span.end),
            ),
            data=data,
        )

        # Creating annotation for meta data
        if not annotation.payloads:
            continue

        create_annotation(
            store=store,
            target=Selector.annotationselector(stam_annotation),
            data=[
                {"id": get_uuid(), "key": key, "value": value, "set": dataset.id()}
                for key, value in annotation.payloads.items()
            ],
            id=get_uuid(),
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


def make_stam_annotation(organization, repo_name, token):
    """get yml alignment from github repo"""
    base_files, layer_files = get_files_from_opf_repo(organization, repo_name, token)
    opf_yml = next(file for file in layer_files if file.name != "meta.yml")
    base_file = next(file for file in base_files if file.name.endswith(".txt"))
    Path(CUR_DIR / opf_yml.name).write_text(opf_yml.decoded_content.decode())
    Path(CUR_DIR / base_file.name).write_text(base_file.decoded_content.decode())
    """convert it to json"""
    opf_stam = opf_to_stam_pipeline(
        CUR_DIR / opf_yml.name, CUR_DIR / base_file.name, KeyEnum.structure_type
    )
    opf_stam.set_filename(str(CUR_DIR / f"{repo_name}.opf.json"))
    opf_stam.save()
    return CUR_DIR


if __name__ == "__main__":
    # Define your file paths and other parameters

    resource_file_path = OPF_EN_DIR / "9342.txt"
    opf_yaml_file_path = OPF_EN_DIR / "Segment.yml"

    annotation_type_key = KeyEnum.structure_type
    opf_stam = opf_to_stam_pipeline(
        opf_yaml_file_path, resource_file_path, annotation_type_key
    )

    output_file_path = OPF_EN_DIR / "Segment.json"
    save_annotation_store(opf_stam, output_file_path)
