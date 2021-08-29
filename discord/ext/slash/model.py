import asyncio
import datetime
import typing
from contextlib import suppress
from enum import IntEnum
from inspect import iscoroutinefunction

import discord
from discord.ext.commands import BucketType, CommandOnCooldown, CooldownMapping

from . import error, http
from .dpy_overrides import ComponentMessage


class ChoiceData:
    """
    Command choice data object

    :ivar name: Name of the choice, this is what the user will see
    :ivar value: Values of the choice, this is what discord will return to you
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __eq__(self, other):
        return isinstance(other, ChoiceData) and self.__dict__ == other.__dict__


class OptionData:
    """
    Command option data object

    :ivar name: Name of the option.
    :ivar description: Description of the option.
    :ivar required: If the option is required.
    :ivar choices: A list of :class:`ChoiceData`, cannot be present on subcommand groups
    :ivar options: List of :class:`OptionData`, this will be present if it's a subcommand group
    """

    def __init__(self, name, description, required=False, choices=None, options=None, **kwargs):
        self.name = name
        self.description = description
        self.type = kwargs.get("type")
        if self.type is None:
            raise error.IncorrectCommandData("type is required for options")
        self.required = required
        if choices is not None:
            self.choices = []
            for choice in choices:
                self.choices.append(ChoiceData(**choice))
        else:
            self.choices = None

        if self.type in (1, 2):
            self.options = []
            if options is not None:
                for option in options:
                    self.options.append(OptionData(**option))
            elif self.type == 2:
                raise error.IncorrectCommandData(
                    "Options are required for subcommands / subcommand groups"
                )

    def __eq__(self, other):
        return isinstance(other, OptionData) and self.__dict__ == other.__dict__


class CommandData:
    """
    Slash command data object

    :ivar name: Name of the command.
    :ivar description: Description of the command.
    :ivar default_permission: Indicates whether users should have permissions to run this command by default.
    :ivar options: List of :class:`OptionData`.
    :ivar id: Command id, this is received from discord so may not be present
    :ivar application_id: The application id of the bot, required only when the application id and bot id are different. (old bots)
    """

    def __init__(
        self,
        name,
        description=None,
        options=None,
        default_permission=True,
        id=None,
        application_id=None,
        version=None,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.default_permission = default_permission
        self.id = id
        self.application_id = application_id
        self.version = version
        if options is not None:
            self.options = []
            for option in options:
                self.options.append(OptionData(**option))
        else:
            self.options = None

    def __eq__(self, other):
        if isinstance(other, CommandData):
            return (
                self.name == other.name
                and self.description == other.description
                and self.options == other.options
                and self.default_permission == other.default_permission
            )
        else:
            return False


class CallbackObject:
    """
    Callback object of this extension.

    .. warning::
        Do not manually init this model.

    :ivar func: The coroutine of the command.
    :ivar __commands_checks__: Check of the command.
    """

    def __init__(self, func):
        self.func = func

        # Ref https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/core.py#L1447
        # Since this isn't inherited from `discord.ext.commands.Command`, discord.py's check decorator will
        # add checks at this var.
        self.__commands_checks__ = []
        if hasattr(self.func, "__commands_checks__"):
            self.__commands_checks__ = self.func.__commands_checks__

        cooldown = None
        if hasattr(self.func, "__commands_cooldown__"):
            cooldown = self.func.__commands_cooldown__
        try:
            self._buckets = CooldownMapping(cooldown)
        except TypeError:
            self._buckets = CooldownMapping(cooldown, BucketType.default)

        self._max_concurrency = None
        if hasattr(self.func, "__commands_max_concurrency__"):
            self._max_concurrency = self.func.__commands_max_concurrency__

        self.on_error = None

    def error(self, coro):
        """
        A decorator that registers a coroutine as a local error handler.

        Works the same way as it does in d.py

        :param: :ref:`coroutine <coroutine>` - The coroutine to register as the local error handler

        :raises: TypeError - The coroutine passed is not a coroutine
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("The error handler must be a coroutine.")
        self.on_error = coro
        return coro

    def _prepare_cooldowns(self, ctx):
        """
        Ref https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/core.py#L765
        """
        if self._buckets.valid:
            dt = ctx.created_at
            current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            bucket = self._buckets.get_bucket(ctx, current)
            retry_after = bucket.update_rate_limit(current)
            if retry_after:
                raise CommandOnCooldown(bucket, retry_after)

    async def _concurrency_checks(self, ctx):
        """The checks required for cooldown and max concurrency."""
        # max concurrency checks
        if self._max_concurrency is not None:
            await self._max_concurrency.acquire(ctx)
        try:
            # cooldown checks
            self._prepare_cooldowns(ctx)
        except Exception:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(ctx)
            raise

    async def invoke(self, *args, **kwargs):
        """
        Invokes the command.

        :param args: Args for the command.
        :raises: .error.CheckFailure
        """
        can_run = await self.can_run(args[0])
        if not can_run:
            raise error.CheckFailure

        await self._concurrency_checks(args[0])

        # to preventing needing different functions per object,
        # this function simply handles cogs
        if hasattr(self, "cog"):
            return await self.func(self.cog, *args, **kwargs)
        return await self.func(*args, **kwargs)

    def is_on_cooldown(self, ctx) -> bool:
        """
        Checks whether the command is currently on cooldown.

        Works the same way as it does in d.py

        :param ctx: SlashContext
        :type ctx: .context.SlashContext

        :return: bool - indicating if the command is on cooldown.
        """
        if not self._buckets.valid:
            return False

        bucket = self._buckets.get_bucket(ctx.message)
        dt = ctx.message.edited_at or ctx.message.created_at
        current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        return bucket.get_tokens(current) == 0

    def reset_cooldown(self, ctx):
        """
        Resets the cooldown on this command.

        Works the same way as it does in d.py

        :param ctx: SlashContext
        :type ctx: .context.SlashContext
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(ctx.message)
            bucket.reset()

    def get_cooldown_retry_after(self, ctx) -> float:
        """
        Retrieves the amount of seconds before this command can be tried again.

        Works the same way as it does in d.py

        :param ctx: SlashContext
        :type ctx: .context.SlashContext

        :return: float - The amount of time left on this command's cooldown in seconds. If this is ``0.0`` then the command isn't on cooldown.
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(ctx.message)
            dt = ctx.message.edited_at or ctx.message.created_at
            current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            return bucket.get_retry_after(current)

        return 0.0

    def add_check(self, func):
        """
        Adds check to the command.

        :param func: Any callable. Coroutines are supported.
        """
        self.__commands_checks__.append(func)

    def remove_check(self, func):
        """
        Removes check to the command.

        .. note::
            If the function is not found at the command check, it will ignore.

        :param func: Any callable. Coroutines are supported.
        """
        with suppress(ValueError):
            self.__commands_checks__.remove(func)

    async def can_run(self, ctx) -> bool:
        """
        Whether the command can be run.

        :param ctx: SlashContext for the check running.
        :type ctx: .context.SlashContext
        :return: bool
        """
        res = [
            bool(x(ctx)) if not iscoroutinefunction(x) else bool(await x(ctx))
            for x in self.__commands_checks__
        ]
        return False not in res


