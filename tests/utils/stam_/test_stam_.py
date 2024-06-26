from pathlib import Path

from stam import AnnotationDataSet, AnnotationStore, DataKey, TextResource

from openpecha2.config import AnnotationGroupEnum
from openpecha2.utils.stam_ import opf_to_stam_pipeline

data_folder = Path(__file__).parent.absolute() / "data"


def test_opf_to_stam():
    pecha_id = "P000216"
    pecha_path = data_folder / pecha_id
    base_file_path = pecha_path / f"{pecha_id}.opf/base" / "v001.txt"
    author_yml_path = pecha_path / f"{pecha_id}.opf/layers/" / "v001/Author.yml"
    annotation_group = AnnotationGroupEnum.structure_type

    opf_stam = opf_to_stam_pipeline(
        pecha_id, author_yml_path, base_file_path, annotation_group
    )
    """ check if return type is AnnotationStore(stam format) """
    assert isinstance(opf_stam, AnnotationStore)
    """ check if resource v001.txt(volume 1) is in the stam """
    assert isinstance(opf_stam.resource("v001.txt"), TextResource)
    """ check if only dataset made and key Structure Type is made"""
    assert opf_stam.datasets_len() == 1
    dataset = next(opf_stam.datasets())
    assert isinstance(dataset, AnnotationDataSet)
    assert dataset.keys_len() == 1

    datakey = dataset.key("Structure Type")
    assert isinstance(datakey, DataKey)

    """ check if the annotation has the annotation value Author """
    assert opf_stam.annotations_len() == 1
    annotation = next(opf_stam.annotations())
    for data in annotation:
        assert str(data.value()) == "Author"
