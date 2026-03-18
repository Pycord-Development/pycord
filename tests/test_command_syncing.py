import copy
from typing import Any

import pytest
from typing_extensions import override

import discord
from discord import MISSING, Bot, SlashCommandGroup
from discord.bot import COMMAND_DEFAULTS, DefaultSetComparison
from discord.types.interactions import ApplicationCommand, ApplicationCommandOption

pytestmark = pytest.mark.asyncio


class SlashCommand(discord.SlashCommand):
    def __init__(self, **kwargs):
        if (r := kwargs.pop("func", None)) is not None:
            callback = r
        else:

            async def dummy_callback(ctx):
                pass

            callback = dummy_callback
        if (desc := kwargs.get("description")) is not None:
            kwargs.pop("description")
        else:
            desc = "desc"
        if (name := kwargs.get("name")) is not None:
            kwargs.pop("name")
        else:
            name = "testing"
        super().__init__(callback, name=name, description=desc, **kwargs)
        if self.integration_types is None:
            self.integration_types = {discord.IntegrationType.guild_install}
        if self.contexts is None:
            self.contexts = {
                discord.InteractionContextType.private_channel,
                discord.InteractionContextType.bot_dm,
                discord.InteractionContextType.guild,
            }


remote_dummy_base: dict = {
    "id": "1",
    "application_id": "1",
    "version": "1",
    "default_member_permissions": None,
    "type": 1,
    "name": "testing",
    "name_localizations": None,
    "description": "desc",
    "description_localizations": None,
    "dm_permission": True,
    "contexts": [0, 1, 2],
    "integration_types": [0],
    "nsfw": False,
}


class DummyBot(Bot):
    @override
    async def _get_command_defaults(self):
        command_defaults = COMMAND_DEFAULTS.copy()
        command_defaults["integration_types"] = DefaultSetComparison(
            (MISSING, {0}), lambda x, y: set(x) == set(y)
        )
        return command_defaults


async def edit_needed(
    local: SlashCommand | SlashCommandGroup, remote: ApplicationCommand
):
    b = DummyBot()
    b.add_application_command(local)
    r = await b.get_desynced_commands(prefetched=[remote])
    return r[0]["action"] == "edit"


