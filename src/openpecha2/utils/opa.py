import json
from pathlib import Path
from typing import Dict

from pydantic import BaseModel, field_validator


class SegmentSource(BaseModel):
    type: str
    relation: str
    lang: str
    base: str

    @field_validator("relation")
    @classmethod
    def validate_relation(cls, v):
        if v not in ["source", "target"]:
            raise ValueError("Relation must be either 'source' or 'target'")
        return v

    @field_validator("lang")
    @classmethod
    def validate_lang(cls, v):
        if v not in ["bo", "en"]:
            raise ValueError("Language must be either 'bo' or 'en'")
        return v


class OpaAnnotation(BaseModel):
    segment_sources: Dict[str, SegmentSource]
    segment_pairs: Dict[str, Dict[str, str]]

    def items(self):
        return iter(self.segment_pairs.items())


def create_opa_annotation_instance(data: Dict) -> OpaAnnotation:
    return OpaAnnotation(
        segment_sources=data["segment_sources"], segment_pairs=data["segment_pairs"]
    )


def create_opa_annotation_from_json(json_path: Path) -> OpaAnnotation:
    """
    Reads a JSON file and returns an OpaAnnotation instance.
    """
    with open(json_path, encoding="utf-8") as file:
        data = json.load(file)
        return OpaAnnotation(**data)
