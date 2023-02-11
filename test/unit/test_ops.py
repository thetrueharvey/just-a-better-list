"""
Tests that individual operations produce the correct result
"""
# %% Dependencies
# std
from typing import Callable
from copy import copy, deepcopy

# external

# internal
from jabl import jabl

# %% Test Suite
def test_map_multiple_collect():
    x = jabl(1, 2, 3, 4, 5, 6)
    check: Callable[[int], bool] = lambda x: x % 2 == 0

    result = x.map(lambda x: x + 1)

    first_collect = result.collect()
    next_collect = result.collect()

    assert first_collect == next_collect
    

def test_map_when_explicit():
    x = jabl(1, 2, 3, 4, 5, 6)
    predicate = jabl(True, False, True, False, True, True)

    result = x.map_when(lambda x: x + 1, predicate)

    assert result.collect() == [2, 2, 4, 4, 6, 7]


def test_map_when_lazy():
    x = jabl(1, 2, 3, 4, 5, 6)
    predicate: Callable[[int], bool] = lambda x: x % 2 == 0

    result = x.map_when(lambda x: x + 1, predicate)

    assert result.collect() == [1, 3, 3, 5, 5, 7]