class TestCommandSyncing:
    @staticmethod
    def dict_factory(**kwargs) -> ApplicationCommand:
        remote_dummy = copy.deepcopy(remote_dummy_base)
        for key, value in kwargs.items():
            if value == MISSING:
                del remote_dummy[key]
            else:
                remote_dummy.update({key: value})
        return remote_dummy

    async def test_default(self):
        assert not await edit_needed(SlashCommand(), TestCommandSyncing.dict_factory())

    async def test_default_member_permissions_defaults(self):
        assert not await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(default_member_permissions=None),
        )
        assert not await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(default_member_permissions=MISSING),
        )

    async def test_default_member_permissions(self):
        assert await edit_needed(
            SlashCommand(default_member_permissions=discord.Permissions(8)),
            TestCommandSyncing.dict_factory(),
        )
        assert await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(default_member_permissions="8"),
        )

    async def test_type_defaults(self):
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(type=1)
        )
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(type=MISSING)
        )

    async def test_name_localizations_defaults(self):
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(name_localizations={})
        )
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(name_localizations=None)
        )
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(name_localizations=MISSING)
        )

    async def test_name_localizations(self):
        assert await edit_needed(
            SlashCommand(name_localizations={"no": "testing_no"}),
            TestCommandSyncing.dict_factory(),
        )
        assert await edit_needed(
            SlashCommand(name_localizations={"no": "testing_no", "ja": "testing_ja"}),
            TestCommandSyncing.dict_factory(),
        )
        assert await edit_needed(
            SlashCommand(name_localizations={"ja": "testing_ja", "no": "testing_no"}),
            TestCommandSyncing.dict_factory(),
        )
        assert await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(name_localizations={"no": "testing_no"}),
        )
        assert await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(
                name_localizations={"no": "testing_no", "ja": "testing_ja"}
            ),
        )
        assert await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(
                name_localizations={"ja": "testing_ja", "no": "testing_no"}
            ),
        )

    async def test_description_localizations_defaults(self):
        assert not await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(description_localizations={}),
        )
        assert not await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(description_localizations=None),
        )
        assert not await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(description_localizations=MISSING),
        )

    async def test_description_localizations(self):
        assert await edit_needed(
            SlashCommand(description_localizations={"no": "testing_desc_es"}),
            TestCommandSyncing.dict_factory(),
        )
        assert await edit_needed(
            SlashCommand(
                description_localizations={
                    "no": "testing_desc_es",
                    "ja": "testing_desc_jp",
                }
            ),
            TestCommandSyncing.dict_factory(),
        )
        assert await edit_needed(
            SlashCommand(
                description_localizations={
                    "ja": "testing_desc_jp",
                    "no": "testing_desc_es",
                }
            ),
            TestCommandSyncing.dict_factory(),
        )
        assert await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(
                description_localizations={"no": "testing_desc_es"}
            ),
        )
        assert await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(
                description_localizations={
                    "no": "testing_desc_es",
                    "ja": "testing_desc_jp",
                }
            ),
        )
        assert await edit_needed(
            SlashCommand(),
            TestCommandSyncing.dict_factory(
                description_localizations={
                    "ja": "testing_desc_jp",
                    "no": "testing_desc_es",
                }
            ),
        )

    async def test_description(self):
        assert await edit_needed(
            SlashCommand(description="different"), TestCommandSyncing.dict_factory()
        )
        assert await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(description="different")
        )

    async def test_contexts_defaults(self):
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(contexts=[2, 1, 0])
        )

    async def test_contexts(self):
        assert await edit_needed(
            SlashCommand(contexts=set()), TestCommandSyncing.dict_factory()
        )
        assert await edit_needed(
            SlashCommand(contexts={discord.InteractionContextType.guild}),
            TestCommandSyncing.dict_factory(),
        )
        assert await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(contexts=[])
        )
        assert await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(contexts=[1])
        )

    async def test_integration_types_defaults(self):
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(integration_types=MISSING)
        )

    async def test_integration_types(self):
        assert await edit_needed(
            SlashCommand(integration_types=set()), TestCommandSyncing.dict_factory()
        )
        assert await edit_needed(
            SlashCommand(integration_types={discord.IntegrationType.user_install}),
            TestCommandSyncing.dict_factory(),
        )
        assert await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(integration_types=[])
        )
        assert await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(integration_types=[1])
        )

    async def test_nsfw_defaults(self):
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(nsfw=False)
        )
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(nsfw=MISSING)
        )

    async def test_nsfw(self):
        assert await edit_needed(
            SlashCommand(nsfw=True), TestCommandSyncing.dict_factory()
        )
        assert await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(nsfw=True)
        )

    async def test_options_defaults(self):
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(options=[])
        )
        assert not await edit_needed(
            SlashCommand(), TestCommandSyncing.dict_factory(options=MISSING)
        )


