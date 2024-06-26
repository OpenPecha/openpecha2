from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from stam_annotator.config import AnnotationEnum, AnnotationGroupEnum
from stam_annotator.opf_loader import OpfAnnotation, Span
from stam_annotator.utility import get_uuid


class Annotation_Data(BaseModel):
    annotation_data_id: str
    annotation_data_key: AnnotationGroupEnum
    annotation_data_value: AnnotationEnum

    store_id: str


class Resource(BaseModel):
    id_: str
    file_path: Path


class Annotation(BaseModel):
    annotation_id: str
    span: Span
    annotation_data: Annotation_Data
    resource_id: str
    payloads: Optional[Dict[str, Any]] = None  # field for additional metadata


class Annotation_Data_Set(BaseModel):
    data_set_id: str
    data_set_key: AnnotationGroupEnum
    annotation_datas: List[Annotation_Data] = Field(default_factory=list)

    @field_validator("data_set_id", mode="before")
    @classmethod
    def set_id(cls, v):
        return v or get_uuid()

    @field_validator("annotation_datas")
    @classmethod
    def annotation_data_key_must_equal_to_data_set_key(cls, annotation_data, values):
        if (
            "data_set_key" in values
            and annotation_data.annotation_data_key != values["key"]
        ):
            raise ValueError("annotation_data_key must match data_set_key")
        return annotation_data

    def add_annotation_data(self, annotation_data: Annotation_Data):
        if annotation_data not in self.annotation_datas:
            self.annotation_datas.append(annotation_data)


class Annotation_Store(BaseModel):
    store_id: str
    datasets: List[Annotation_Data_Set] = Field(default_factory=list)
    resources: List[Resource] = Field(default_factory=list)
    annotations: List[Annotation] = Field(default_factory=list)

    @field_validator("store_id", mode="before")
    @classmethod
    def set_id(cls, v):
        return v or get_uuid()

    def add_resource(self, resource: Resource):
        self.resources.append(resource)

    def add_data_set(self, data_set: Annotation_Data_Set):
        self.datasets.append(data_set)

    def add_annotation(self, annotation: Annotation):
        self.annotations.append(annotation)


def create_resource(file_path: Path):
    return Resource(id_=file_path.name, file_path=file_path)


def create_data_set(data_set_id: str, data_set_key: AnnotationGroupEnum):
    return Annotation_Data_Set(data_set_id=data_set_id, data_set_key=data_set_key)


def create_annotation(
    annotation_id: str,
    span: Span,
    annotation_data: Annotation_Data,
    resource_id: str,
    payloads: Optional[Dict[str, Any]],
):
    return Annotation(
        annotation_id=annotation_id,
        span=span,
        annotation_data=annotation_data,
        resource_id=resource_id,
        payloads=payloads,
    )


def add_annotation_data_to_data_set(
    data_set: Annotation_Data_Set, annotation_data: Annotation_Data
):
    if annotation_data not in data_set.annotation_datas:
        data_set.annotation_datas.append(annotation_data)


def convert_opf_for_pre_stam_format(
    opf_annot: OpfAnnotation,
    annotation_type_key: AnnotationGroupEnum,
    resource_file_path: Path,
) -> Annotation_Store:
    """
    Convert opf annotation to annotation store for pre-stam format.
    class Annotation_Store is defined with format that is  compatible with stam.
    """

    store_id = get_uuid()
    annotation_store = Annotation_Store(store_id=store_id)
    resource = create_resource(resource_file_path)
    annotation_store.add_resource(resource)

    data_set = create_data_set(
        data_set_id=opf_annot.id, data_set_key=annotation_type_key
    )
    annotation_store.add_data_set(data_set)

    annotation_data = Annotation_Data(
        annotation_data_id=get_uuid(),
        annotation_data_key=annotation_type_key,
        annotation_data_value=opf_annot.annotation_type,
        store_id=store_id,
    )
    for id, annotation in opf_annot.annotations.items():
        add_annotation_data_to_data_set(data_set, annotation_data)
        annotation = create_annotation(
            annotation_id=id,
            span=annotation.span,
            annotation_data=annotation_data,
            resource_id=resource.id_,
            payloads=annotation.payloads,
        )
        annotation_store.add_annotation(annotation)

    return annotation_store
