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
    Optional,
    Union,
    TypeVar,
    Generic,
    Type,
    cast,
)
from collections.abc import Callable, Sequence, Iterable, Iterator

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

    def zip(self, other: jabl[V]) -> jabl[tuple[T, V]]:
        '''
        >>> x = jabl(1, 2, 3)
        >>> y = jabl(4, 5, 6)
        >>> x.zip(y)
        >>> jabl((1, 4), (2, 5), (3, 6))
        '''
        # TODO: Handle length differences....
        return jabl(*zip(self, other))

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    def filter(
        self,
        predicate: Callable[[T], bool] | jabl[bool]
    ) -> jabl[T]:
        @beartype
        def _validate(predicate: Union[Callable[[T], bool], jabl[bool]]):
            pass
        _validate(predicate)
        
        new: jabl[T] = jabl(*filter(predicate, self.data))
        
        return new

    def map(self, func: Callable[[T], V]) -> jabl[V]:
        def _validate(func: Callable[[T], V]):
            pass
        _validate(func)

        new = jabl(*map(func, self.data))

        return new

    def map_when(
        self,
        value: Callable[[T], V] | jabl[V] | V,
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
            value: Callable[[T], V] | jabl[V] | V,
            predicate: Callable[[T], bool] | jabl[bool]
        ):
            pass
        _validate(value, predicate)

        _predicate = predicate if isinstance(predicate, jabl) else self.map(predicate)

        if isinstance(value, jabl):
            value = cast(jabl[V], value)
            
            data = when_a_then_b_else_c(
                a=_predicate.data,
                b=value.data,
                c=self.data
            )        
        elif callable(value):
            value = cast(Callable[[T], V], value)
            
            data = map(
                lambda x, p: value(x) if p else x,  # TODO: Check the typing here? I just toldyou it's callable above
                self.data,
                _predicate.data
            )
        else:
            value = cast(V, value)

            data = map(
                lambda p, x: value if p else x,  # TODO: Check the typing here
                _predicate.data,
                self.data,
            )
        new = jabl(*data)

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

        k, m = divmod(len(self.data), n)

        new: jabl[jabl[T]] = jabl(
            *[self.data[(i * k) + min(i, m) : (i + 1) * k + min(i+1, m)] for i in range(n)]
        )

        return new

    def unchunk(self) -> jabl[T]:
        '''Inverse of the `chunk` method

        >>> x = [jabl(1,2,3), jabl(4,5,6), jabl(7)]
        >>> x.unchunk(chunk_size=3)
        >>> jabl(1, 2, 3, 4, 5, 6, 7)
        '''
        data = []
        for chunk in self.data:
            if isinstance(chunk, jabl):
                data += chunk.data
            else:
                data += chunk

        new = jabl(*data)

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
        # More as a placeholder to eventually allow lazy evaluation
        return list(self.data)

    def peek(self, n: int = -1) -> list[T]:
        return self.data[:n]

    @beartype
    def window(self, n: int):
        '''Yield an iterator as a windows over the input, with each element being a tuple
        '''
        new = jabl(*iter(_Window(stack=self.data, n=n)))
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
    def __init__(self, data: Sequence[T], n: int):
        self.data = data
        self.n = n

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if isinstance(self.data, (_Window, map, filter)):  # If windows are being chained
            self.data = tuple(self.data)

        result = self.data[self.i: (self.i + self.n)]
        if len(result) < self.n:
            raise StopIteration
        
        self.i += 1
        return result


# %% When.Then.Otherwise
class When(Generic[T, V, U]):
    """
    A class that represents the `when` component of the `when` method of a `jabl`.
    """
    predicate: Callable[[T], bool]
    child: Then[T, V, U]
    
    def __init__(self, predicate: Callable[[T], bool]):
        self.predicate = predicate

    def then(
        self,
        value: Callable[[T], V] | Type[V] | jabl[V] | V
    ) -> Then[T, V, U]:
        """
        A function or literal that is called when the condition of the `when` method is met.

        TODO: Validation of the length of the value if it's a jabl
        """
        then: Then[T, V, U] = Then(value)
        self.child = then
        return then

    def eval(
        self,
        data: jabl[T],
        ignore_indices: Optional[jabl[bool]] = None
    ) -> jabl[Union[T, V]]:
        _predicate = data.map(self.predicate)

        # TODO: Check that child exists (although users shouldn't be able to call this method directly)

        if ignore_indices is None:
            ignore_indices = data.map(lambda _: False)
            
        # if the predicate was False, then check if the evaluated condition is True
        _predicate = _predicate.zip(ignore_indices).map(lambda x_y: not x_y[1] and x_y[0])

        ignore_indices = ignore_indices.zip(_predicate).map(lambda x_y: x_y[0] or x_y[1])

        _data: jabl[Union[T, V]] = self.child.eval(data, _predicate, ignore_indices)

        return _data


class Then(Generic[T, V, U]):
    """
    A class that represents the `then` branch of the `when` method of a `jabl`.
    """
    value: Callable[[T], V] | Type[V] | jabl[V] | V
    child: When[T, U, V] | Otherwise[T, U]

    def __init__(
        self,
        value: Callable[[T], V] | Type[V] | jabl[V] | V,
    ):
        self.value = value

    def when(self, predicate: Callable[[T], bool]) -> When[T, U, V]:
        """
        A function or literal that is called when the condition of the associated `when` method is met.
        """
        new: When[T, U, V] = When(predicate)
        self.child = new
        return new

    def otherwise(self, value: Callable[[T], U] | Type[U] | jabl[U] | U) -> Otherwise[T, U]:
        """
        A function or literal that is called when the condition of the associated `when` method is not met.
        """
        new: Otherwise[T, U] = Otherwise(value)
        self.child = new
        return new

    def eval(
        self,
        data: jabl[T],
        predicate: jabl[bool],
        ignore_indices: jabl[bool]
    ) -> jabl[Union[V, T]]:
        _data = data.map_when(self.value, predicate)

        _data = self.child.eval(_data, ignore_indices)
        
        return _data


class Otherwise(Generic[T, V]):
    """
    A class that represents the default condition of a When/Then statement.
    """
    func: Callable[[T], V] | Type[V] | jabl[V] | V
    
    def __init__(
        self,
        value: Callable[[T], V] | Type[V] | jabl[V] | V,
    ):
        self.value = value

    def eval(self, data: jabl[T], ignore_indices: jabl[bool]) -> jabl[Union[V, T]]:
        _data = data.map_when(self.value, ignore_indices.map(lambda x: not x))
        return _data
        
        

# %% Utils
def when_a_then_b_else_c(a: Iterable[bool], b: Iterable[T], c: Iterable[V]) -> jabl[T | V]:
    '''A utility function that mimics the behavior of the `when` method of `jabl`
    '''
    data = [b_i if a_i else c_i for a_i, b_i, c_i in zip(a, b, c)]
    return jabl(*data)
