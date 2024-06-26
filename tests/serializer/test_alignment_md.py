from pathlib import Path

from openpecha2.alignment import Alignment
from openpecha2.serializers.md import Alignment_MD_formatter


def test_alignment_md_serializer():
    data_folder = Path(__file__).parent.absolute() / "alignment_data"
    alignment_id = "A2EAB20E4"
    alignment_path = data_folder / alignment_id
    alignment = Alignment(alignment_id, alignment_path)
    alignment.load_alignment()

    md_formatter = Alignment_MD_formatter(alignment)
    md_formatter.serialize(data_folder)

    bo_expected_output = (data_folder / "bo_expected_output.md").read_text()
    en_expected_output = (data_folder / "en_expected_output.md").read_text()

    assert (data_folder / "I0604E8AE_bo.md").read_text() == bo_expected_output
    assert (data_folder / "I95FE2C27_en-us.md").read_text() == en_expected_output

    (data_folder / "I0604E8AE_bo.md").unlink()
    (data_folder / "I95FE2C27_en-us.md").unlink()