class TestCommandSyncingWithOption:
    @staticmethod
    def dict_factory(**kwargs) -> dict[str, Any]:
        remote_dummy = copy.deepcopy(remote_dummy_base)
        remote_dummy["options"] = [
            {
                "type": 3,
                "name": "user",
                "name_localizations": None,
                "description": "name",
                "description_localizations": None,
                "required": True,
            }
        ]
        for key, value in kwargs.items():
            if value == MISSING:
                del remote_dummy["options"][0][key]
            else:
                remote_dummy["options"][0].update({key: value})
        return remote_dummy

    class SlashOptionCommand(SlashCommand):
        @staticmethod
        def default_option() -> discord.Option:
            return discord.Option(str, name="user", description="name")

        def __init__(
            self, options: list[discord.Option | dict] | None = None, **kwargs
        ):
            async def dummy_callback(ctx, user):
                pass

            if options is None:
                options = [self.default_option()]
            for n, i in enumerate(options):
                if isinstance(i, dict):
                    d = self.default_option()
                    for key, value in i.items():
                        d.__setattr__(key, value)
                    options[n] = d
            super().__init__(func=dummy_callback, options=options, **kwargs)

    async def test_type(self):
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"input_type": discord.SlashCommandOptionType(5)}]
            ),
            TestCommandSyncingWithOption.dict_factory(),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(type=5),
        )

    async def test_name(self):
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"name": "pycord"}]),
            TestCommandSyncingWithOption.dict_factory(),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(name="pycord"),
        )

    async def test_description(self):
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"description": "pycord_desc"}]
            ),
            TestCommandSyncingWithOption.dict_factory(),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(description="pycord_desc"),
        )

    async def test_name_localizations_defaults(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(name_localizations={}),
        )
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(name_localizations=None),
        )
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(name_localizations=MISSING),
        )

    async def test_name_localizations(self):
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"name_localizations": {"no": "testing_no"}}]
            ),
            TestCommandSyncingWithOption.dict_factory(),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"name_localizations": {"no": "testing_no", "ja": "testing_ja"}}]
            ),
            TestCommandSyncingWithOption.dict_factory(),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"name_localizations": {"ja": "testing_ja", "no": "testing_no"}}]
            ),
            TestCommandSyncingWithOption.dict_factory(),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(
                name_localizations={"no": "testing_no"}
            ),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(
                name_localizations={"no": "testing_no", "ja": "testing_ja"}
            ),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(
                name_localizations={"ja": "testing_ja", "no": "testing_no"}
            ),
        )

    async def test_description_localizations_defaults(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(description_localizations={}),
        )
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(description_localizations=None),
        )
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(
                description_localizations=MISSING
            ),
        )

    async def test_description_localizations(self):
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"description_localizations": {"no": "testing_desc_es"}}]
            ),
            TestCommandSyncingWithOption.dict_factory(),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [
                    {
                        "description_localizations": {
                            "no": "testing_desc_es",
                            "ja": "testing_desc_jp",
                        }
                    }
                ]
            ),
            TestCommandSyncingWithOption.dict_factory(),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [
                    {
                        "description_localizations": {
                            "ja": "testing_desc_jp",
                            "no": "testing_desc_es",
                        }
                    }
                ]
            ),
            TestCommandSyncingWithOption.dict_factory(),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(
                description_localizations={"no": "testing_desc_es"}
            ),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(
                description_localizations={
                    "no": "testing_desc_es",
                    "ja": "testing_desc_jp",
                }
            ),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(
                description_localizations={
                    "ja": "testing_desc_jp",
                    "no": "testing_desc_es",
                }
            ),
        )

    async def test_required_defaults(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"required": False}]),
            TestCommandSyncingWithOption.dict_factory(required=MISSING),
        )
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(required=True),
        )

    async def test_required(self):
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(required=MISSING),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(required=False),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"required": False}]),
            TestCommandSyncingWithOption.dict_factory(required=True),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"required": None}]),
            TestCommandSyncingWithOption.dict_factory(required=MISSING),
        )

    async def test_choices_defaults(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(choices=MISSING),
        )
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(choices=[]),
        )
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [
                    {
                        "choices": [
                            discord.OptionChoice("a"),
                            discord.OptionChoice("b"),
                            discord.OptionChoice("c"),
                        ]
                    }
                ]
            ),
            TestCommandSyncingWithOption.dict_factory(
                choices=[
                    {"name": "a", "value": "a"},
                    {"name": "b", "value": "b"},
                    {"name": "c", "value": "c"},
                ]
            ),
        )

    async def test_choices(self):
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"choices": [discord.OptionChoice("a"), discord.OptionChoice("b")]}]
            ),
            TestCommandSyncingWithOption.dict_factory(
                choices=[
                    {"name": "a", "value": "a"},
                    {"name": "b", "value": "b"},
                    {"name": "c", "value": "c"},
                ]
            ),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [
                    {
                        "choices": [
                            discord.OptionChoice("a"),
                            discord.OptionChoice("b"),
                            discord.OptionChoice("c"),
                        ]
                    }
                ]
            ),
            TestCommandSyncingWithOption.dict_factory(
                choices=[{"name": "a", "value": "a"}, {"name": "b", "value": "b"}]
            ),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [
                    {
                        "choices": [
                            discord.OptionChoice("a"),
                            discord.OptionChoice("x"),
                            discord.OptionChoice("c"),
                        ]
                    }
                ]
            ),
            TestCommandSyncingWithOption.dict_factory(
                choices=[
                    {"name": "a", "value": "a"},
                    {"name": "b", "value": "b"},
                    {"name": "c", "value": "c"},
                ]
            ),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [
                    {
                        "choices": [
                            discord.OptionChoice("a"),
                            discord.OptionChoice("b"),
                            discord.OptionChoice("c"),
                        ]
                    }
                ]
            ),
            TestCommandSyncingWithOption.dict_factory(
                choices=[
                    {"name": "a", "value": "a"},
                    {"name": "x", "value": "x"},
                    {"name": "c", "value": "c"},
                ]
            ),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"choices": [discord.OptionChoice("a"), discord.OptionChoice("c")]}]
            ),
            TestCommandSyncingWithOption.dict_factory(
                choices=[
                    {"name": "a", "value": "a"},
                    {"name": "b", "value": "b"},
                    {"name": "c", "value": "c"},
                ]
            ),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [
                    {
                        "choices": [
                            discord.OptionChoice("a"),
                            discord.OptionChoice("b"),
                            discord.OptionChoice("c"),
                        ]
                    }
                ]
            ),
            TestCommandSyncingWithOption.dict_factory(
                choices=[{"name": "a", "value": "a"}, {"name": "c", "value": "c"}]
            ),
        )

    async def test_channel_type_defaults(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(channel_types=[]),
        )
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(channel_types=MISSING),
        )
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"channel_types": [discord.ChannelType(0), discord.ChannelType(1)]}]
            ),
            TestCommandSyncingWithOption.dict_factory(channel_types=[0, 1]),
        )

    async def test_channel_types(self):
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"channel_types": [discord.ChannelType(0)]}]
            ),
            TestCommandSyncingWithOption.dict_factory(channel_types=[0, 1]),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"channel_types": [discord.ChannelType(0), discord.ChannelType(1)]}]
            ),
            TestCommandSyncingWithOption.dict_factory(channel_types=[0]),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(channel_types=[0, 1]),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"channel_types": [discord.ChannelType(0), discord.ChannelType(1)]}]
            ),
            TestCommandSyncingWithOption.dict_factory(channel_types=MISSING),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"channel_types": [discord.ChannelType(0), discord.ChannelType(5)]}]
            ),
            TestCommandSyncingWithOption.dict_factory(channel_types=[0, 1]),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"channel_types": [discord.ChannelType(0), discord.ChannelType(1)]}]
            ),
            TestCommandSyncingWithOption.dict_factory(channel_types=[0, 5]),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [
                    {
                        "channel_types": [
                            discord.ChannelType(0),
                            discord.ChannelType(1),
                            discord.ChannelType(15),
                        ]
                    }
                ]
            ),
            TestCommandSyncingWithOption.dict_factory(channel_types=[0, 1]),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"channel_types": [discord.ChannelType(0), discord.ChannelType(1)]}]
            ),
            TestCommandSyncingWithOption.dict_factory(channel_types=[0, 1, 15]),
        )

    async def test_min_value_defaults(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(min_value=MISSING),
        )

    async def test_min_value(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 5}]),
            TestCommandSyncingWithOption.dict_factory(min_value=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 6}]),
            TestCommandSyncingWithOption.dict_factory(min_value=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 5}]),
            TestCommandSyncingWithOption.dict_factory(min_value=6),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(min_value=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 5}]),
            TestCommandSyncingWithOption.dict_factory(),
        )

        # Floats
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 5.5}]),
            TestCommandSyncingWithOption.dict_factory(min_value=5.5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 6.0}]),
            TestCommandSyncingWithOption.dict_factory(min_value=5.0),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 5.77}]),
            TestCommandSyncingWithOption.dict_factory(min_value=6.123),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(min_value=5.333),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 5.333}]),
            TestCommandSyncingWithOption.dict_factory(),
        )

        # Mixed
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 5.0}]),
            TestCommandSyncingWithOption.dict_factory(min_value=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 6}]),
            TestCommandSyncingWithOption.dict_factory(min_value=5.0),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_value": 5.0}]),
            TestCommandSyncingWithOption.dict_factory(min_value=6),
        )

    async def test_max_value_defaults(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(max_value=MISSING),
        )

    async def test_max_value(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 5}]),
            TestCommandSyncingWithOption.dict_factory(max_value=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 6}]),
            TestCommandSyncingWithOption.dict_factory(max_value=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 5}]),
            TestCommandSyncingWithOption.dict_factory(max_value=6),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(max_value=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 5}]),
            TestCommandSyncingWithOption.dict_factory(),
        )

        # Floats
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 5.5}]),
            TestCommandSyncingWithOption.dict_factory(max_value=5.5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 6.0}]),
            TestCommandSyncingWithOption.dict_factory(max_value=5.0),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 5.77}]),
            TestCommandSyncingWithOption.dict_factory(max_value=6.123),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(max_value=5.333),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 5.333}]),
            TestCommandSyncingWithOption.dict_factory(),
        )

        # Mixed
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 5.0}]),
            TestCommandSyncingWithOption.dict_factory(max_value=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 6}]),
            TestCommandSyncingWithOption.dict_factory(max_value=5.0),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_value": 5.0}]),
            TestCommandSyncingWithOption.dict_factory(max_value=6),
        )

    async def test_min_length_defaults(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(min_length=MISSING),
        )

    async def test_min_length(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_length": 5}]),
            TestCommandSyncingWithOption.dict_factory(min_length=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_length": 6}]),
            TestCommandSyncingWithOption.dict_factory(min_length=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_length": 5}]),
            TestCommandSyncingWithOption.dict_factory(min_length=6),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(min_length=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"min_length": 5}]),
            TestCommandSyncingWithOption.dict_factory(),
        )

    async def test_max_length_defaults(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(max_length=MISSING),
        )

    async def test_max_length(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_length": 5}]),
            TestCommandSyncingWithOption.dict_factory(max_length=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_length": 6}]),
            TestCommandSyncingWithOption.dict_factory(max_length=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_length": 5}]),
            TestCommandSyncingWithOption.dict_factory(max_length=6),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(max_length=5),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand([{"max_length": 5}]),
            TestCommandSyncingWithOption.dict_factory(),
        )

    async def test_autocomplete_default(self):
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(autocomplete=False),
        )
        assert not await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(autocomplete=MISSING),
        )

    async def test_autocomplete(self):
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(),
            TestCommandSyncingWithOption.dict_factory(autocomplete=True),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"autocomplete": lambda x: x}]
            ),
            TestCommandSyncingWithOption.dict_factory(autocomplete=False),
        )
        assert await edit_needed(
            TestCommandSyncingWithOption.SlashOptionCommand(
                [{"autocomplete": lambda x: x}]
            ),
            TestCommandSyncingWithOption.dict_factory(autocomplete=MISSING),
        )


