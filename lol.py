from typing import Union, get_args, get_origin
from types import UnionType

aaa = Union[int, str, float]
print(get_origin(aaa), get_args(aaa), get_origin(aaa) is Union, get_origin(aaa) is UnionType)
    