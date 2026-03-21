from types import UnionType
from typing import Union, get_args, get_origin

aaa = Union[int, str, float]
print(
    get_origin(aaa),
    get_args(aaa),
    get_origin(aaa) is Union,
    get_origin(aaa) is UnionType,
)
