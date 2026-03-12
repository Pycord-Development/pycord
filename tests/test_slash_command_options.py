from enum import Enum
from typing import Literal, Optional, Union

import pytest
from typing_extensions import Annotated

import discord
from discord import ChannelType, SlashCommandOptionType
from discord.commands.core import SlashCommand
from discord.commands.options import Option, OptionChoice


def _build_registered_slash_command(func):
    cmd = SlashCommand(func)
    bot = discord.Bot()
    bot.add_application_command(cmd)
    return cmd


def test_slash_command_parses_basic_option():
    async def greet(ctx, name: str):
        await ctx.respond(name)

    cmd = _build_registered_slash_command(greet)
    options = cmd.to_dict().get("options")

    assert len(options) == 1
    assert options[0]["name"] == "name"
    assert options[0]["type"] == SlashCommandOptionType.string.value


def test_slash_command_sets_default_and_required_flag():
    async def greet(ctx, name: str = "pycord"):
        await ctx.respond(name)

    cmd = _build_registered_slash_command(greet)

    assert len(cmd.options) == 1
    assert cmd.options[0].default == "pycord"
    assert cmd.options[0].required is False


def test_slash_command_uses_option_decorator_parameter_name_mapping():
    @discord.option(
        "display_name",
        str,
        parameter_name="display-name",
        description="Displayed name",
    )
    async def greet(ctx, display_name: str):
        await ctx.respond(display_name)

    cmd = _build_registered_slash_command(greet)
    option = cmd.to_dict().get("options")[0]

    assert option["name"] == "display-name"
    assert cmd.options[0]._param_name == "display_name"
    assert option["description"] == "Displayed name"


def test_option_choice_rejects_invalid_value_type():
    with pytest.raises(TypeError):
        OptionChoice(name="broken", value=object())


def test_option_to_dict_requires_parsed_type():
    option = Option(name="value", parameter_name="value", description="Some value")

    with pytest.raises(ValueError, match="Option type has not been set"):
        option.to_dict()


def test_option_rejects_min_length_for_non_string():
    option = Option(
        int,
        name="amount",
        parameter_name="amount",
        description="Amount",
        min_length=2,
    )

    with pytest.raises(ValueError, match="min_length and max_length"):
        option._handle_type()


def test_option_rejects_min_value_for_non_numeric():
    option = Option(
        str,
        name="label",
        parameter_name="label",
        description="Label",
        min_value=1,
    )

    with pytest.raises(ValueError, match="max_value is only applicable"):
        option._handle_type()


def test_option_parses_literal_annotation_choices():
    option = Option(
        Literal["red", "green"],
        name="color",
        parameter_name="color",
        description="Color",
    )
    option._handle_type()

    assert option._api_type is SlashCommandOptionType.string
    assert [choice.value for choice in option.choices] == ["red", "green"]


def test_option_parses_union_channel_types():
    option = Option(
        Union[discord.TextChannel, discord.VoiceChannel],
        name="where",
        parameter_name="where",
        description="Where",
    )
    option._handle_type()

    assert option._api_type is SlashCommandOptionType.channel
    assert sorted(option.channel_types, key=lambda t: t.value) == [
        ChannelType.text,
        ChannelType.voice,
    ]


def test_option_switches_to_autocomplete_above_25_choices():
    option = Option(
        str,
        name="pick",
        parameter_name="pick",
        description="Pick",
        choices=[f"choice-{i}" for i in range(26)],
    )

    assert option.autocomplete is not None
    assert option.choices == []


def test_annotation_metadata_option_is_used():
    async def echo(ctx, text: Annotated[str, discord.Option(description="Some text")]):
        await ctx.respond(text)

    cmd = _build_registered_slash_command(echo)
    option = cmd.to_dict().get("options")[0]

    assert option["type"] == SlashCommandOptionType.string.value
    assert option["description"] == "Some text"


def test_annotation_optional_type_parses_to_string():
    async def echo(ctx, text: Optional[str]):
        await ctx.respond(text)

    cmd = _build_registered_slash_command(echo)
    option = cmd.to_dict().get("options")[0]

    assert option["type"] == SlashCommandOptionType.string.value


def test_annotation_literal_exposes_choices():
    async def pick(ctx, value: Literal["a", "b"]):
        await ctx.respond(value)

    cmd = _build_registered_slash_command(pick)
    option = cmd.to_dict().get("options")[0]

    assert option["type"] == SlashCommandOptionType.string.value
    assert [choice["value"] for choice in option["choices"]] == ["a", "b"]


def test_annotation_literal_with_mixed_types_raises():
    async def pick(ctx, value: Literal["a", 1]):
        await ctx.respond(value)

    with pytest.raises(TypeError, match="Error processing parameter 'value'"):
        SlashCommand(pick)


def test_option_parses_choices_from_enum():
    class Flavor(Enum):
        VANILLA = "vanilla"
        CHOCOLATE = "chocolate"

    option = Option(
        Flavor,
        name="flavor",
        parameter_name="flavor",
        description="Flavor",
    )
    option._handle_type()

    assert option._api_type is SlashCommandOptionType.string
    assert [choice.value for choice in option.choices] == ["vanilla", "chocolate"]
