"""
The MIT License (MIT)

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

from types import SimpleNamespace

import discord


def ns(**kwargs) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def test_get_single_attr_match():
    items = [ns(name="foo"), ns(name="bar"), ns(name="baz")]
    result = discord.utils.get(items, name="bar")
    assert result is not None
    assert result.name == "bar"


def test_get_returns_first_match():
    items = [ns(name="foo", value=1), ns(name="foo", value=2)]
    result = discord.utils.get(items, name="foo")
    assert result is not None
    assert result.value == 1


def test_get_no_match_returns_none():
    items = [ns(name="foo"), ns(name="bar")]
    assert discord.utils.get(items, name="baz") is None


def test_get_empty_iterable_returns_none():
    assert discord.utils.get([], name="foo") is None


def test_get_multiple_attrs():
    items = [ns(name="foo", value=1), ns(name="foo", value=2), ns(name="bar", value=1)]
    result = discord.utils.get(items, name="foo", value=2)
    assert result is not None
    assert result.value == 2


def test_get_multiple_attrs_no_match_returns_none():
    items = [ns(name="foo", value=1), ns(name="bar", value=2)]
    assert discord.utils.get(items, name="foo", value=2) is None


def test_get_nested_attr():
    items = [
        ns(inner=ns(name="foo")),
        ns(inner=ns(name="bar")),
    ]
    result = discord.utils.get(items, inner__name="bar")
    assert result is not None
    assert result.inner.name == "bar"


def test_get_match_at_start():
    items = [ns(name="foo"), ns(name="bar"), ns(name="baz")]
    result = discord.utils.get(items, name="foo")
    assert result is not None
    assert result.name == "foo"


def test_get_match_at_end():
    items = [ns(name="foo"), ns(name="bar"), ns(name="baz")]
    result = discord.utils.get(items, name="baz")
    assert result is not None
    assert result.name == "baz"