class CommandObject(CallbackObject):
    """
    Slash command object of this extension.

    .. warning::
        Do not manually init this model.

    :ivar name: Name of the command.
    :ivar description: Description of the command.
    :ivar allowed_guild_ids: List of the allowed guild id.
    :ivar options: List of the option of the command. Used for `auto_register`.
    :ivar connector: Kwargs connector of the command.
    """

    def __init__(self, name, cmd, _type=1):  # Let's reuse old command formatting.
        super().__init__(cmd["func"])
        self.name = name.lower() if _type == 1 else name
        self.description = cmd["description"]
        self.allowed_guild_ids = cmd["guild_ids"] or []
        self.options = cmd["api_options"] or []
        self.connector = cmd["connector"] or {}
        self._type = _type


class BaseCommandObject(CommandObject):
    """
    BaseCommand object of this extension.

    .. note::
        This model inherits :class:`.model.CommandObject`, so this has every variables from that.

    .. warning::
        Do not manually init this model.

    :ivar has_subcommands: Indicates whether this base command has subcommands.
    :ivar default_permission: Indicates whether users should have permissions to run this command by default.
    :ivar permissions: Permissions to restrict use of this command.
    """

    def __init__(self, name, cmd, _type=1):  # Let's reuse old command formatting.
        super().__init__(name, cmd, _type)
        self.has_subcommands = cmd["has_subcommands"]
        self.default_permission = cmd["default_permission"]
        self.permissions = cmd["api_permissions"] or {}


class SubcommandObject(CommandObject):
    """
    Subcommand object of this extension.

    .. note::
        This model inherits :class:`.model.CommandObject`, so this has every variables from that.

    .. warning::
        Do not manually init this model.

    :ivar base: Name of the base slash command.
    :ivar subcommand_group: Name of the subcommand group. ``None`` if not exist.
    :ivar base_description: Description of the base command.
    :ivar subcommand_group_description: Description of the subcommand_group.
    """

    def __init__(self, sub, base, name, sub_group=None):
        super().__init__(name, sub)
        self.base = base.lower()
        self.subcommand_group = sub_group.lower() if sub_group else sub_group
        self.base_description = sub["base_desc"]
        self.subcommand_group_description = sub["sub_group_desc"]


