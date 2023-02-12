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
    when: Callable[[int], bool] = lambda x: x % 2 == 0
    then = jabl(10, 20, 30, 40, 50, 60)
    otherwise = jabl("A", "B", "C", "D", "E", "F")
    
    expr = When(when)

    (expr
        .then(then)
        .otherwise(otherwise))

    result = expr.eval(jabl(1, 2, 3, 4, 5, 6))

    assert result.collect() == ["A", 20, "C", 40, "E", 60]


def test_multiple_chain():
    expr = When(lambda x: x == 1)

    sub = jabl(10, 20, 30, 40, 50, 60)

    (expr
        .then("A")
        .when(lambda x: x == 2)
        .then(sub)
        .when(lambda x: x == 3)
        .then(lambda _: "C")
        .when(lambda x: x == 4)
        .then(lambda _: "D")
        .when(lambda x: x == 5)
        .then(sub)
        .otherwise("G"))

    result = expr.eval(jabl(1, 2, 3, 4, 5, 6))

    assert result.collect() == ["A", 20, "C", "D", 50, "G"]


# %%
