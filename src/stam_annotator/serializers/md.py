from pathlib import Path
from typing import Dict, List

from antx import transfer

from stam_annotator.config import PECHAS_PATH, AnnotationEnum
from stam_annotator.stam_fetcher.pecha import Pecha


class Pecha_MD_formatter:
    def __init__(self, pecha: Pecha):
        self.pecha = pecha
        self.pecha_id = pecha.id_
        self.base_texts = self.load_base_texts()
        self.grouped_annotations = self.group_annotations_by_type()

    @classmethod
    def from_id(cls, pecha_id: str, github_token: str, out_path: Path = PECHAS_PATH):
        pecha = Pecha.from_id(pecha_id, github_token, out_path)
        return cls(pecha) if pecha else None

    def load_base_texts(self):
        base_texts = {}
        for volume_name in self.pecha.get_pecha_volume_names():
            base_texts[volume_name] = self.pecha.get_base_text(volume_name)
        return base_texts

    def group_annotations_by_type(self):
        grouped_annotations: Dict[str, Dict[str, List]] = {}
        annotations = self.pecha.get_annotations()
        for volume_id, volume_annotations in annotations.items():
            grouped_annotations[volume_id] = {}
            for annotation_id, annotation_details in volume_annotations.items():
                annotation_type = annotation_details["annotation"]
                annotation_entry = {
                    "text": annotation_details["text"],
                    "span": annotation_details["span"],
                }
                if annotation_type not in grouped_annotations[volume_id]:
                    grouped_annotations[volume_id][annotation_type] = [annotation_entry]
                else:
                    grouped_annotations[volume_id][annotation_type].append(
                        annotation_entry
                    )
        return grouped_annotations

    def serialize(self, output_dir: Path):
        for volume_name in self.pecha.get_pecha_volume_names():
            self.serialize_volume(volume_name, output_dir)

    def serialize_volume(self, volume_name: str, output_dir: Path):
        base_text_backup = self.base_texts[volume_name]
        base_text_with_ann = base_text_backup
        volume_annotations = self.grouped_annotations[volume_name]

        for annotation_type, annotations in volume_annotations.items():
            base_text_with_ann = self.apply_annotation(
                base_text_with_ann, base_text_backup, annotation_type, annotations
            )

        output_md_file = output_dir / f"{self.pecha_id}_{volume_name}.md"
        output_md_file.write_text(base_text_with_ann)

    @staticmethod
    def apply_annotation(
        base_text_with_ann: str, base_text: str, ann_type: str, annotations: List[Dict]
    ) -> str:
        if ann_type == AnnotationEnum.book_title.value:
            ann_style = [["BookTitle start", "(<h1>)"], ["BookTitle end", "(</h1>)"]]
        if ann_type == AnnotationEnum.chapter.value:
            ann_style = [["Chapter start", "(<h2>)"], ["Chapter end", "(</h2>)"]]
        if ann_type == AnnotationEnum.sabche.value:
            ann_style = [["Sabche start", "(<h3>)"], ["Sabche end", "(</h3>)"]]
        if ann_type == AnnotationEnum.author.value:
            ann_style = [["Author start", "(<i>—)"], ["Author end", "(—</i>)"]]
        if ann_type == AnnotationEnum.yigchung.value:
            ann_style = [["Yigchung start", "(<i>)"], ["Yigchung end", "(</i>)"]]
        if ann_type == AnnotationEnum.quotation.value:
            ann_style = [
                ["Quotation start", "(<blockquote>)"],
                ["Quotation end", "(</blockquote>)"],
            ]

        for annotation in annotations:
            start, end = annotation["span"]["start"], annotation["span"]["end"]
            if start >= end:
                continue
            curr_base_text_with_ann = (
                base_text[:start]
                + ann_style[0][1]
                + base_text[start : end + 1]  # noqa
                + ann_style[1][1]
                + base_text[end + 1 :]  # noqa
            )
            base_text_with_ann = transfer(
                curr_base_text_with_ann, ann_style, base_text_with_ann, output="txt"
            )

        return base_text_with_ann


if __name__ == "__main__":

    pecha_id = "P000216"
    pecha = Pecha(pecha_id, Path("/home/tenzin3/stam_annotator/P000216"))
    formatter = Pecha_MD_formatter(pecha)

    output_dir = Path(".")
    formatter.serialize(output_dir)
