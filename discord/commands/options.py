from __future__ import annotations

import ast
import importlib
import inspect
import logging
import sys
import types
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Iterable
from enum import Enum, IntEnum
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from ..abc import GuildChannel
from ..channel import (
    CategoryChannel,
    DMChannel,
    ForumChannel,
    MediaChannel,
    StageChannel,
    TextChannel,
    Thread,
    VoiceChannel,
)
from ..enums import ChannelType
from ..enums import Enum as DiscordEnum
from ..enums import SlashCommandOptionType
from ..member import Member
from ..message import Attachment
from ..role import Role
from ..user import User
from ..utils import (
    MISSING,
    basic_autocomplete,
    deprecated,
    normalise_optional_params,
    resolve_annotation,
)
from .context import AutocompleteContext

if TYPE_CHECKING:
    from ..cog import Cog


PY_310 = sys.version_info >= (3, 10)  # for UnionType
PY_311 = sys.version_info >= (3, 11)  # for StrEnum

PY_314 = sys.version_info >= (3, 14)
StrEnum = None
if PY_311:
    from enum import StrEnum  # type: ignore

    StrEnum = StrEnum

if TYPE_CHECKING:
    from discord.ext.commands import Converter

    AutocompleteReturnType = (
        Iterable["OptionChoice"] | Iterable[str] | Iterable[int] | Iterable[float]
    )

    T = TypeVar("T", bound=AutocompleteReturnType)
    MaybeAwaitable = T | Awaitable[T]
    AutocompleteFunction = (
        Callable[[AutocompleteContext], MaybeAwaitable[AutocompleteReturnType]]
        | Callable[[Cog, AutocompleteContext], MaybeAwaitable[AutocompleteReturnType]]
        | Callable[
            [AutocompleteContext, Any],
            MaybeAwaitable[AutocompleteReturnType],
        ]
        | Callable[
            [Cog, AutocompleteContext, Any],
            MaybeAwaitable[AutocompleteReturnType],
        ]
    )

    ValidChannelType = (
        TextChannel | VoiceChannel | CategoryChannel | ForumChannel | StageChannel
    )

    ValidOptionType = (
        type[str]
        | type[bool]
        | type[int]
        | type[float]
        | type[GuildChannel]
        | type[ValidChannelType]
        | type[Thread]
        | type[Member]
        | type[User]
        | type[Attachment]
        | type[Role]
        | SlashCommandOptionType
        | type[Literal]  # pyright: ignore[reportMissingTypeArgument]
        | Converter[Any]
        | type[Converter[Any]]
        | type[Enum]
        | type[DiscordEnum]
    )

    ValidChoicesType = (
        Iterable["OptionChoice"]
        | Iterable[str]
        | Iterable[int]
        | Iterable[float]
        | type[Enum]
        | type[DiscordEnum]
    )

CLS_TO_CHANNEL_TYPE: dict[type[GuildChannel | DMChannel | Thread], ChannelType] = {
    TextChannel: ChannelType.text,
    VoiceChannel: ChannelType.voice,
    StageChannel: ChannelType.stage_voice,
    CategoryChannel: ChannelType.category,
    Thread: ChannelType.public_thread,
    ForumChannel: ChannelType.forum,
    MediaChannel: ChannelType.media,
    DMChannel: ChannelType.private,
}
CHANNEL_TYPE_TO_CLS: dict[ChannelType, type[GuildChannel | DMChannel | Thread]] = {
    v: k for k, v in CLS_TO_CHANNEL_TYPE.items()
}
OPTION_TYPE_TO_SLASH_OPTION_TYPE: dict[ValidOptionType, SlashCommandOptionType] = {
    str: SlashCommandOptionType.string,
    bool: SlashCommandOptionType.boolean,
    int: SlashCommandOptionType.integer,
    float: SlashCommandOptionType.number,
    GuildChannel: SlashCommandOptionType.channel,
    Thread: SlashCommandOptionType.channel,
    Member: SlashCommandOptionType.user,
    User: SlashCommandOptionType.user,
    Attachment: SlashCommandOptionType.attachment,
    Role: SlashCommandOptionType.role,
}


_log = logging.getLogger(__name__)


