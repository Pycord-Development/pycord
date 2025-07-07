"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

# mypy: implicit-reexport=True
from typing import TypeVar

import pytest

from discord.utils import (
    MISSING,
    find,
    generate_snowflake,
    snowflake_time,
    utcnow,
)

from .helpers import coroutine

A = TypeVar("A")
B = TypeVar("B")


def test_temporary():
    assert True


# def test_copy_doc() -> None:
#     def foo(a: A, b: B) -> Tuple[A, B]:
#         """
#         This is a test function.
#         """
#         return a, b
#
#     @copy_doc(foo)
#     def bar(a, b):  # type: ignore[no-untyped-def]
#         return a, b
#
#     assert bar.__doc__ == foo.__doc__
#     assert signature(bar) == signature(foo)
#
#
# def test_snowflake() -> None:
#     now = utcnow().replace(microsecond=0)
#     snowflake = time_snowflake(now)
#     assert snowflake_time(snowflake) == now
#
#
# def test_missing() -> None:
#     assert MISSING != object()
#     assert not MISSING
#     assert repr(MISSING) == '...'
#
# def test_find_get() -> None:
#     class Obj:
#         def __init__(self, value: int):
#             self.value = value
#             self.deep = self
#
#         def __eq__(self, other: Any) -> bool:
#             return isinstance(other, self.__class__) and self.value == other.value
#
#         def __repr__(self) -> str:
#             return f'<Obj {self.value}>'
#
#     obj_list = [Obj(i) for i in range(10)]
#     for i in range(11):
#         for val in (
#                 find(lambda o: o.value == i, obj_list),
#                 get(obj_list, value=i),
#                 get(obj_list, deep__value=i),
#                 get(obj_list, value=i, deep__value=i),
#         ):
#             if i >= len(obj_list):
#                 assert val is None
#             else:
#                 assert val == Obj(i)
#
#
# def test_unique() -> None:
#     values = [random.randint(0, 100) for _ in range(1000)]
#     unique = _unique(values)
#     unique.sort()
#     assert unique == list(set(values))
#
#
# @pytest.mark.parametrize('use_clock', (True, False))
# @pytest.mark.parametrize('value', list(range(0, 100, random.randrange(5, 10))))
# def test_parse_ratelimit_header(use_clock, value):  # type: ignore[no-untyped-def]
#     class RatelimitRequest:
#         def __init__(self, reset_after: int):
#             self.headers = {
#                 'X-Ratelimit-Reset-After': reset_after,
#                 'X-Ratelimit-Reset': (utcnow() + datetime.timedelta(seconds=reset_after)).timestamp(),
#             }
#
#     assert round(_parse_ratelimit_header(RatelimitRequest(value), use_clock=use_clock)) == value
#
#
# @pytest.mark.parametrize('value', range(5))
# async def test_maybe_coroutine(value) -> None:  # type: ignore[no-untyped-def]
#     assert value == await maybe_coroutine(lambda v: v, value)
#     assert value == await maybe_coroutine(coroutine, value)
#
#
# @pytest.mark.parametrize('size', list(range(10, 20)))
# @pytest.mark.filterwarnings("ignore:coroutine 'coroutine' was never awaited")
# async def test_async_all(size) -> None:  # type: ignore[no-untyped-def]
#     values = []
#     raw_values = []
#
#     for i in range(size):
#         value = random.choices((True, False), (size - 1, 1))[0]
#         raw_values.append(value)
#         values.append(coroutine(value) if random.choice((True, False)) else value)
#
#     assert all(raw_values) == await async_all(values)
