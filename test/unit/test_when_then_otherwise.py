"""
Tests that the underlying When, Then, Otherwise classes function as expected.
"""
# %% Dependencies
# std
from typing import Callable

# external

# internal
from jabl import jabl
from jabl.jabl import (
    When,
    Then,
    Otherwise,
)


# %% Test Suite
def test_single_chain():
    check: Callable[[int], bool] = lambda x: x % 2 == 0
    then = jabl(10, 20, 30, 40, 50, 60)
    otherwise = jabl("A", "B", "C", "D", "E", "F")
    
    expr = When(check)

    (expr
        .then(then)
        .otherwise(otherwise))

    result = expr.eval(jabl(1, 2, 3, 4, 5, 6))

    assert result.collect() == ["A", 10, "C", 20, "E", 30]
    
# %%
