"""
Tests that individual operations produce the correct result
"""
# %% Dependencies
# std
from typing import Callable

# external

# internal
from jabl import jabl

# %% Test Suite
def test_map():
    x = jabl(1, 2, 3, 4, 5, 6)

    result = x.map(lambda x: x + 1)

    assert result.collect() == [2, 3, 4, 5, 6, 7]


def test_filter():
    x = jabl(1, 2, 3, 4, 5, 6)

    result = x.filter(lambda x: x % 2 == 0)

    assert result.collect() == [2, 4, 6]


def test_map_when():
    x = jabl(1, 2, 3, 4, 5, 6)
    y = jabl("A", "B", "C", "D", "E", "F")

    result = x.map_when(y, lambda x: x % 2 == 0)

    assert result.collect() == [1, "B", 3, "D", 5, "F"]


def test_chunk():
    x = jabl(1, 2, 3, 4, 5, 6)

    result = x.chunk(n_chunks=3)

    assert result.collect() == [(1, 2), (3, 4), (5, 6)]


def test_unchunk():
    x = jabl(1, 2, 3, 4, 5, 6)

    result = x.chunk(n_chunks=3).unchunk()

    assert result.collect() == [1, 2, 3, 4, 5, 6]
