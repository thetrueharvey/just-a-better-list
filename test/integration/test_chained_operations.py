'''Tests that operations are correctly chained as expected
'''
# %% Libraries
# stdlib
from typing import List

# 3rd party

# module
from src.List import jabl


# %%
def test_simple_chain(simple_data: List[int]):
    data = jabl(*simple_data)

    result = (
        data
            .into_iter()
            .map(lambda x: x**2)
            .filter(lambda x: x > 5)
            .map(lambda x: x**0.5)
            .map(round)
            .collect()
    )

    assert result == [3, 4, 5]


def test_window(simple_data: List[int]):
    data = jabl(*simple_data)

    result = (
        data
            .into_iter()
            .window(n=2)
            .map(lambda x: x[1] > x[0])
            .collect()
    )

    assert result == [(1,2), (2,3), (3,4), (4,5)]


def test_nested_window(simple_data: List[int]):
    data = jabl(*simple_data)

    result = (
        data
            .into_iter()
            .window(n=3)
            .map(sum)
            .window(n=2)
            .map(lambda x: x[1] > x[0])
            .collect()
    )

    assert result == [(1,2), (2,3), (3,4), (4,5)]


def test_chunking(simple_data: List[int]):
    data = jabl(*simple_data)

    result = (
        data
            .into_iter()
            .chunk(n_chunks=2)
            .unchunk()
            .collect()
    )

    assert result == [1,2,3,4,5]

    result = (
        data
            .into_iter()
            .chunk(n_chunks=2)
            .paramap(
                lambda x: x.into_iter().map(lambda y: y**2).collect(),
                n_workers=20
            )
            .unchunk()
            .collect()
    )

    assert result == [1, 4, 9, 16, 25]  # Need to implement equality checking

    a=0
