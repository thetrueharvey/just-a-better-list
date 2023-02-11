"""
Tests that type inference resolves correctly
"""
# %% Dependencies
# stdlib
from typing import reveal_type

# external

# internal
from jabl import jabl


# %% Test Suite
def test_type_inference():
    test = jabl(1,2,3)
    assert reveal_type(test) == 'Type of "test" is "jabl[int]"'
    
    test = jabl(1,2,3).into_iter().map(float)
    test = jabl(1,2,3).into_iter().map(float).collect()
    test = jabl(1,2,3).into_iter().chunk(3)
    test = jabl(1,2,3).into_iter().chunk(3).map(lambda chunk: chunk.into_iter().map(float).collect()).unchunk()


def test_custom_types_inference():
    class SomeClass:
        x: list[int]
        
        def __init__(self, x: list[int]) -> None:
            self.x = x

    test = jabl(1,2,3).into_iter().map(SomeClass)

    test = jabl("1", "2", "3").into_iter().map(SomeClass)
    
    test = jabl("1", "2", "3").into_iter().map(lambda x: SomeClass(x))

    test = jabl("1", "2", "3").into_iter().map(lambda x: SomeClass([int(x)]))
# %%
