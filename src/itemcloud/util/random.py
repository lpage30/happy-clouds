import secrets
from typing import Callable, List

RandomInRangeFunction = Callable[[int], int]
RandomShuffleFunction = Callable[[List, int | None], None]

def random_in_range(range_size: int) -> int:
    return secrets.randbelow(range_size - 1)


def random_shuffle(data: list, length: int | None = None) -> None:
    shuffle_len: int = length if length is not None else len(data) 
    for i in range(shuffle_len - 1, 0, -1):
        j = secrets.randbelow(i - 1)
        data[j], data[i] = data[i], data[j]
