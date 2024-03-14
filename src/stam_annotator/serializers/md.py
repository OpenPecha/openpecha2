from pathlib import Path
from typing import Dict, List

from antx import transfer

from stam_annotator.config import PECHAS_PATH, AnnotationEnum
from stam_annotator.serializers.config import NEWLINE_NORMALIZATION
from stam_annotator.serializers.utility import add_newlines_around_hashes
from stam_annotator.stam_fetcher.alignment import Alignment
from stam_annotator.stam_fetcher.pecha import Pecha


class Alignment_MD_formatter:
    def __init__(self, alignment: Alignment):
        self.alignment = alignment

    @classmethod
    def from_id(cls, id_: str, github_token: str, out_path: Path = PECHAS_PATH):
        alignment = Alignment.from_id(id_, github_token, out_path)
        return cls(alignment) if alignment else None

    def serialize(self, output_dir: Path):
        pechas = list(self.alignment.segment_source.keys())
        pechas_md_content: Dict[str, str] = {pecha_id: "" for pecha_id in pechas}

        for segment_pair in self.alignment.get_segment_pairs():
            for segment in segment_pair:
                pecha_id, text = segment[1], segment[0]
                if pecha_id not in pechas_md_content:
                    continue
                pechas_md_content[pecha_id] += text + f"{NEWLINE_NORMALIZATION}\n\n"
            """Add empty segment for pechas that don't have the segment."""
            segment_sources = [segment[1] for segment in segment_pair]
            for pecha_id in pechas:
                if pecha_id not in segment_sources:
                    pechas_md_content[pecha_id] += f"{NEWLINE_NORMALIZATION}\n\n"

        for pecha_id, md_content in pechas_md_content.items():
            output_md_file = output_dir / f"{pecha_id}.md"
            output_md_file.write_text(md_content)
        print(f"[SUCCESS]: Alignment {self.alignment.id_} serialized successfully.")


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
        if not annotations:
            return grouped_annotations
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
        base_text_backup = base_text_backup.replace(
            "\n",
            NEWLINE_NORMALIZATION,
        )
        base_text_with_ann = base_text_backup
        volume_annotations = self.grouped_annotations[volume_name]

        for annotation_type, annotations in volume_annotations.items():
            base_text_with_ann = self.apply_annotation(
                base_text_with_ann, base_text_backup, annotation_type, annotations
            )

        output_md_file = output_dir / f"{self.pecha_id}_{volume_name}.md"
        base_text_with_ann = add_newlines_around_hashes(base_text_with_ann)
        output_md_file.write_text(base_text_with_ann)

    @staticmethod
    def apply_annotation(
        base_text_with_ann: str, base_text: str, ann_type: str, annotations: List[Dict]
    ) -> str:
        if ann_type == AnnotationEnum.book_title.value:
            ann_style = [["BookTitle start", "(# )"]]
        if ann_type == AnnotationEnum.sub_title.value:
            ann_style = [["SubTitle start", "(## )"]]
        if ann_type == AnnotationEnum.chapter.value:
            ann_style = [["Chapter start", "(### )"]]
        if ann_type == AnnotationEnum.sabche.value:
            ann_style = [["Sabche start", "(#### )"]]
        if ann_type == AnnotationEnum.pagination.value:
            ann_style = [["Pagination start", "(##### )"]]
        if ann_type == AnnotationEnum.citation.value:
            ann_style = [["Citation start", "(> )"]]
        if ann_type == AnnotationEnum.tsawa.value:
            ann_style = [["Tsawa start", "(>> )"]]

        if ann_type == AnnotationEnum.author.value:
            ann_style = [["Author start", "(===>)"], ["Author end", "(<===)"]]
        if ann_type == AnnotationEnum.yigchung.value:
            ann_style = [["Yigchung start", "(--->)"], ["Yigchung end", "(<---)"]]
        if ann_type == AnnotationEnum.quotation.value:
            ann_style = [
                ["Quotation start", "(<<<)"],
                ["Quotation end", "(>>>)"],
            ]
        for annotation in annotations:
            start, end = annotation["span"]["start"], annotation["span"]["end"]
            if start >= end:
                continue
            curr_base_text_with_ann = (
                base_text[:start]
                + ann_style[0][1]
                + base_text[start : end + 1]  # noqa
                + (
                    ann_style[1][1]
                    if len(ann_style) > 1 and len(ann_style[1]) > 1
                    else ""
                )
                + base_text[end + 1 :]  # noqa
            )

            print(f"Transfering  {ann_style[0][0]} annotation")
            base_text_with_ann = transfer(
                curr_base_text_with_ann, ann_style, base_text_with_ann, output="txt"
            )

        return base_text_with_ann


if __name__ == "__main__":
    from stam_annotator.github_token import GITHUB_TOKEN

    # alignment = Alignment_MD_formatter.from_id("AB3CAED2A", GITHUB_TOKEN)
    # output_dir = Path(".")
    # alignment.serialize(output_dir)

    pecha = Pecha_MD_formatter.from_id("P000216", GITHUB_TOKEN)
    pecha.serialize(Path("."))
