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

# PEP 563: all annotations in this module are stored as strings at runtime.
# This file intentionally uses `from __future__ import annotations` so that
# every callback defined here exercises the exact scenario reported in #513.
from __future__ import annotations

import discord
from discord.commands import SlashCommand
from discord.commands.options import Option
from discord.enums import SlashCommandOptionType

# ---------------------------------------------------------------------------
# Callbacks — defined here so their __annotations__ are PEP-563 strings.
# ---------------------------------------------------------------------------


async def _ann_member(ctx, user: Option(discord.Member, "A member")):
    pass


async def _ann_str(ctx, name: Option(str, "A name")):
    pass


async def _ann_int(ctx, count: Option(int, "A count")):
    pass


async def _ann_role(ctx, role: Option(discord.Role, "A role")):
    pass


async def _ann_not_required(
    ctx, user: Option(discord.Member, "optional", required=False)
):
    pass


async def _plain_str(ctx, name: str):
    pass


async def _plain_int(ctx, count: int):
    pass


async def _default_member(
    ctx, user: discord.Member = Option(discord.Member, "A member")
):
    pass


async def _default_not_required(
    ctx,
    user: discord.Member = Option(
        discord.Member, "optional", required=False, default=None
    ),
):
    pass


# ---------------------------------------------------------------------------
# Option(...) as annotation under PEP 563
# ---------------------------------------------------------------------------


class TestOptionAsAnnotation:
    def test_member_input_type(self):
        cmd = SlashCommand(_ann_member, name="test")
        assert cmd.options[0].input_type == SlashCommandOptionType.user

    def test_str_input_type(self):
        cmd = SlashCommand(_ann_str, name="test")
        assert cmd.options[0].input_type == SlashCommandOptionType.string

    def test_int_input_type(self):
        cmd = SlashCommand(_ann_int, name="test")
        assert cmd.options[0].input_type == SlashCommandOptionType.integer

    def test_role_input_type(self):
        cmd = SlashCommand(_ann_role, name="test")
        assert cmd.options[0].input_type == SlashCommandOptionType.role

    def test_option_name_matches_param(self):
        cmd = SlashCommand(_ann_member, name="test")
        assert cmd.options[0].name == "user"

    def test_not_required_flag(self):
        cmd = SlashCommand(_ann_not_required, name="test")
        assert not cmd.options[0].required

    def test_raw_type_is_never_string(self):
        # Before the fix, _raw_type would be a str like "discord.Member"; after it
        # must always be an actual type or SlashCommandOptionType enum value.
        for func in (_ann_member, _ann_str, _ann_int, _ann_role):
            cmd = SlashCommand(func, name="test")
            raw = cmd.options[0]._raw_type
            assert isinstance(
                raw, (type, SlashCommandOptionType)
            ), f"{func.__name__}: _raw_type={raw!r} should be a class, not a string"


# ---------------------------------------------------------------------------
# Plain type annotations under PEP 563 — regression
# ---------------------------------------------------------------------------


class TestPlainAnnotationRegression:
    def test_str_annotation(self):
        cmd = SlashCommand(_plain_str, name="test")
        assert cmd.options[0].input_type == SlashCommandOptionType.string

    def test_int_annotation(self):
        cmd = SlashCommand(_plain_int, name="test")
        assert cmd.options[0].input_type == SlashCommandOptionType.integer

    def test_raw_type_is_never_string(self):
        for func in (_plain_str, _plain_int):
            cmd = SlashCommand(func, name="test")
            raw = cmd.options[0]._raw_type
            assert isinstance(
                raw, (type, SlashCommandOptionType)
            ), f"{func.__name__}: _raw_type={raw!r} should be a class, not a string"


# ---------------------------------------------------------------------------
# Option(...) as default value — pre-existing workaround must keep working
# ---------------------------------------------------------------------------


class TestOptionAsDefaultRegression:
    def test_member_default(self):
        cmd = SlashCommand(_default_member, name="test")
        assert cmd.options[0].input_type == SlashCommandOptionType.user

    def test_not_required_default(self):
        cmd = SlashCommand(_default_not_required, name="test")
        opt = cmd.options[0]
        assert opt.input_type == SlashCommandOptionType.user
        assert not opt.required
