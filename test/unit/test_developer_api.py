"""
Do interfaces hidden from the user function as intended?
"""
# %% Dependencies
# std
from typing import Callable

# external

# internal
from jabl import jabl


# %% Test Suite
def test_iter():
    x = jabl(1, 2, 3, 4, 5, 6)

    assert [*x] == [e for e in x] == [1, 2, 3, 4, 5, 6]