class CogBaseCommandObject(BaseCommandObject):
    """
    Slash command object but for Cog.

    .. warning::
        Do not manually init this model.
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.cog = None  # Manually set this later.


class CogSubcommandObject(SubcommandObject):
    """
    Subcommand object but for Cog.

    .. warning::
        Do not manually init this model.
    """

    def __init__(self, base, cmd, sub_group, name, sub):
        super().__init__(sub, base, name, sub_group)
        self.base_command_data = cmd
        self.cog = None  # Manually set this later.


class ComponentCallbackObject(CallbackObject):
    """
    Internal component object. Inherits :class:`CallbackObject`, so it has all variables from it.

    .. warning::
        Do not manually init this model.

    :ivar message_ids: The message IDs registered to this callback.
    :ivar custom_ids: The component custom IDs registered to this callback.
    :ivar component_type: Type of the component. See `:class.utils.manage_components.ComponentsType`
    """

    def __init__(
        self,
        func,
        message_ids,
        custom_ids,
        component_type,
    ):
        if component_type not in (2, 3, None):
            raise error.IncorrectFormat(f"Invalid component type `{component_type}`")

        super().__init__(func)
        message_ids = set(message_ids)
        custom_ids = set(custom_ids)
        self.keys = {
            (message_id, custom_id) for message_id in message_ids for custom_id in custom_ids
        }

        self.component_type = component_type

    async def invoke(self, ctx):
        """
        Invokes the component callback.

        :param ctx: The :class:`.context.ComponentContext` for the interaction.
        """
        return await super().invoke(ctx)


class CogComponentCallbackObject(ComponentCallbackObject):
    """
    Component callback object but for Cog. Has all variables from :class:`ComponentCallbackObject`.

    .. warning::
        Do not manually init this model.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cog = None  # Manually set this later.


class SlashCommandOptionType(IntEnum):
    """
    Equivalent of `ApplicationCommandOptionType <https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoptiontype>`_  in the Discord API.
    """

    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    FLOAT = 10

    @classmethod
    def from_type(cls, t: type):
        """
        Get a specific SlashCommandOptionType from a type (or object).

        :param t: The type or object to get a SlashCommandOptionType for.
        :return: :class:`.model.SlashCommandOptionType` or ``None``
        """

        if issubclass(t, str):
            return cls.STRING
        if issubclass(t, bool):
            return cls.BOOLEAN
        # The check for bool MUST be above the check for integers as booleans subclass integers
        if issubclass(t, int):
            return cls.INTEGER
        if issubclass(t, discord.abc.User):
            return cls.USER
        if issubclass(t, discord.abc.GuildChannel):
            return cls.CHANNEL
        if issubclass(t, discord.abc.Role):
            return cls.ROLE
        if hasattr(typing, "_GenericAlias"):  # 3.7 onwards
            # Easier than imports
            if hasattr(t, "__origin__"):
                if t.__origin__ is typing.Union:
                    # proven in 3.7.8+, 3.8.6+, 3.9+ definitively
                    return cls.MENTIONABLE
        if not hasattr(typing, "_GenericAlias"):  # py 3.6
            if isinstance(t, typing._Union):  # noqa
                return cls.MENTIONABLE

        if issubclass(t, float):
            return cls.FLOAT