class TestSubCommandSyncing:

    @staticmethod
    def dict_factory(top: dict, command: dict) -> dict[str, Any]:
        remote_dummy = TestCommandSyncing.dict_factory(**top)
        if "name" not in top:
            remote_dummy["name"] = "subcommand"
        remote_dummy["options"] = [
            ApplicationCommandOption(
                type=1,
                name="testing",
                name_localizations=None,
                description="desc",
                description_localizations=None,
                required=True,
            )
        ]
        for key, value in command.items():
            if value == MISSING:
                del remote_dummy["options"][0][key]
            else:
                remote_dummy["options"][0].update({key: value})
        return remote_dummy

    async def test_parent_name(self):
        async def edit_needed(
            local: SlashCommand | SlashCommandGroup, remote: ApplicationCommand
        ):
            b = DummyBot()
            b.add_application_command(local)
            r = await b.get_desynced_commands(prefetched=[remote])
            return r[0]["action"] == "upsert" and r[1]["action"] == "delete"

        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand())
        assert not await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("newgroupname")
        s.add_command(SlashCommand())
        assert await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand())
        assert await edit_needed(s, self.dict_factory({"name": "new_discord_name"}, {}))

    async def test_parent_attrs(self):
        s = SlashCommandGroup("subcommand", description="newdescname")
        s.add_command(SlashCommand())
        assert await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand())
        assert await edit_needed(
            s, self.dict_factory({"description": "new_discord_desc"}, {})
        )

    async def test_child_name(self):
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand(parent=s))
        assert not await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand(name="newsubcommand_name"))
        assert await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand())
        assert await edit_needed(s, self.dict_factory({}, {"name": "new_discord_name"}))

    async def test_child(self):
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand(description="newdescript"))
        assert await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand())
        assert await edit_needed(
            s, self.dict_factory({}, {"description": "new_descript"})
        )

    async def test_subcommand_counts(self):
        s = SlashCommandGroup("subcommand")
        assert await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand(parent=s))
        rd = self.dict_factory({}, {})
        rd["options"] = []
        assert await edit_needed(s, rd)

    async def test_multi_subcommand_diff(self):
        # No Different
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand(parent=s))
        s.add_command(SlashCommand(parent=s, name="another"))
        rd = self.dict_factory({}, {})
        rd["options"].append(
            ApplicationCommandOption(
                type=1,
                name="another",
                name_localizations=None,
                description="desc",
                description_localizations=None,
                required=True,
            )
        )
        assert not await edit_needed(s, rd)

        # First Local Different
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand(parent=s, description="different"))
        s.add_command(SlashCommand(parent=s, name="another"))
        rd = self.dict_factory({}, {})
        rd["options"].append(
            ApplicationCommandOption(
                type=1,
                name="another",
                name_localizations=None,
                description="desc",
                description_localizations=None,
                required=True,
            )
        )
        assert await edit_needed(s, rd)

        # Second Local Different
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand(parent=s))
        s.add_command(SlashCommand(parent=s, name="another", description="different"))
        rd = self.dict_factory({}, {})
        rd["options"].append(
            ApplicationCommandOption(
                type=1,
                name="another",
                name_localizations=None,
                description="desc",
                description_localizations=None,
                required=True,
            )
        )
        assert await edit_needed(s, rd)

        # First Remote Different
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand(parent=s))
        s.add_command(SlashCommand(parent=s, name="another"))
        rd = self.dict_factory({}, {"description": "different"})
        rd["options"].append(
            ApplicationCommandOption(
                type=1,
                name="another",
                name_localizations=None,
                description="desc",
                description_localizations=None,
                required=True,
            )
        )
        assert await edit_needed(s, rd)

        # Second Remote Different
        s = SlashCommandGroup("subcommand")
        s.add_command(SlashCommand(parent=s))
        s.add_command(SlashCommand(parent=s, name="another"))
        rd = self.dict_factory({}, {})
        rd["options"].append(
            ApplicationCommandOption(
                type=1,
                name="another",
                name_localizations=None,
                description="different",
                description_localizations=None,
                required=True,
            )
        )
        assert await edit_needed(s, rd)


