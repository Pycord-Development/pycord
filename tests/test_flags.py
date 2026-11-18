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

import discord


def test_kwargs_set_and_get():
    flags = discord.MessageFlags(ephemeral=True, suppress_embeds=True)

    assert flags.ephemeral is True
    assert flags.suppress_embeds is True
    assert flags.crossposted is False
    assert flags.value == (1 << 6) | (1 << 2)

    flags.ephemeral = False
    assert flags.ephemeral is False
    assert flags.value == 1 << 2


def test_invalid_kwarg_raises():
    try:
        discord.MessageFlags(not_a_flag=True)
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError for unknown flag name")


def test_equality_and_hash():
    a = discord.MessageFlags(urgent=True)
    b = discord.MessageFlags._from_value(1 << 4)

    assert a == b
    assert hash(a) == hash(b)
    assert a != discord.MessageFlags()
    # Same value but different flag class must not compare equal.
    assert a != discord.AttachmentFlags._from_value(1 << 4)


def test_operators():
    a = discord.Intents(guilds=True, members=True)
    b = discord.Intents(members=True, invites=True)

    assert (a | b).value == (1 << 0) | (1 << 1) | (1 << 6)
    assert (a + b) == (a | b)
    assert (a & b).value == 1 << 1
    assert (a - b).value == 1 << 0
    assert (~a).value == ~a.value

    # Operators also accept class-level flag_value descriptors, on both sides.
    assert (a | discord.Intents.invites).invites is True
    assert (discord.Intents.invites | a).invites is True
    assert (a - discord.Intents.members).members is False


def test_reflected_sub():
    flags = discord.Intents(guilds=True, members=True)

    # ``flag - flags`` must be "flag without flags", not "flags without flag".
    result = discord.Intents.invites - flags
    assert result.value == 1 << 6
    assert result.invites is True
    assert result.guilds is False
    assert result.members is False

    assert (discord.Intents.guilds - flags).value == 0


def test_operator_with_other_type_raises():
    try:
        discord.MessageFlags() | discord.AttachmentFlags()
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError when combining different flag types")


def test_iter_skips_aliases():
    flags = dict(discord.PublicUserFlags(verified_bot_developer=True))

    assert flags["verified_bot_developer"] is True
    assert flags["staff"] is False
    assert "early_verified_bot_developer" not in flags


def test_system_channel_flags_are_inverted():
    # Discord's bits mean "suppress", so a set bit reads as False.
    flags = discord.SystemChannelFlags()
    assert flags.value == 0b1111
    assert not any(enabled for _, enabled in flags)

    flags.join_notifications = True
    assert flags.join_notifications is True
    assert flags.value & 1 == 0  # enabling clears the "suppress" bit

    raw = discord.SystemChannelFlags._from_value(1)
    assert raw.join_notifications is False
    assert raw.premium_subscriptions is True


def test_intents_factories():
    none = discord.Intents.none()
    assert none.value == 0
    assert not any(enabled for _, enabled in none)

    everything = discord.Intents.all()
    assert all(enabled for _, enabled in everything)

    default = discord.Intents.default()
    assert default.guilds is True
    assert default.presences is False
    assert default.members is False
    assert default.message_content is False


def test_intents_multi_bit_alias():
    intents = discord.Intents.none()
    intents.messages = True

    assert intents.guild_messages is True
    assert intents.dm_messages is True

    intents.dm_messages = False
    # Alias only reports True when every bit it covers is set.
    assert intents.messages is False


def test_member_cache_flags():
    assert discord.MemberCacheFlags() == discord.MemberCacheFlags.all()
    assert discord.MemberCacheFlags.none().value == 0

    intents = discord.Intents.none()
    intents.voice_states = True
    flags = discord.MemberCacheFlags.from_intents(intents)
    assert flags.voice is True
    assert flags.interaction is True
    assert flags.joined is False

    try:
        discord.MemberCacheFlags.all()._verify_intents(intents)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "expected ValueError when joined is set without members intent"
        )


def test_public_user_flags_all():
    flags = discord.PublicUserFlags(staff=True, active_developer=True)

    assert flags.all() == [discord.UserFlags.staff, discord.UserFlags.active_developer]
