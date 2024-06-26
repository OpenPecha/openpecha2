from pathlib import Path

from openpecha2.utils.opa import OpaAnnotation, create_opa_annotation_instance
from openpecha2.utils.opa_opf_loader import load_opa_annotations_from_yaml

data_folder = Path(__file__).parent.absolute() / "data"


def test_create_opa_instance_with_single_annotation():
    yaml_file_path = data_folder / "A6E3A916A_36CA.yml"
    opa_annot_yml = load_opa_annotations_from_yaml(yaml_file_path)

    opa_annot = create_opa_annotation_instance(opa_annot_yml)
    assert isinstance(opa_annot, OpaAnnotation)