class TestSubSubCommandSyncing:

    @staticmethod
    def dict_factory(top: dict, command: dict) -> dict[str, Any]:
        remote_dummy = TestCommandSyncing.dict_factory(**top)
        if "name" not in top:
            remote_dummy["name"] = "subcommand"
        remote_dummy["options"] = [
            ApplicationCommandOption(
                type=2,
                name="testing",
                name_localizations=None,
                description="desc",
                description_localizations=None,
                required=True,
                options=[
                    ApplicationCommandOption(
                        type=1,
                        name="testing",
                        name_localizations=None,
                        description="desc",
                        description_localizations=None,
                        required=True,
                    )
                ],
            )
        ]
        for key, value in command.items():
            if value == MISSING:
                del remote_dummy["options"][0]["options"][0][key]
            else:
                remote_dummy["options"][0]["options"][0].update({key: value})
        return remote_dummy

    async def test_child_name(self):
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand(parent=ss))
        assert not await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand(name="newsubcommand_name"))
        assert await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand())
        assert await edit_needed(s, self.dict_factory({}, {"name": "new_discord_name"}))

    async def test_child(self):
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand(description="newdescript"))
        assert await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand())
        assert await edit_needed(
            s, self.dict_factory({}, {"description": "new_descript"})
        )

    async def test_subsubcommand_counts(self):
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        assert await edit_needed(s, self.dict_factory({}, {}))
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand(parent=ss))
        rd = self.dict_factory({}, {})
        rd["options"][0]["options"] = []
        assert await edit_needed(s, rd)

    async def test_multi_subsubcommand_diff(self):
        # No Different
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand(parent=ss))
        ss.add_command(SlashCommand(parent=ss, name="another"))
        rd = self.dict_factory({}, {})
        rd["options"][0]["options"].append(
            ApplicationCommandOption(
                type=1,
                name="another",
                name_localizations=None,
                description="desc",
                description_localizations=None,
                required=True,
            )
        )
        assert not await edit_needed(s, rd)

        # First Local Different
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand(parent=ss, description="different"))
        ss.add_command(SlashCommand(parent=ss, name="another"))
        rd = self.dict_factory({}, {})
        rd["options"][0]["options"].append(
            ApplicationCommandOption(
                type=1,
                name="another",
                name_localizations=None,
                description="desc",
                description_localizations=None,
                required=True,
            )
        )
        assert await edit_needed(s, rd)

        # Second Local Different
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand(parent=ss))
        ss.add_command(SlashCommand(parent=ss, name="another", description="different"))
        rd = self.dict_factory({}, {})
        rd["options"][0]["options"].append(
            ApplicationCommandOption(
                type=1,
                name="another",
                name_localizations=None,
                description="desc",
                description_localizations=None,
                required=True,
            )
        )
        assert await edit_needed(s, rd)

        # First Remote Different
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand(parent=ss))
        ss.add_command(SlashCommand(parent=ss, name="another"))
        rd = self.dict_factory({}, {"description": "different"})
        rd["options"][0]["options"].append(
            ApplicationCommandOption(
                type=1,
                name="another",
                name_localizations=None,
                description="desc",
                description_localizations=None,
                required=True,
            )
        )
        assert await edit_needed(s, rd)

        # Second Remote Different
        s = SlashCommandGroup("subcommand")
        ss = s.create_subgroup("testing", description="desc")
        ss.add_command(SlashCommand(parent=ss))
        ss.add_command(SlashCommand(parent=ss, name="another"))
        rd = self.dict_factory({}, {})
        rd["options"][0]["options"].append(
            ApplicationCommandOption(
                type=1,
                name="another",
                name_localizations=None,
                description="different",
                description_localizations=None,
                required=True,
            )
        )
        assert await edit_needed(s, rd)
