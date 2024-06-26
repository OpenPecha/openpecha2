from pathlib import Path

from openpecha2.utils.opa_opf_loader import load_opa_annotations_from_yaml

data_folder = Path(__file__).parent.absolute() / "opa_data"


def test_load_opa_annotation():
    yaml_file_path = data_folder / "A6E3A916A_36CA.yml"

    opa_annot = load_opa_annotations_from_yaml(yaml_file_path)
    expected_opa_annot = {
        "segment_sources": {
            "I3D3CFB25": {
                "type": "translation",
                "relation": "source",
                "lang": "bo",
                "base": "CD23",
            },
            "IC0947659": {
                "type": "translation",
                "relation": "target",
                "lang": "en",
                "base": "9342",
            },
        },
        "segment_pairs": {
            "b168a8b67c754c328f5000f6fc763c7b": {
                "I3D3CFB25": "c084570928f845fbaa1ba4dbcab66be3",
                "IC0947659": "aca983cf21a0462a99fe6436ef916df3",
            },
            "cd81d0dd191340e89330b331eb3b78a0": {
                "I3D3CFB25": "f75f18477b12493baac716f49beea8c7",
                "IC0947659": "7ad15c145e304e3baab8f6a054cb009e",
            },
            "509a0f44e56e4c1bb499c6a189e83ef8": {
                "I3D3CFB25": "52c193b4d5d5434690fed5215862c20f",
                "IC0947659": "edff04256ebd4f8280cc289f27bb04cd",
            },
        },
    }
    assert opa_annot["segment_sources"] == expected_opa_annot["segment_sources"]
    assert opa_annot["segment_pairs"] == expected_opa_annot["segment_pairs"]
