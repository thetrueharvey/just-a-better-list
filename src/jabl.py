'''Just a Better List

The primary class for constructing better, more Rust-like lists.

At some point, when I'm better, I may end up porting the backend over to rust for that speed

TODO: Want to make everything fully lazy so that a list-graph can be instantiated, and data pushed through it
'''
# %% Dependencies
# stdlib
from __future__ import annotations
from typing import (
    Any,
    Optional,
    Union,
    TypeVar,
    Generic,
    Type,
    cast,
)
from functools import reduce
from collections.abc import Callable

# external
from beartype import beartype

# internal


# %% types
T = TypeVar('T')
V = TypeVar('V')


# %% Class
class jabl(Generic[T]):
    def __init__(self, *args: T):
        self.data =  args
        self.stack: Any = None

    def into_iter(self):
        self.stack = self.data
        return self

    @beartype
    def filter(
        self,
        predicate: Union[Callable[..., bool], list[bool]]
    ):
        if isinstance(predicate, list):
            def _predicate(_):
                for bool_ in predicate:
                    yield bool_
        else:
            _predicate = predicate

        self.stack = filter(_predicate, self.stack)
        
        return self

    @beartype
    def map(self, func: Callable[[T], V]):
        self.stack = map(func, self.stack)

        return cast(jabl[V], self)

    @beartype
    def chunk(
        self,
        chunk_size: Optional[int] = None,
        n_chunks: Optional[int] = None
    ):
        '''Converts the list into a chunked form, i.e.:
        
        >>> x = jabl(1, 2, 3, 4, 5, 6, 7)
        >>> x.chunk(chunk_size=3)
        >>> [jabl(1,2,3), jabl(4,5,6), jabl(7)]


        Note that the chunks themselves are `jabls`, so you can do some fun an interesting things with nested mapping
        '''
        assert chunk_size is not None or n_chunks is not None, 'Specify `chunk_size` or `chunk_length`'

        assert n_chunks is not None, 'Only `n_chunks` is currently supported'
        # TODO: Support chunk size

        n = n_chunks

        k, m = divmod(len(self.stack), n)
        self.stack = [
            jabl(
                *self.stack[
                    (i * k) + min(i, m) : (i + 1) * k + min(i+1, m)
                ]
            )
            for i in range(n)
        ]

        return self

    @beartype
    def unchunk(self):
        '''Inverse of the `chunk` method

        >>> x = [jabl(1,2,3), jabl(4,5,6), jabl(7)]
        >>> x.unchunk(chunk_size=3)
        >>> jabl(1, 2, 3, 4, 5, 6, 7)
        '''
        new_stack = []
        for chunk in self.stack:
            if isinstance(chunk, jabl):
                new_stack += chunk.collect()
            else:
                new_stack += chunk

        self.stack = new_stack

        return self

    @beartype
    def fold(self, func: Callable[[T], V], accumulator: V) -> V:
        raise NotImplementedError()

    @beartype
    def collect(self):
        # TODO: Actually use the `as_list` arg
        if isinstance(self.stack, list):
            return self.stack

        if self.stack is None:
            return [*self.data]
        return [*self.stack]

    @beartype
    def window(self, n: int):
        '''Yield an iterator as a windows over the input, with each element being a tuple
        '''
        self.stack = iter(_Window(stack=self.stack, n=n))
        return self

    @beartype
    def when(self, predicate: Callable[..., bool]):
        raise NotImplementedError()

        return self

    @beartype
    def then(self, func: Callable[..., Any]):
        raise NotImplementedError()

        return self

    @beartype
    def otherwise(self, func: Callable[..., Any]):
        raise NotImplementedError()

        return self


class _Window(jabl[T]):
    def __init__(self, stack: list[T], n: int):
        self.stack = stack
        self.n = n

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if isinstance(self.stack, (_Window, map, filter)):  # If windows are being chained
            self.stack = tuple(self.stack)

        result = self.stack[self.i: (self.i + self.n)]
        if len(result) < self.n:
            raise StopIteration
        
        self.i += 1
        return result

