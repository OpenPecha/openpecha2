from typing import List

from openpecha2.serializers.config import NEWLINE_NORMALIZATION


def add_newlines_around_hashes(input_string):
    lines = input_string.split(NEWLINE_NORMALIZATION)

    processed_lines: List[str] = []

    for i, line in enumerate(lines):
        if i != len(lines) - 1:
            line = line + NEWLINE_NORMALIZATION
        """Add new line if line starts with #"""
        if line.startswith("#"):
            processed_lines.append(line + "\n\n")
            continue
        """Add new line if next line starts with #"""

        if i + 1 < len(lines) and lines[i + 1].startswith("#"):
            processed_lines.append(line + "\n\n")
            continue

        processed_lines.append(line + "\n\n")

    # Join the processed lines back into a single string
    output_string = "".join(processed_lines)

    return output_string
