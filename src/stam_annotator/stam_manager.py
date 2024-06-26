import time
from pathlib import Path
from typing import List, Sequence, Union

import stam
from stam import AnnotationDataSet, Annotations, AnnotationStore

from stam_annotator.config import AnnotationEnum, AnnotationGroupEnum
from stam_annotator.loaders.opa_loader import OpaAnnotation
from stam_annotator.to_stam_convertor.utility import (
    convert_opf_stam_annotation_to_dictionary,
)


def load_stam_from_json(file_path: Union[str, Path]) -> AnnotationStore:
    file_path = str(file_path)
    return stam.AnnotationStore(file=file_path)


def load_multiple_stam_from_json(
    file_paths: Sequence[Union[str, Path]]
) -> List[AnnotationStore]:
    return [load_stam_from_json(file_path) for file_path in file_paths]


def get_annotation_data_set(store: AnnotationStore, key: str) -> AnnotationDataSet:
    for data_set in store.datasets():
        for data_set_key in data_set.keys():
            try:
                if data_set_key == data_set.key(key):
                    return data_set
            except:  # noqa
                pass

    return False


def get_annotations(
    store: AnnotationStore,
    key: AnnotationGroupEnum,
    value: AnnotationEnum,
    include_payload: bool = True,
) -> Annotations:
    start_time = time.time()

    data_set = get_annotation_data_set(store, key.value)
    data_key = data_set.key(key.value)
    annotations = data_set.data(filter=data_key, value=value.value).annotations()

    annotations = convert_opf_stam_annotation_to_dictionary(
        annotations, include_payload
    )
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"[INFO]: Time taken: {elapsed_time:.2f} seconds")

    return annotations


def combine_stams(stams: List[AnnotationStore]) -> AnnotationStore:
    """
    This function combines multiple stams into one.
    It requires at least two STAM objects in the list to proceed.
    """
    if len(stams) < 2:
        raise ValueError("At least two STAM objects are required.")

    stam1 = stams[0]
    for stam2 in stams[1:]:
        stam1 = combine_two_stam(stam1, stam2)
    return stam1


def combine_two_stam(stam1: AnnotationStore, stam2: AnnotationStore) -> AnnotationStore:

    """
    In this function, all the resources, data set and annotations are being transfered from
    stam2 to stam1.
    """
    # transfer resources
    for resource in stam2.resources():
        stam1.add_resource(id=resource.id(), text=resource.text())

    # transfer annotations
    for annotation in stam2.annotations():
        annotation_data = next(annotation.__iter__(), None)
        if not annotation_data:
            continue

        """
        if the associated data set already exists, then data_set_id of already existing is used
        with annotation,
        else data set id of new is used.

        """
        annotation_data_key = annotation_data.key().id()

        data_set = get_annotation_data_set(stam1, annotation_data_key)
        """if the key is not present in the data set, then it is added to data set"""
        if not data_set:
            data_set = next(stam1.datasets())
            data_set.add_key(annotation_data_key)

        data_set_id = data_set.id()
        data = {
            "id": annotation_data.id(),
            "key": annotation_data_key,
            "value": annotation_data.value().get(),
            "set": data_set_id,
        }
        stam1.annotate(id=annotation.id(), target=annotation.target(), data=data)
    return stam1


def get_alignment_annotations(
    opa_alignment: OpaAnnotation,
    opf_annotations: List[AnnotationStore],
):
    """
    This function returns the annotations of the given key and value from the alignment
    annotation store.
    """

    start_time = time.time()
    alignment_sources = list(opa_alignment.segment_sources.keys())

    alignment_annotations = {}
    for segment_id, segment in opa_alignment.segment_pairs.items():
        # Get if all the sources are present in the segment
        if not all(source in segment for source in alignment_sources):
            raise ValueError("The alignment is not complete.")

        # get the annotation
        current_annotation = {}
        for source_id, segment_offset in segment.items():
            for opf_annot in opf_annotations:
                try:
                    if opf_annot.annotation(segment_offset):
                        language = opa_alignment.segment_sources[source_id].lang
                        current_annotation[language] = str(
                            opf_annot.annotation(segment_offset)
                        )
                        break
                except:  # noqa
                    pass
        alignment_annotations[segment_id] = current_annotation
    end_time = time.time()  # End timing
    elapsed_time = end_time - start_time
    print(f"[INFO]: Time taken: {elapsed_time:.2f} seconds")

    return alignment_annotations
