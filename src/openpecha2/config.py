from enum import Enum
from pathlib import Path


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


# Path
BASE_PATH = _mkdir(Path.home() / ".pecha_data")
PECHAS_PATH = _mkdir(BASE_PATH / "pechas")
ROOT_DIR = Path(__file__).parent.parent.parent


class AnnotationEnum(Enum):
    index = "index"

    book_title = "BookTitle"
    sub_title = "SubTitle"
    book_number = "BookNumber"
    poti_title = "PotiTitle"
    author = "Author"
    chapter = "Chapter"
    quotation = "Quotation"

    topic = "Text"
    sub_topic = "SubText"

    pagination = "Pagination"
    language = "Language"
    citation = "Citation"
    correction = "Correction"
    error_candidate = "ErrorCandidate"
    peydurma = "Peydurma"
    pedurma_note = "PedurmaNote"
    sabche = "Sabche"
    tsawa = "Tsawa"
    yigchung = "Yigchung"
    durchen = "Durchen"
    footnote = "Footnote"
    segment = "Segment"
    ocr_confidence = "OCRConfidence"
    transcription_time_span = "TranscriptionTimeSpan"


class AnnotationGroupEnum(Enum):
    structure_type = "Structure Type"
    translation = "Translation"
