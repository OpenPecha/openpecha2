import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from stam import Annotation, AnnotationStore

from openpecha2.config import PECHAS_PATH, AnnotationEnum, AnnotationGroupEnum
from openpecha2.github_utils import clone_github_repo
from openpecha2.utility import add_base_path_to_stam_annotation_files
from openpecha2.utils.opa_opf_loader import get_enum_value_if_match_ignore_case

ORGANIZATION = "PechaData"


class Pecha:
    def __init__(self, id_: str, base_path: Path):
        self.id_ = id_
        self.base_path = base_path
        self.pecha_volumes: Dict[str, AnnotationStore] = {}
        add_base_path_to_stam_annotation_files(self.base_path)
        self.load_pecha()

    @property
    def pecha_fn(self):
        return self.base_path / f"{self.id_}.opf" / "layers"

    def load_pecha(self):
        json_files = list(self.pecha_fn.glob("**/*.opf.json"))
        for json_file in json_files:
            index = json_file.name.index(".opf.json")
            volumen_name = json_file.name[:index]
            self.pecha_volumes[volumen_name] = AnnotationStore(file=str(json_file))

    @classmethod
    def from_id(cls, id_: str, github_token: str, out_path: Path = PECHAS_PATH):
        """Check if repo exists in github"""
        clone_github_repo(ORGANIZATION, id_, out_path, github_token)

        cls.base_path = out_path / f"{id_}"
        return cls(id_, cls.base_path)

    @property
    def meta_data(self):
        for file_path in self.base_path.rglob("meta.json"):
            with file_path.open() as file:
                return json.load(file)
        return {}

    @property
    def index_data(self):
        for file_path in self.base_path.rglob("index.json"):
            with file_path.open() as file:
                return json.load(file)
        return {}

    def get_base_text(self, volume_name: str) -> str:
        resource = list(self.base_path.rglob(f"{volume_name}.txt"))[0]
        return resource.read_text()

    @staticmethod
    def get_span_from_annotation(annotation: Annotation) -> Dict:
        return {
            "start": annotation.offset().begin().value(),
            "end": annotation.offset().end().value(),
        }

    def get_annotation(self, id_: str, volume_name) -> Tuple[str, Dict]:
        """stam returns annotation texts in a list, so we join them"""
        annotation = self.pecha_volumes[volume_name].annotation(id_)
        annotation_text = " ".join(annotation.text())
        annotation_span = self.get_span_from_annotation(annotation)
        return (annotation_text, annotation_span)

    def get_pecha_volume_names(self) -> List:
        return list(self.pecha_volumes.keys())

    def format_annotations_as_dict(self, annotations) -> Dict:
        annotations_dict = {}
        for annotation in annotations:
            """get annotation text, key and type"""
            annotation_content = {}
            annotation_payloads = {}
            for annotation_data in annotation:
                key, value = annotation_data.key().id(), str(annotation_data.value())
                matched_enum = get_enum_value_if_match_ignore_case(
                    AnnotationGroupEnum, key
                )
                if matched_enum:
                    annotation_content["annotation_group"] = key
                    annotation_content["annotation"] = value
                else:
                    annotation_payloads[key] = value

            """save annotation data in a dict with annotation id """
            annotation_content["text"] = str(annotation)
            annotation_content["span"] = self.get_span_from_annotation(annotation)
            if annotation_payloads:
                annotation_content["payloads"] = annotation_payloads
            annotations_dict[annotation.id()] = annotation_content
        return annotations_dict

    def get_annotations(self) -> Optional[Dict]:
        annotations = {}
        for volume_name in self.get_pecha_volume_names():
            stam_annotations = self.pecha_volumes[volume_name].annotations()
            volume_annotations = self.format_annotations_as_dict(stam_annotations)
            annotations[volume_name] = volume_annotations
        return annotations

    def get_filtered_annotations(
        self,
        annotation_group: Optional[AnnotationGroupEnum] = None,
        annotation_type: Optional[AnnotationEnum] = None,
    ) -> Optional[Dict]:
        if annotation_group is None or annotation_type is None:
            print("[INFO]: Please provide annotation_group and annotation_type")
            return None

        annotations = {}
        for volume_name in self.get_pecha_volume_names():
            stam_volume = self.pecha_volumes[volume_name]
            stam_dataset = next(stam_volume.datasets())
            stam_key = stam_dataset.key(annotation_group.value)
            stam_annotations = stam_volume.annotations(
                filter=stam_key, value=annotation_type.value
            )
            volume_annotations = self.format_annotations_as_dict(stam_annotations)
            annotations[volume_name] = volume_annotations
        return annotations
