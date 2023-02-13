import random

from jabl import jabl


def setup():
    return [random.randint(a=0, b=100) for _ in range(1_000_000)]

def profile(data: list[int]):
    (jabl(*data)
        .map(lambda x: x**2)
        .filter(lambda x: x > 5)
        .map(lambda x: x**0.5)
        .map(round)
        .collect()
    )

if __name__ == "__main__":
    data = setup()
    profile(data)
