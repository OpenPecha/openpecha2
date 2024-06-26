from pathlib import Path

from stam_annotator.serializers.md import Pecha_MD_formatter
from stam_annotator.stam_fetcher.pecha import Pecha


def test_md_serializer():
    data_folder = Path(__file__).parent.absolute() / "data"
    pecha_id = "P000216"
    pecha_path = data_folder / pecha_id
    pecha = Pecha(pecha_id, pecha_path)

    md_formatter = Pecha_MD_formatter(pecha)
    assert md_formatter.pecha.id_ == "P000216"

    annotation_types = md_formatter.grouped_annotations["v001"].keys()
    assert set(annotation_types) == {
        "Author",
        "BookTitle",
    }

    volumes = md_formatter.pecha.get_pecha_volume_names()
    assert volumes == ["v001"]

    md_formatter.serialize(data_folder)

    output_file = data_folder / f"{pecha_id}_v001.md"
    assert output_file.exists()
    expected_output_content = (data_folder / "expected_output.md").read_text()
    assert output_file.read_text() == expected_output_content
    output_file.unlink()


test_md_serializer()
