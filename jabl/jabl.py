'''Just a Better List

The primary class for constructing better, more Rust-like lists.

At some point, when I'm better, I may end up porting the backend over to rust for that speed

TODO: Want to make everything fully lazy so that a list-graph can be instantiated, and data pushed through it
'''
# %% Dependencies
# stdlib
from __future__ import annotations
from typing import (
    Protocol,
    runtime_checkable,
    Any,
    Optional,
    Union,
    TypeVar,
    Generic,
    Type,
    cast,
)
from functools import reduce
from collections.abc import Callable, Sequence, Iterable
from copy import copy, deepcopy

# external
from beartype import beartype

# internal


# %% types
T = TypeVar('T')
V = TypeVar('V')
U = TypeVar('U')


@runtime_checkable
class SupportsAdd(Protocol):
    def __add__(self, other: SupportsAdd) -> SupportsAdd:
        ...


ADD = TypeVar('ADD', bound=SupportsAdd)


# %% Class
class jabl(Generic[T]):
    def __init__(self, *args: T):
        self.data: Sequence[T] = args
        self.stack: Iterable[T] = self.data

    def zip(self, other: jabl[V]) -> jabl[tuple[T, V]]:
        '''
        >>> x = jabl(1, 2, 3)
        >>> y = jabl(4, 5, 6)
        >>> x.zip(y)
        >>> jabl((1, 4), (2, 5), (3, 6))
        '''
        # TODO: Handle length differences....
        return jabl(
            *zip(self.stack, other.stack)
        )

    def clone(self) -> jabl[T]:
        new: jabl[T] = jabl()
        new.data = copy(self.data)
        new.stack = copy(self.stack)

        return new

    def filter(
        self,
        predicate: Callable[[T], bool] | jabl[bool]
    ) -> jabl[T]:
        @beartype
        def _validate(predicate: Union[Callable[[T], bool], list[bool]]):
            pass
        _validate(predicate)
        
        if isinstance(predicate, list):
            def _predicate(_):
                for _bool in predicate:
                    yield _bool
        else:
            _predicate = predicate

        new = self.clone()
        new.stack = filter(_predicate, new.stack)
        
        return new

    def map(self, func: Callable[[T], V] | Type[V]) -> jabl[V]:
        def _validate(func: Callable[[T], V] | Type[V]):
            pass
        _validate(func)

        new = self.clone()
        new.stack = map(func, new.stack)

        return cast(jabl[V], new)

    def map_when(
        self,
        func: Callable[[T], V] | Type[V] | jabl[bool],
        predicate: Callable[[T], bool] | jabl[bool]
    ) -> jabl[Union[V, T]]:
        '''
        Applies `func` to elements of this jabl whenever `predicate` is True,
        or evaluates to True for the given element.

        >>> x = jabl(1, 2, 3)
        >>> y = jabl(True, False, True)
        >>> x.map_when(lambda x: x + 1, y)
        >>> jabl(2, 2, 4)
        '''
        def _validate(
            func: Callable[[T], V] | Type[V] | jabl[bool],
            predicate: Callable[[T], bool] | jabl[bool]
        ):
            pass
        _validate(func, predicate)

        _predicate = predicate if isinstance(predicate, jabl) else self.map(predicate)

        new: jabl[Union[V, T]] = self.clone()

        if isinstance(func, jabl):
            stack = map(
                lambda a, b, c: a if b else c,
                func.stack,
                _predicate.stack,
                new.stack
            )
        else:
            stack = map(
                lambda x, p: func(x) if p else x,  # TODO: Check the typing here
                new.stack,
                _predicate.stack
            )
        new.stack = stack

        return new

    def chunk(
        self,
        chunk_size: Optional[int] = None,
        n_chunks: Optional[int] = None
    ) -> jabl[jabl[T]]:
        '''Converts the list into a chunked form, i.e.:
        
        >>> x = jabl(1, 2, 3, 4, 5, 6, 7)
        >>> x.chunk(chunk_size=3)
        >>> [jabl(1,2,3), jabl(4,5,6), jabl(7)]


        Note that the chunks themselves are `jabls`, so you can do some fun an interesting things with nested mapping
        '''
        def _validate(
            chunk_size: Optional[int] = None,
            n_chunks: Optional[int] = None
        ):
            pass
        _validate(chunk_size, n_chunks)

        assert chunk_size is not None or n_chunks is not None, 'Specify `chunk_size` or `chunk_length`'

        assert n_chunks is not None, 'Only `n_chunks` is currently supported'
        # TODO: Support chunk size

        n = n_chunks

        k, m = divmod(len(self.stack), n)

        new: jabl[jabl[T]] = self.clone()
        new.stack = [
            jabl(
                *new.stack[
                    (i * k) + min(i, m) : (i + 1) * k + min(i+1, m)
                ]
            )
            for i in range(n)
        ]

        return new

    def unchunk(self) -> jabl[T]:
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

        new = self.clone()
        new.stack = new_stack

        return new

    @beartype
    def fold(self, func: Callable[[T], ADD], accumulator: ADD) -> ADD:
        def _validate(
            func: Callable[[T], ADD],
            accumulator: ADD,
        ):
            pass
        _validate(func, accumulator)

        try:
            accumulator + accumulator  # type: ignore # we just want to confirm that addition works
        except NotImplementedError:
            raise TypeError('`accumulator` must support addition between instances of itself')

        raise NotImplementedError()

    def collect(self) -> list[T]:
        # TODO: Actually use the `as_list` arg
        return [*deepcopy(self.stack)]

    @beartype
    def window(self, n: int):
        '''Yield an iterator as a windows over the input, with each element being a tuple
        '''
        new = self.clone()
        new.stack = iter(_Window(stack=new.stack, n=n))
        return new

    @beartype
    def when(self, predicate: Callable[..., bool]):
        """
        Begins branching logic, using the format:

        >>> x = jabl(1, 2, 3, 4, 5, 6, 7)
        >>> x.when(lambda x: x % 2 == 0).then("A").otherwise("B")

        Note that the 'when' method begins the branching logic, returning a new object representing
        this intermediate state, and thus must be followed by `.then`, which can be followed by
        either `.when` to create a secondary condition, or `.otherwise` to create a default condition.
        """

        return self


