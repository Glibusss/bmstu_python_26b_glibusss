from io import StringIO
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from file_filter import filter_file


@pytest.mark.parametrize(
    ("text", "search_words", "stop_words", "expected"),
    [
        pytest.param(
            "а Роза упала на лапу\n"
            "роз лежит рядом\n"
            "РОЗА снова здесь\n"
            "растёт розарий\n",
            ["роза"],
            [],
            ["а Роза упала на лапу\n", "РОЗА снова здесь\n"],
            id="case-insensitive-full-word",
        ),
        pytest.param(
            "а Роза упала на лапу Азора\n"
            "роза лежит на столе\n"
            "АЗОРА пришёл один\n",
            ["роза"],
            ["азора"],
            ["роза лежит на столе\n"],
            id="stop-word-priority",
        ),
        pytest.param(
            "кот и пёс увидели другого кота\n",
            ["кот", "пёс"],
            [],
            ["кот и пёс увидели другого кота\n"],
            id="multiple-search-words-yield-once",
        ),
        pytest.param(
            "any text\n",
            [],
            [],
            [],
            id="empty-search-list",
        ),
        pytest.param(
            "роза\nдругая строка\n",
            ["роза"],
            [],
            ["роза\n"],
            id="search-word-is-whole-line",
        ),
        pytest.param(
            "стоп\nцель\n",
            ["стоп", "цель"],
            ["стоп"],
            ["цель\n"],
            id="stop-word-is-whole-line",
        ),
        pytest.param(
            "я дома\nяблоко дома\nа я\n",
            ["я"],
            [],
            ["я дома\n", "а я\n"],
            id="single-character-search",
        ),
        pytest.param(
            "я дом\nмы дом\nяма дом\n",
            ["дом"],
            ["я"],
            ["мы дом\n", "яма дом\n"],
            id="single-character-stop",
        ),
        pytest.param(
            "роза азора\nроза азор\n",
            ["роза"],
            ["азор"],
            ["роза азора\n"],
            id="partial-stop-word-does-not-match",
        ),
        pytest.param(
            "роза\nроз\nрозан\n",
            ["роз"],
            [],
            ["роз\n"],
            id="partial-search-word-does-not-match",
        ),
        pytest.param(
            "роза\nдругая строка\n",
            ["роза"],
            ["роза"],
            [],
            id="same-search-and-stop-word",
        ),
        pytest.param(
            "Кот\nпёс\n",
            ["кот", "КОТ"],
            ["волк", "ВОЛК"],
            ["Кот\n"],
            id="duplicate-case-insensitive-filters",
        ),
        pytest.param(
            "\nцель",
            ["цель"],
            [],
            ["цель"],
            id="blank-line-and-no-final-newline",
        ),
    ],
)
def test_filter_file(text, search_words, stop_words, expected):
    source = StringIO(text)

    result = list(filter_file(source, search_words, stop_words))

    assert result == expected
    assert not source.closed


@pytest.mark.parametrize(
    "source_path",
    ["phrases.txt", Path("phrases.txt")],
)
def test_path_input_is_supported(source_path):
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
