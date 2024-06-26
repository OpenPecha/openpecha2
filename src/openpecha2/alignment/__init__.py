import json
from pathlib import Path
from typing import Dict, List, Tuple

from openpecha2.config import PECHAS_PATH
from openpecha2.core.pecha import Pecha
from openpecha2.github_utils import clone_github_repo

ORGANIZATION = "PechaData"


class Alignment:
    segment_source: Dict[str, Dict[str, str]]
    segment_pairs: Dict[str, Dict[str, str]]

    def __init__(self, id_: str, base_path: Path, github_token: str = ""):
        self.id_ = id_
        self.github_token = github_token
        self.base_path = base_path
        self.pechas: Dict = {}
        self.load_alignment()

    @property
    def alignment_fn(self):
        return str(self.base_path / f"{self.id_}.opa" / "alignment.json")

    def load_alignment(self):
        with open(self.alignment_fn, encoding="utf-8") as file:
            data = json.load(file)
        self.segment_source = data["segment_sources"]
        self.segment_pairs = data["segment_pairs"]

        # load pechas
        for id_ in self.segment_source.keys():
            """if pecha exists in base path, load it"""
            parent_dir = self.base_path.parent
            pecha_path = parent_dir / id_
            if pecha_path.exists():
                self.pechas[id_] = Pecha(id_, pecha_path)
            else:
                self.pechas[id_] = Pecha.from_id(id_, self.github_token)

    @property
    def meta_data(self):
        for file_path in self.base_path.rglob("meta.json"):
            with file_path.open() as file:
                return json.load(file)
        return {}

    def get_segment_pairs(self):
        for id_ in self.segment_pairs:
            yield self.get_segment_pair(id_)

    def get_segment_pair(self, id_) -> List[Tuple[str, str, str, Dict]]:
        segment_pair = []
        for pecha_id, segment_id in self.segment_pairs[id_].items():
            segment_lang = self.segment_source[pecha_id]["lang"]
            pecha_volume_name = self.segment_source[pecha_id]["base"]
            segment_text, segment_span = self.pechas[pecha_id].get_annotation(
                segment_id, pecha_volume_name
            )
            segment_pair.append((segment_text, pecha_id, segment_lang, segment_span))
        return segment_pair

    @classmethod
    def from_id(cls, id_: str, github_token: str, out_path: Path = PECHAS_PATH):
        """load if alignment exits"""
        clone_github_repo(ORGANIZATION, id_, out_path, github_token)

        cls.base_path = out_path / f"{id_}"
        return cls(
            id_,
            cls.base_path,
            github_token,
        )