class _Window(jabl[T]):
    def __init__(self, stack: Iterable[T], n: int):
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


# %% When.Then.Otherwise
class When(Generic[T, V]):
    """
    A class that represents the `when` component of the `when` method of a `jabl`.
    """
    predicate: Callable[[T], bool]
    child: Then[T, V]
    
    def __init__(self, predicate: Callable[[T], bool]):
        self.predicate = predicate

    def then(self, func: Callable[[T], V] | Type[V] | jabl[V]) -> Then[T, V]:
        """
        A function or literal that is called when the condition of the `when` method is met.
        """
        then = Then(func)
        self.child = then
        return then

    def eval(
        self,
        data: jabl[T],
        predicate: Optional[jabl[bool]] = None
    ) -> jabl[Union[T, V]]:
        _predicate = data.map(self.predicate)

        # TODO: Check that child exists (although users shouldn't be able to call this method directly)

        if predicate is not None:
            # if the predicate was False, then check if the evaluated condition is True
            _predicate = _predicate.zip(predicate).map(lambda x_y: not x_y[1] and x_y[0])

        _data: jabl[Union[T, V]] = self.child.eval(data, _predicate)

        return _data


class Then(Generic[T, V]):
    """
    A class that represents the `then` branch of the `when` method of a `jabl`.
    """
    func: Callable[[T], V] | Type[V] | jabl[V]
    child: When[T, V] | Otherwise[T, V]

    def __init__(
        self,
        func: Callable[[T], V] | Type[V] | jabl[V],
    ):
        self.func = func

    def when(self, predicate: Callable[[T], bool]) -> When[T, V]:
        """
        A function or literal that is called when the condition of the associated `when` method is met.
        """
        new: When[T, V] = When(predicate)
        self.child = new
        return new

    def otherwise(self, func: Callable[[T], U] | Type[V] | jabl[V]) -> Otherwise[T, U]:
        """
        A function or literal that is called when the condition of the associated `when` method is not met.
        """
        new: Otherwise[T, U] = Otherwise(func)
        self.child = new
        return new

    def eval(self, data: jabl[T], predicate: jabl[bool]) -> jabl[Union[V, T]]:
        _data = data.map_when(self.func, predicate)

        _data = self.child.eval(_data, predicate)
        
        return _data


class Otherwise(Generic[T, V]):
    """
    A class that represents the default condition of a When/Then statement.
    """
    func: Callable[[T], V] | Type[V] | jabl[V]
    
    def __init__(
        self,
        func: Callable[[T], V] | Type[V] | jabl[V],
    ):
        self.func = func

    def eval(self, data: jabl[T], predicate: jabl[bool]) -> jabl[Union[V, T]]:
        _data = data.map_when(self.func, predicate.map(lambda x: not x))
        return _data
        
        

# %%
