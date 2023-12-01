from enum import Enum
from pathlib import Path

CUR_DIR = Path(__file__).parent.absolute()
ROOT_DIR = CUR_DIR.parent.parent.absolute()
DATA_DIR = ROOT_DIR / "data"

OPF_DIR = DATA_DIR / "opf"
OPA_DIR = DATA_DIR / "opa"


class ValueEnum(Enum):
    author = "Author"
    book_title = "BookTitle"
    chapter = "Chapter"
    quotation = "Quotation"
    sabche = "Sabche"
    tsawa = "Tsawa"


class KeyEnum(Enum):
    structure_type = "Structure Type"