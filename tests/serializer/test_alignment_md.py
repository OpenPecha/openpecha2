from pathlib import Path

from stam_annotator.serializers.md import Alignment_MD_formatter
from stam_annotator.stam_fetcher.alignment import Alignment


def test_pecha_md_serializer():
    data_folder = Path(__file__).parent.absolute() / "alignment_data"
    alignment_id = "A2EAB20E4"
    alignment_path = data_folder / alignment_id
    alignment = Alignment(alignment_id, alignment_path)
    alignment.load_alignment()

    md_formatter = Alignment_MD_formatter(alignment)
    md_formatter.serialize(data_folder)
    pechas_id = list(md_formatter.alignment.segment_source.keys())
    for pecha_id in pechas_id:
        assert (data_folder / f"{pecha_id}.md").exists()

    bo_expected_output = (data_folder / "bo_expected_output.md").read_text()
    en_expected_output = (data_folder / "en_expected_output.md").read_text()

    assert (data_folder / "I0604E8AE.md").read_text() == bo_expected_output
    assert (data_folder / "I95FE2C27.md").read_text() == en_expected_output

    (data_folder / "I0604E8AE.md").unlink()
    (data_folder / "I95FE2C27.md").unlink()