def _is_type_checking_statement(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        return node.id == "TYPE_CHECKING"
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return node.value.id == "typing" and node.attr == "TYPE_CHECKING"
    return False


def _get_type_checking_locals(func: Callable[..., Any]) -> dict[str, Any]:
    module = inspect.getmodule(func)
    module_file = getattr(module, "__file__", None)
    module_name = getattr(module, "__name__", None)
    if module is None or module_file is None or module_name is None:
        return {}

    try:
        with open(module_file, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=module_file)
    except Exception:
        return {}

    resolved: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, ast.If) or not _is_type_checking_statement(node.test):
            continue

        for stmt in node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    try:
                        imported = importlib.import_module(alias.name)
                    except Exception:
                        continue
                    resolved[alias.asname or alias.name.split(".")[-1]] = imported
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module is None:
                    continue
                try:
                    imported_module = importlib.import_module(
                        stmt.module, package=module_name
                    )
                except Exception:
                    continue
                for alias in stmt.names:
                    if alias.name == "*":
                        continue
                    if not hasattr(imported_module, alias.name):
                        continue
                    resolved[alias.asname or alias.name] = getattr(
                        imported_module, alias.name
                    )

    return resolved


class OptionChoice:
    def __init__(
        self,
        name: str,
        value: str | int | float | None = None,
        name_localizations: dict[str, str] = MISSING,
    ) -> None:
        self.name: str = name
        self.value: str | int | float = value if value is not None else name
        self.name_localizations: dict[str, str] = name_localizations

        if not isinstance(
            self.value, (str, int, float)
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(
                f"Option choice value must be of type str, int, or float, not {type(self.value)}."
            )

        self._api_type: SlashCommandOptionType = SlashCommandOptionType.from_datatype(  # type: ignore
            type(self.value)
        )  # type: ignore

    def to_dict(self) -> dict[str, str | int | float | dict[str, str]]:
        base: dict[str, str | int | float | dict[str, str]] = {
            "name": self.name,
            "value": self.value,
        }
        if self.name_localizations:
            base["name_localizations"] = self.name_localizations

        return base


class Option:
    def __init__(
        self,
        input_type: ValidOptionType = str,
        /,
        *,
        name: str | None = None,
        parameter_name: str | None = None,
        name_localizations: dict[str, str] | None = None,
        description: str | None = None,
        description_localizations: dict[str, str] | None = None,
        required: bool = True,
        default: int | str | float | None = None,
        choices: ValidChoicesType | None = None,
        channel_types: list[ChannelType] | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        autocomplete: AutocompleteFunction | None = None,
    ) -> None:

        self.name: str | None = name
        self._param_name: str | None = parameter_name or name

        self.description: str | None = description

        self._param_type: ValidOptionType = input_type
        self._api_type: SlashCommandOptionType | None = None
        self.converter: Converter[Any] | None = None

        self.required: bool = required if default is None else False
        self.default: int | str | float | None = default

        self.name_localizations: dict[str, str] = name_localizations or {}
        self.description_localizations: dict[str, str] = description_localizations or {}
        self.channel_types: list[ChannelType] = channel_types or []
        self.min_value: int | float | None = min_value
        self.max_value: int | float | None = max_value
        self.min_length: int | None = min_length
        self.max_length: int | None = max_length

        self._autocomplete: AutocompleteFunction | None = None
        self.autocomplete = autocomplete

        self.choices: list[OptionChoice] = self._handle_choices(choices)

    @property
    def autocomplete(self) -> AutocompleteFunction | None:
        """
        The autocomplete handler for the option. Accepts a callable (sync or async)
        that takes a single required argument of :class:`AutocompleteContext` or two arguments
        of :class:`discord.Cog` (being the command's cog) and :class:`AutocompleteContext`.
        The callable must return an iterable of :class:`str` or :class:`OptionChoice`.
        Alternatively, :func:`discord.utils.basic_autocomplete` may be used in place of the callable.

        Returns
        -------
        Optional[AutocompleteFunction]

        .. versionchanged:: 2.7

        .. note::
            Does not validate the input value against the autocomplete results.
        """
        return self._autocomplete

    @autocomplete.setter
    def autocomplete(self, value: AutocompleteFunction | None) -> None:
        self._autocomplete = value
        # this is done here so it does not have to be computed every time the autocomplete is invoked
        if self._autocomplete is not None:
            self._autocomplete_is_instance_method = (
                sum(
                    1
                    for param in inspect.signature(
                        self._autocomplete
                    ).parameters.values()
                    if param.default == param.empty
                    and param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)
                )
                == 2
            )

    def _copy_from(self, other: Option) -> None:
        self.name = other.name
        self._param_name = other._param_name
        self.description = other.description
        self._param_type = other._param_type
        self._api_type = other._api_type
        self.converter = other.converter
        self.required = other.required
        self.default = other.default
        self.choices = other.choices.copy()
        self.name_localizations = other.name_localizations.copy()
        self.description_localizations = other.description_localizations.copy()
        self.channel_types = other.channel_types.copy()
        self.min_value = other.min_value
        self.max_value = other.max_value
        self.min_length = other.min_length
        self.max_length = other.max_length
        self.autocomplete = other.autocomplete

    def _validate_minmax_value(self) -> None:
        if self._api_type not in (
            SlashCommandOptionType.integer,
            SlashCommandOptionType.number,
        ):
            raise ValueError(
                f"max_value is only applicable for int and float parameter types, not {self._param_type}."
            )

    def _validate_minmax_length(self, max_length: int | None = None) -> None:
        if self._api_type is not SlashCommandOptionType.string:
            raise ValueError(
                f"min_length and max_length are only applicable for string option types, not {self._api_type}."
            )

        if max_length is not None and (max_length < 1 or max_length > 6000):
            raise ValueError("max_length must be between 1 and 6000.")

    def _handle_type(self, param_type: ValidOptionType | None = None) -> None:
        param_type = param_type or self._param_type
        if isinstance(param_type, SlashCommandOptionType):
            self._api_type = param_type
            return

        from discord.ext.commands.converter import CONVERTER_MAPPING, Converter

        try:
            self._api_type = OPTION_TYPE_TO_SLASH_OPTION_TYPE[param_type]  # type: ignore
        except KeyError:
            try:
                converter_cls = CONVERTER_MAPPING[param_type]  # type: ignore
                self.converter = converter_cls()  # type: ignore
                self._api_type = OPTION_TYPE_TO_SLASH_OPTION_TYPE[converter_cls]  # type: ignore
            except KeyError:
                pass

        origin = get_origin(param_type)
        args = get_args(param_type)

        if inspect.isclass(param_type):
            print(
                "Handling class type:",
                param_type,
                type(param_type),
                get_origin(param_type),
                get_args(param_type),
                param_type.__name__,
            )
            if issubclass(param_type, (Enum, DiscordEnum)):  # type: ignore
                self._parse_choices_from_enum(param_type)
            elif issubclass(param_type, Converter):  # type: ignore
                self.converter = param_type()  # type: ignore
        elif isinstance(
            param_type, Converter
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            self.converter = param_type
        elif origin is Annotated:
            self._handle_type(args[0])
            return
        elif (
            get_origin(param_type) is Union
        ):  # pyright: ignore[reportUnnecessaryComparison]
            union_args = get_args(param_type)
            non_none_args = normalise_optional_params(union_args)[:-1]
            if len(non_none_args) == 1:
                self._handle_type(non_none_args[0])
                return
            if any(
                c in CLS_TO_CHANNEL_TYPE for c in non_none_args if isinstance(c, type)
            ):
                self._api_type = SlashCommandOptionType.channel
                self.channel_types = [CLS_TO_CHANNEL_TYPE[c] for c in non_none_args]
                return
            if any(
                isinstance(c, type) and issubclass(c, (Member, User))
                for c in non_none_args
            ):
                self._api_type = SlashCommandOptionType.user
                return
        elif (
            get_origin(param_type) is Literal
        ):  # pyright: ignore[reportUnnecessaryComparison]
            literal_args = get_args(param_type)
            if all(isinstance(arg, str) for arg in literal_args):
                self._api_type = SlashCommandOptionType.string
            elif all(isinstance(arg, int) for arg in literal_args):
                self._api_type = SlashCommandOptionType.integer
            elif all(isinstance(arg, float) for arg in literal_args):
                self._api_type = SlashCommandOptionType.number
            else:
                raise TypeError(
                    f"Unsupported literal choice types in annotation: {literal_args}. "
                    f"All literal choices must be of the same type and must be str, int, or float."
                )

            self._handle_choices(literal_args)
            return

        if self.min_length is not None or self.max_length is not None:
            self._validate_minmax_length(self.max_length)

        if self.min_value is not None or self.max_value is not None:
            self._validate_minmax_value()

    def _handle_choices(self, choices: ValidChoicesType | None) -> list[OptionChoice]:
        if not choices:
            return []

        final_choices: list[OptionChoice] = []

        if isinstance(choices, type) and (
            issubclass(choices, (Enum, DiscordEnum))
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            return self._parse_choices_from_enum(choices)

        if isinstance(
            choices, Iterable
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            for choice in choices:
                if isinstance(choice, OptionChoice):
                    final_choices.append(choice)
                elif isinstance(
                    choice, (str, int, float)
                ):  # pyright: ignore[reportUnnecessaryIsInstance]
                    final_choices.append(OptionChoice(name=str(choice), value=choice))
                else:
                    raise TypeError(
                        f"Invalid choice type: {type(choice)}. Choices must be OptionChoice instances or str/int/float."
                    )
        else:
            raise TypeError(
                f"Invalid choices type: {type(choices)}. Choices must be an iterable of OptionChoice or str/int/float, or an Enum class."
            )

        print(
            "Final parsed choices:",
            final_choices,
            len(final_choices),
            self.autocomplete,
        )
        if len(final_choices) > 25 and self.autocomplete is None:
            self.choices = []
            self.autocomplete = basic_autocomplete(final_choices)
            _log.info(
                "Option '%s' has more than 25 choices, so choices were cleared and basic autocomplete was set up automatically.",
                self.name,
            )

        return final_choices

    def _parse_choices_from_enum(self, enum_cls: type[Enum]) -> list[OptionChoice]:
        print("Parsing choices from Enum:", enum_cls, type(enum_cls))
        if self.description is None and enum_cls.__doc__ is not None:
            description = inspect.cleandoc(enum_cls.__doc__)
            if len(description) > 100:
                description = description[:97] + "..."
                _log.warning(
                    "Option %s's description was truncated due to Enum %s's docstring exceeding 100 characters.",
                    self.name,
                    self._api_type,
                )

            self.description = description

        if issubclass(enum_cls, IntEnum):
            self._api_type = SlashCommandOptionType.integer
        elif StrEnum and issubclass(enum_cls, StrEnum):
            self._api_type = SlashCommandOptionType.string
        else:
            first_member_type: type = next(iter(enum_cls)).value
            print("First member type of Enum:", first_member_type)
            if not isinstance(first_member_type, (str, int, float)):
                raise TypeError(
                    f"For parameter {self._param_name}: Enum choices must have values of type str, int, or float. Found {type(first_member_type)} in {enum_cls}."
                )

            self._api_type = SlashCommandOptionType.from_datatype(  # type: ignore
                type(first_member_type)
            )

        return self._handle_choices(
            [OptionChoice(name=member.name, value=member.value) for member in enum_cls]
        )

    def to_dict(self) -> dict[str, Any]:
        if not self._api_type:
            raise ValueError("Option type has not been set.")

        base: dict[str, Any] = {
            "type": self._api_type.value,
            "name": self._param_name,
            "description": self.description,
            "required": self.required,
        }
        if self.choices:
            base["choices"] = [choice.to_dict() for choice in self.choices]
        if self.name_localizations:
            base["name_localizations"] = self.name_localizations
        if self.description_localizations:
            base["description_localizations"] = self.description_localizations
        if self.channel_types:
            base["channel_types"] = [ct.value for ct in self.channel_types]
        if self.min_value is not None:
            base["min_value"] = self.min_value
        if self.max_value is not None:
            base["max_value"] = self.max_value
        if self.min_length is not None:
            base["min_length"] = self.min_length
        if self.max_length is not None:
            base["max_length"] = self.max_length

        return base


ValidThreadType = Literal[
    "public",
    "private",
    "news",
    ChannelType.news_thread,
    ChannelType.private_thread,
    ChannelType.public_thread,
]


@deprecated(
    "ThreadOption is deprecated and will be removed in a future version. Please use Option with the appropriate channel_types instead.",
    since="2.9",
)
class ThreadOption(Option):
    """Represents a class that can be passed as the ``input_type`` for an :class:`Option` class.

    .. versionadded:: 2.0

    Parameters
    ----------
    thread_type: Literal["public", "private", "news", :attr:`ChannelType.news_thread`, :attr:`ChannelType.private_thread`, :attr:`ChannelType.public_thread`]
        The thread type to expect for this options input.
    """

    def __init__(self, thread_type: ValidThreadType) -> types.NoneType:
        type_map = {
            "public": ChannelType.public_thread,
            "private": ChannelType.private_thread,
            "news": ChannelType.news_thread,
        }
        return super().__init__(
            Thread,
            channel_types=[type_map.get(thread_type, thread_type)],  # type: ignore
        )


def _get_options(
    func: Callable[..., Any], *, cog: type[Cog] | None = None
) -> dict[str, Option]:
    signature = inspect.signature(
        func, globals=func.__globals__, locals=func.__globals__
    )

    res: dict[str, Option] = {}
    parameters = OrderedDict(signature.parameters)

    existing_options: dict[str, Option] = getattr(func, "__options__", {}).copy()
    print(f"Existing options for function '{func.__name__}': {existing_options}")

    # skip 'self' and 'context' parameters if they exist
    param_items = list(parameters.items())
    if cog is not None:
        if param_items and param_items[0][0] != "self":
            _log.warning(
                f"First parameter of method '{func.__name__}' should be 'self' when it's in a cog, but got '{param_items[0][0]!r}'."
            )
        skip_count = 2
    else:
        skip_count = 2 if param_items and param_items[0][0] == "self" else 1

    skip_count = min(skip_count, len(param_items))

    for param_name, param in param_items[skip_count:]:
        existing = existing_options.pop(param_name, None)
        option = Option(
            name=param_name,
            parameter_name=param_name,
            description=inspect.cleandoc(param.__doc__) if param.__doc__ else None,
        )

        annotation_is_option = False
        if param.annotation is not param.empty:
            try:
                annotation = resolve_annotation(
                    param.annotation, func.__globals__, func.__globals__, {}
                )
            except NameError:
                # Only attempt TYPE_CHECKING import recovery for forward refs.
                if not isinstance(param.annotation, str):
                    raise
                eval_locals = func.__globals__.copy()

                eval_locals.update(_get_type_checking_locals(func))
                annotation = resolve_annotation(
                    param.annotation, func.__globals__, eval_locals, {}
                )
            if isinstance(annotation, Option):
                annotation_is_option = True
                option._copy_from(annotation)  # pyright: ignore[reportPrivateUsage]
                if option.name is None:
                    option.name = param_name
                if option._param_name is None:  # pyright: ignore[reportPrivateUsage]
                    option._param_name = (
                        param_name  # pyright: ignore[reportPrivateUsage]
                    )
            else:
                option._param_type = annotation  # pyright: ignore[reportPrivateUsage]

        if existing:
            option._copy_from(existing)  # pyright: ignore[reportPrivateUsage]

        if param.default is not param.empty:
            option.default = param.default
            option.required = False

        if param.annotation is param.empty and not annotation_is_option:
            continue

        try:
            option._handle_type()  # pyright: ignore[reportPrivateUsage]
        except Exception as e:
            raise TypeError(
                f"Error processing parameter '{param_name}' of function '{func.__name__}': {e}"
            ) from e

    if existing_options:
        for param_name in existing_options:
            raise ValueError(
                f"Option '{existing_options[param_name].name}' specified for parameter "
                f"'{param_name}' in function '{func.__name__}' was not found in the function. "
            )

    return res


CallableT = TypeVar("CallableT", bound=Callable[..., Any])


def option(
    name: str,
    input_type: ValidOptionType = str,
    /,
    *,
    parameter_name: str | None = None,
    name_localizations: dict[str, str] | None = None,
    description: str | None = MISSING,
    description_localizations: dict[str, str] | None = None,
    required: bool = True,
    default: int | str | float | None = None,
    choices: ValidChoicesType | None = None,
    channel_types: list[ChannelType] | None = None,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    autocomplete: AutocompleteFunction | None = None,
) -> Callable[[CallableT], CallableT]:
    """Decorator to specify metadata for a command option.

    You may use multiple instances of this decorator to
    specify metadata for multiple parameters in the same command.

    Parameters
    ----------
    name: :class:`str`
        The name of the option as it will appear in Discord. This is required.
    input_type: ValidOptionType
        The type of the option. This can be inferred from type annotations, but may be specified
        here for convenience. Defaults to :class:`str` if not specified or inferred.
    parameter_name: Optional[:class:`str`]
        The name of the parameter this option corresponds to. If not specified, it will be assumed
        to be the same as the option name. This is only necessary to specify if the parameter name
        is different from the option name.
    name_localizations: Optional[Dict[:class:`str`, :class:`str`]]
        A mapping of locale codes to localized option names.
    description: Optional[:class:`str`]
        The description of the option as it will appear in Discord. If not specified, it will be
        inferred from the parameter's docstring if available.
    description_localizations: Optional[Dict[:class:`str`, :class:`str`]]
        A mapping of locale codes to localized option descriptions.
    required: :class:`bool`
        Whether the option is required. Defaults to ``True``. If a default value is provided,
        this will be set to ``False``.
    default: Optional[Union[:class:`int`, :class:`str`, :class:`float`]]
        The default value for the option. If provided, the option will not be required.
    choices: Optional[
        Union[
            Iterable[:class:`OptionChoice`],
            Iterable[:class:`str`],
            Iterable[:class:`int`],
            Iterable[:class:`float`],
            Type[Enum],
            Type[DiscordEnum]
        ]
    ]
        A list of choices for the option. Each choice can be an instance of :class:`OptionChoice`
        or a raw value (str, int, or float). If an Enum class is provided, choices will be generated
        from the Enum members. If more than 25 choices are provided, they will be cleared and basic
        autocomplete will be set up automatically.
    channel_types: Optional[List[:class:`ChannelType`]]
        A list of channel types to limit a channel option to. Only applicable if the option type is a
        channel or a union of channel types.
    min_value: Optional[Union[:class:`int`, :class:`float`]]
        The minimum value for the option. Only applicable for int and float option types.
    max_value: Optional[Union[:class:`int`, :class:`float`]]
        The maximum value for the option. Only applicable for int and float option types.
    min_length: Optional[:class:`int`]
        The minimum length for the option. Only applicable for string option types.
    max_length: Optional[:class:`int`]
        The maximum length for the option. Only applicable for string option types.
    autocomplete: Optional[AutocompleteFunction]
        An autocomplete handler for the option. Accepts a callable (sync or async)
        that takes a single required argument of :class:`AutocompleteContext` or two arguments
        of :class:`discord.Cog` (being the command's cog) and :class:`AutocompleteContext`.
        The callable must return an iterable of :class:`str` or :class:`OptionChoice`. Alternatively,
        :func:`discord.utils.basic_autocomplete` may be used in place of the callable.
    """

    def inner(func: CallableT) -> CallableT:
        opt = Option(
            input_type,
            name=name,
            parameter_name=parameter_name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            required=required,
            default=default,
            choices=choices,
            channel_types=channel_types,
            min_value=min_value,
            max_value=max_value,
            min_length=min_length,
            max_length=max_length,
            autocomplete=autocomplete,
        )
        try:
            func.__options__[name] = opt  # type: ignore
        except AttributeError:
            func.__options__ = {name: opt}  # type: ignore

        return func

    return inner


def options(**options: Option) -> Callable[[CallableT], CallableT]:
    """Decorator to specify multiple options for a command at once.

    You may not use both this decorator and the :func:`option` decorator
    to specify metadata for the same parameter. This will raise a
    :exc:`ValueError`.

    Parameters
    ----------
    **options
        Keyword arguments where the key is the parameter name and
        the value is an instance of :class:`Option` containing the
        option metadata for that parameter.

    Example
    -------

    .. code-block:: python3

        @commands.slash_command(name="opt_multiple")
        @options(
            target=discord.Option(description="The target member or user",),
            hidden=discord.Option(description="Whether the option should be hidden"),
        )
        async def opt_multiple(
            self,
            ctx: discord.ApplicationContext,
            target: Union[discord.Member, discord.User],
            hidden: bool = False,
        ) -> None:
             await ctx.respond(f"target={target.mention}")
    """

    def inner(func: CallableT) -> CallableT:
        if not all(
            isinstance(opt, Option) for opt in options.values()
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(
                "All values passed to @options must be instances of Option."
            )

        existing_options: dict[str, Option] = getattr(func, "__options__", {}).copy()
        if not existing_options:
            existing_options = options
        else:
            for name, opt in options.items():
                if name in existing_options:
                    raise ValueError(
                        f"Duplicate option metadata for parameter '{name}' in function '{func.__name__}'. "
                        "Please don't use both @option and @options decorators to specify metadata for the same parameter."
                    )
                existing_options[name] = opt

        func.__options__ = existing_options  # type: ignore
        return func

    return inner
