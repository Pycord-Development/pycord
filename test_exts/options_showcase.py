from __future__ import annotations

from enum import Enum, IntEnum
from typing import Annotated, Literal, Optional, Union

import discord
from discord import OptionChoice, option
from discord.enums import SlashCommandOptionType
from discord.ext import commands


class Color(Enum):
    red = "red"
    green = "green"
    blue = "blue"


class Priority(IntEnum):
    low = 1
    medium = 2
    high = 3


async def color_autocomplete(
    ctx: discord.AutocompleteContext,
) -> list[OptionChoice]:
    choices = ["red", "green", "blue", "orange", "yellow"]
    return [OptionChoice(name=c) for c in choices if ctx.value.lower() in c]


class OptionShowcase(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(name="opt_primitives")
    async def opt_primitives(
        self,
        ctx: discord.ApplicationContext,
        text: str,
        count: int,
        ratio: float,
        flag: bool,
    ) -> None:
        await ctx.respond(
            f"text={text} count={count} ratio={ratio} flag={flag}"
        )

    @commands.slash_command(name="opt_choices")
    @option("color", description="Pick a color", choices=["red", "green", "blue"])
    @option("priority", description="Pick a priority", choices=Priority)
    async def opt_choices(
        self,
        ctx: discord.ApplicationContext,
        color: str,
        priority: Priority,
    ) -> None:
        await ctx.respond(f"color={color} priority={priority}")

    @commands.slash_command(name="opt_optionchoice")
    @option(
        "size",
        description="Pick a size",
        choices=[
            OptionChoice(name="Small", value="S"),
            OptionChoice(name="Large", value="L"),
        ],
    )
    async def opt_optionchoice(
        self,
        ctx: discord.ApplicationContext,
        size: str,
    ) -> None:
        await ctx.respond(f"size={size}")

    @commands.slash_command(name="opt_literal")
    async def opt_literal(
        self,
        ctx: discord.ApplicationContext,
        mode: Literal["fast", "safe"],
        level: Literal[1, 2, 3],
    ) -> None:
        await ctx.respond(f"mode={mode} level={level}")

    @commands.slash_command(name="opt_optional")
    async def opt_optional(
        self,
        ctx: discord.ApplicationContext,
        note: Optional[str] = None,
        amount: Optional[int] = None,
    ) -> None:
        await ctx.respond(f"note={note} amount={amount}")

    @commands.slash_command(name="opt_channels")
    async def opt_channels(
        self,
        ctx: discord.ApplicationContext,
        channel: Union[discord.TextChannel, discord.VoiceChannel],
        thread: discord.Thread,
    ) -> None:
        await ctx.respond(
            f"channel={channel.mention} thread={thread.mention}"
        )

    @commands.slash_command(name="opt_channeltypes")
    @option(
        "channel",
        discord.abc.GuildChannel,
        description="Pick a text or voice channel",
        channel_types=[
            discord.ChannelType.text,
            discord.ChannelType.voice,
        ],
    )
    async def opt_channeltypes(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.abc.GuildChannel,
    ) -> None:
        await ctx.respond(f"channel={channel.mention}")

    @commands.slash_command(name="opt_users")
    async def opt_users(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member,
        user: discord.User,
        role: discord.Role,
    ) -> None:
        await ctx.respond(
            f"member={member.mention} user={user.mention} role={role.name}"
        )

    @commands.slash_command(name="opt_union_user")
    async def opt_union_user(
        self,
        ctx: discord.ApplicationContext,
        target: Union[discord.Member, discord.User],
    ) -> None:
        await ctx.respond(f"target={target.mention}")

    @commands.slash_command(name="opt_attachment")
    async def opt_attachment(
        self,
        ctx: discord.ApplicationContext,
        file: discord.Attachment,
    ) -> None:
        if file:
            await ctx.respond(f"file={file.filename}")
        else:
            await ctx.respond("No file provided")

    @commands.slash_command(name="opt_decorator")
    @option(
        "value",
        SlashCommandOptionType.integer,
        description="Value 1-10",
        min_value=1,
        max_value=10,
    )
    @option(
        "text",
        SlashCommandOptionType.string,
        description="Text 1-10 chars",
        min_length=1,
        max_length=10,
    )
    async def opt_decorator(
        self,
        ctx: discord.ApplicationContext,
        value: int,
        text: str,
    ) -> None:
        await ctx.respond(f"value={value} text={text}")

    @commands.slash_command(name="opt_annotated")
    async def opt_annotated(
        self,
        ctx: discord.ApplicationContext,
        tag: Annotated[str, "ignored"],
    ) -> None:
        await ctx.respond(f"tag={tag}")

    @commands.slash_command(name="opt_autocomplete")
    @option("color", description="Pick a color", autocomplete=color_autocomplete)
    async def opt_autocomplete(
        self,
        ctx: discord.ApplicationContext,
        color: str,
    ) -> None:
        await ctx.respond(f"color={color}")


def setup(bot: discord.Bot) -> None:
    bot.add_cog(OptionShowcase(bot))
