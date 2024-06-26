from pathlib import Path

from config import data_folder

from stam_annotator.loaders.utility import load_opf_annotations_from_yaml


def test_load_opf_annotations_from_yaml():
    # opf_author.yml has only one annotation
    yaml_file_path = data_folder / "opf_author.yml"
    yaml_annotations = load_opf_annotations_from_yaml(yaml_file_path)
    assert yaml_annotations["id"] == "5a54033501934d03bf5b8543542d9d6d"
    assert yaml_annotations["annotation_type"] == "Author"
    assert yaml_annotations["revision"] == "00001"
    annotation_id = next(iter(yaml_annotations["annotations"]))
    assert yaml_annotations["annotations"][annotation_id]["span"]["start"] == 19
    assert yaml_annotations["annotations"][annotation_id]["span"]["end"] == 83

    # opf_quotations.yml has more than one annotation
    yaml_file_path = Path(__file__).parent.absolute() / "data" / "opf_quotations.yml"
    yaml_annotations = load_opf_annotations_from_yaml(yaml_file_path)
    assert yaml_annotations["id"] == "10eb4f16d43f41fe90064829cf241d18"
    assert yaml_annotations["annotation_type"] == "Quotation"
    assert yaml_annotations["revision"] == "00001"
    assert yaml_annotations["annotations"]["a1f3e26bdb08449aaece0bba4ac4f5cc"] == {
        "span": {"start": 16302, "end": 16330}
    }
    assert yaml_annotations["annotations"]["670003b927a54a5aad937c6ae0206e61"] == {
        "span": {"start": 16444, "end": 16450}
    }


if __name__ == "__main__":
    test_load_opf_annotations_from_yaml()
