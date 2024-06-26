from pathlib import Path

from openpecha2.utils.opa_opf_loader import load_opf_annotations_from_yaml
from openpecha2.utils.opf import OpfAnnotation, create_opf_annotation_instance

data_folder = Path(__file__).parent.absolute() / "data"


def test_create_opf_instance_with_single_annotation():
    yaml_file_path = data_folder / "opf_author.yml"
    opf_annot_yml = load_opf_annotations_from_yaml(yaml_file_path)

    opf_annot = create_opf_annotation_instance(opf_annot_yml)
    assert isinstance(opf_annot, OpfAnnotation)

    assert opf_annot.id == "5a54033501934d03bf5b8543542d9d6d"
    assert opf_annot.annotation_type == "Author"
    assert opf_annot.revision == "00001"
    for uuid, annotation in opf_annot.annotations.items():
        if uuid == "0":
            start, end = annotation.span.start, annotation.span.end
            assert start == 19
            assert end == 83


def test_create_opf_instance_with_annotations():
    yaml_file_path = data_folder / "opf_quotations.yml"
    opf_annot_yml = load_opf_annotations_from_yaml(yaml_file_path)

    opf_annot = create_opf_annotation_instance(opf_annot_yml)

    assert isinstance(opf_annot, OpfAnnotation)
    assert opf_annot.id == "10eb4f16d43f41fe90064829cf241d18"
    assert opf_annot.annotation_type == "Quotation"
    assert opf_annot.revision == "00001"
    for uuid, annotation in opf_annot.annotations.items():
        if uuid == "a1f3e26bdb08449aaece0bba4ac4f5cc":
            start, end = annotation.span.start, annotation.span.end
            assert start == 16302
            assert end == 16330
        if uuid == "670003b927a54a5aad937c6ae0206e61":
            start, end = annotation.span.start, annotation.span.end
            assert start == 16444
            assert end == 16450
