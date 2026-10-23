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

ns = SimpleNamespace


def test_unset_fields_default_to_true():
    mentions = discord.AllowedMentions()

    assert mentions.everyone is True
    assert mentions.users is True
    assert mentions.roles is True
    assert mentions.replied_user is True
    assert mentions.to_dict() == {
        "parse": ["everyone", "users", "roles"],
        "replied_user": True,
    }


def test_merge_only_overrides_explicitly_set_fields():
    base = discord.AllowedMentions(everyone=False, users=[ns(id=1)])
    override = discord.AllowedMentions(roles=False)

    merged = base.merge(override)

    assert merged.to_dict() == {
        "parse": [],
        "users": [1],
        "replied_user": True,
    }


def test_merge_with_empty():
    base = discord.AllowedMentions(everyone=False, users=[ns(id=1)])

    # Merging with an all-default instance must not reset anything to True.
    assert base.merge(discord.AllowedMentions()).to_dict() == base.to_dict()


def test_setters() -> None:
    mentions = discord.AllowedMentions()
    mentions.everyone = False
    mentions.users = [ns(id=1)]

    assert mentions.to_dict() == {
        "parse": ["roles"],
        "users": [1],
        "replied_user": True,
    }
