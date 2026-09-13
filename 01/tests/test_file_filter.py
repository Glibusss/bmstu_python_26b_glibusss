from io import StringIO
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from homework import filter_file


@pytest.mark.parametrize(
    ("text", "search_words", "stop_words", "expected"),
    [
        (
            "а Роза упала на лапу\n"
            "роз лежит рядом\n"
            "РОЗА снова здесь\n"
            "растёт розарий\n",
            ["роза"],
            [],
            ["а Роза упала на лапу\n", "РОЗА снова здесь\n"],
        ),
        (
            "а Роза упала на лапу Азора\n"
            "роза лежит на столе\n"
            "АЗОРА пришёл один\n",
            ["роза"],
            ["азора"],
            ["роза лежит на столе\n"],
        ),
        (
            "кот и пёс увидели другого кота\n",
            ["кот", "пёс"],
            [],
            ["кот и пёс увидели другого кота\n"],
        ),
        ("any text\n", [], [], []),
    ],
)
def test_filter_file(text, search_words, stop_words, expected):
    source = StringIO(text)

    result = list(filter_file(source, search_words, stop_words))

    assert result == expected
    assert not source.closed


def test_path_input_is_supported():
    source_path = Path("phrases.txt")
    file_data = "Alpha beta\nGamma DELTA\nBeta forbidden\n"

    with patch("builtins.open", mock_open(read_data=file_data)) as opened_file:
        result = list(
            filter_file(
                source_path,
                ["beta", "delta"],
                ["FORBIDDEN"],
            )
        )

    assert result == ["Alpha beta\n", "Gamma DELTA\n"]
    opened_file.assert_called_once_with(source_path, encoding="utf-8")


class TrackingLines:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.requested_lines = 0

    def __iter__(self):
        for line in ("first target\n", "second target\n"):
            self.requested_lines += 1
            yield line


def test_filter_is_lazy_and_reads_one_line_at_a_time():
    source = TrackingLines()
    result = filter_file(source, ["target"], [])

    assert source.requested_lines == 0
    assert next(result) == "first target\n"
    assert source.requested_lines == 1
