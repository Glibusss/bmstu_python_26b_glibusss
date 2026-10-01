from __future__ import annotations

import os
from collections.abc import Iterable, Iterator
from typing import TextIO


FileSource = str | os.PathLike[str] | TextIO


def _filtered_lines(
    lines: Iterable[str],
    search_words: frozenset[str],
    stop_words: frozenset[str],
) -> Iterator[str]:
    for line in lines:
        words = {word.casefold() for word in line.split()}
        if words.isdisjoint(stop_words) and not words.isdisjoint(search_words):
            yield line


def filter_file(
    file_or_path: FileSource,
    search_words: Iterable[str],
    stop_words: Iterable[str],
) -> Iterator[str]:
    normalized_search = frozenset(word.casefold() for word in search_words)
    normalized_stop = frozenset(word.casefold() for word in stop_words)

    if isinstance(file_or_path, (str, os.PathLike)):
        with open(file_or_path, encoding="utf-8") as source:
            yield from _filtered_lines(
                source,
                normalized_search,
                normalized_stop,
            )
        return

    yield from _filtered_lines(
        file_or_path,
        normalized_search,
        normalized_stop,
    )