class SlashMessage(ComponentMessage):
    """discord.py's :class:`discord.Message` but overridden ``edit`` and ``delete`` to work for slash command."""

    def __init__(self, *, state, channel, data, _http: http.SlashCommandRequest, interaction_token):
        # Yes I know it isn't the best way but this makes implementation simple.
        super().__init__(state=state, channel=channel, data=data)
        self._http = _http
        self.__interaction_token = interaction_token

    async def _slash_edit(self, **fields):
        """
        An internal function
        """
        _resp = {}

        try:
            content = fields["content"]
        except KeyError:
            pass
        else:
            if content is not None:
                content = str(content)
            _resp["content"] = content

        try:
            components = fields["components"]
        except KeyError:
            pass
        else:
            if components is None:
                _resp["components"] = []
            else:
                _resp["components"] = components

        try:
            embeds = fields["embeds"]
        except KeyError:
            # Nope
            pass
        else:
            if not isinstance(embeds, list):
                raise error.IncorrectFormat("Provide a list of embeds.")
            if len(embeds) > 10:
                raise error.IncorrectFormat("Do not provide more than 10 embeds.")
            _resp["embeds"] = [e.to_dict() for e in embeds]

        try:
            embed = fields["embed"]
        except KeyError:
            pass
        else:
            if "embeds" in _resp:
                raise error.IncorrectFormat("You can't use both `embed` and `embeds`!")

            if embed is None:
                _resp["embeds"] = []
            else:
                _resp["embeds"] = [embed.to_dict()]

        file = fields.get("file")
        files = fields.get("files")

        if files is not None and file is not None:
            raise error.IncorrectFormat("You can't use both `file` and `files`!")
        if file:
            files = [file]

        allowed_mentions = fields.get("allowed_mentions")
        if allowed_mentions is not None:
            if self._state.allowed_mentions is not None:
                _resp["allowed_mentions"] = self._state.allowed_mentions.merge(
                    allowed_mentions
                ).to_dict()
            else:
                _resp["allowed_mentions"] = allowed_mentions.to_dict()
        else:
            if self._state.allowed_mentions is not None:
                _resp["allowed_mentions"] = self._state.allowed_mentions.to_dict()
            else:
                _resp["allowed_mentions"] = {}

        await self._http.edit(_resp, self.__interaction_token, self.id, files=files)

        delete_after = fields.get("delete_after")
        if delete_after:
            await self.delete(delay=delete_after)
        if files:
            [x.close() for x in files]

    async def edit(self, **fields):
        """Refer :meth:`discord.Message.edit`."""
        if "file" in fields or "files" in fields or "embeds" in fields:
            await self._slash_edit(**fields)
        else:
            try:
                await super().edit(**fields)
            except discord.Forbidden:
                await self._slash_edit(**fields)

    async def delete(self, *, delay=None):
        """Refer :meth:`discord.Message.delete`."""
        try:
            await super().delete(delay=delay)
        except discord.Forbidden:
            if not delay:
                return await self._http.delete(self.__interaction_token, self.id)

            async def wrap():
                with suppress(discord.HTTPException):
                    await asyncio.sleep(delay)
                    await self._http.delete(self.__interaction_token, self.id)

            self._state.loop.create_task(wrap())


class PermissionData:
    """
    Single slash permission data.

    :ivar id: User or role id, based on following type specfic.
    :ivar type: The ``SlashCommandPermissionsType`` type of this permission.
    :ivar permission: State of permission. ``True`` to allow, ``False`` to disallow.
    """

    def __init__(self, id, type, permission, **kwargs):
        self.id = id
        self.type = type
        self.permission = permission

    def __eq__(self, other):
        if isinstance(other, PermissionData):
            return (
                self.id == other.id
                and self.type == other.id
                and self.permission == other.permission
            )
        else:
            return False


class GuildPermissionsData:
    """
    Slash permissions data for a command in a guild.

    :ivar id: Command id, provided by discord.
    :ivar guild_id: Guild id that the permissions are in.
    :ivar permissions: List of permissions dict.
    """

    def __init__(self, id, guild_id, permissions, **kwargs):
        self.id = id
        self.guild_id = guild_id
        self.permissions = []
        if permissions:
            for permission in permissions:
                self.permissions.append(PermissionData(**permission))

    def __eq__(self, other):
        if isinstance(other, GuildPermissionsData):
            return (
                self.id == other.id
                and self.guild_id == other.guild_id
                and self.permissions == other.permissions
            )
        else:
            return False


class SlashCommandPermissionType(IntEnum):
    """
    Equivalent of `ApplicationCommandPermissionType <https://discord.com/developers/docs/interactions/slash-commands#applicationcommandpermissiontype>`_  in the Discord API.
    """

    ROLE = 1
    USER = 2

    @classmethod
    def from_type(cls, t: type):
        if issubclass(t, discord.abc.Role):
            return cls.ROLE
        if issubclass(t, discord.abc.User):
            return cls.USER


class ComponentType(IntEnum):
    actionrow = 1
    button = 2
    select = 3


class ButtonStyle(IntEnum):
    blue = 1
    blurple = 1
    gray = 2
    grey = 2
    green = 3
    red = 4
    URL = 5

    primary = 1
    secondary = 2
    success = 3
    danger = 4


class ContextMenuType(IntEnum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3

    # @classmethod
    # def from_type(cls, t: type):
    #     if isinstance(t, discord.Member) or issubclass(t, discord.abc.User):
    #         return cls.USER
    #     if issubclass(t, discord.abc.Messageable):
    #         return cls.MESSAGE
