from __future__ import annotations
from collections.abc import Awaitable, Iterable, Callable
from enum import Enum, IntEnum
import logging
import sys
import types
from typing import Annotated, Any, Literal, TypeVar, Union, get_args, get_origin
import discord
from discord.enums import SlashCommandOptionType, Enum as DiscordEnum
from discord.commands import AutocompleteContext
from discord.ext.commands import Converter
from discord.cog import Cog
import inspect


PY_310 = sys.version_info >= (3, 10)  # for UnionType
PY_311 = sys.version_info >= (3, 11)  # for StrEnum

PY_314 = sys.version_info >= (3, 14)
StrEnum = None
if PY_311:
    from enum import StrEnum  # type: ignore

    StrEnum = StrEnum

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
    discord.TextChannel
    | discord.VoiceChannel
    | discord.CategoryChannel
    | discord.ForumChannel
    | discord.StageChannel
)

ValidOptionType = (
    type[str]
    | type[bool]
    | type[int]
    | type[float]
    | type[discord.abc.GuildChannel]
    | type[ValidChannelType]
    | type[discord.Thread]
    | type[discord.Member]
    | type[discord.User]
    | type[discord.Attachment]
    | type[discord.Role]
    | type[discord.Role]
    | SlashCommandOptionType
    | type[Literal]
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

CLS_TO_CHANNEL_TYPE: dict[
    type[discord.abc.GuildChannel | discord.Thread], discord.ChannelType
] = {
    discord.TextChannel: discord.ChannelType.text,
    discord.VoiceChannel: discord.ChannelType.voice,
    discord.CategoryChannel: discord.ChannelType.category,
    discord.ForumChannel: discord.ChannelType.forum,
    discord.StageChannel: discord.ChannelType.stage_voice,
    discord.Thread: discord.ChannelType.public_thread,
}
CHANNEL_TYPE_TO_CLS: dict[
    discord.ChannelType, type[discord.abc.GuildChannel | discord.Thread]
] = {v: k for k, v in CLS_TO_CHANNEL_TYPE.items()}
OPTION_TYPE_TO_SLASH_OPTION_TYPE: dict[ValidOptionType, SlashCommandOptionType] = {
    str: SlashCommandOptionType.string,
    bool: SlashCommandOptionType.boolean,
    int: SlashCommandOptionType.integer,
    float: SlashCommandOptionType.number,
    discord.abc.GuildChannel: SlashCommandOptionType.channel,
    discord.Thread: SlashCommandOptionType.channel,
    discord.Member: SlashCommandOptionType.user,
    discord.User: SlashCommandOptionType.user,
    discord.Attachment: SlashCommandOptionType.attachment,
    discord.Role: SlashCommandOptionType.role,
}
OPTION_TYPE_TO_DEFAULT_TYPES: dict[SlashCommandOptionType, tuple[type[Any], ...]] = {
    SlashCommandOptionType.string: (str,),
    SlashCommandOptionType.boolean: (bool,),
    SlashCommandOptionType.integer: (int,),
    SlashCommandOptionType.number: (float,),
    SlashCommandOptionType.channel: (type(None),),  # Channel IDs are passed as strings
    SlashCommandOptionType.user: (type(None),),  # User IDs are passed as strings
    SlashCommandOptionType.attachment: (
        type(None),
    ),  # Attachment IDs are passed as strings
    SlashCommandOptionType.role: (type(None),),  # Role IDs are passed as strings
}

_log = logging.getLogger(__name__)


class OptionChoice:
    def __init__(
        self,
        name: str,
        value: str | int | float | None = None,
        name_localizations: dict[str, str] = discord.MISSING,
    ) -> None:
        self.name: str = name
        self.value: str | int | float = value if value is not None else name
        self.name_localizations: dict[str, str] = name_localizations

    def to_dict(self) -> dict[str, str | int | float]:
        base = {"name": self.name, "value": self.value}
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
        description: str | None = None,
        required: bool = True,
        default: int | str | float | None = None,
        choices: ValidChoicesType | None = None,
        name_localizations: dict[str, str] | None = None,
        description_localizations: dict[str, str] | None = None,
        channel_types: list[discord.ChannelType] | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        autocomplete: AutocompleteFunction | None = None,
    ) -> None:
        self.name: str | None = name
        self._param_name: str | None = None

        self.description: str | None = description

        self._param_type: ValidOptionType = input_type
        self._api_type: SlashCommandOptionType | None = None
        self.converter: Converter[Any] | None = None
        self._handle_type(input_type)

        self.required: bool = required if default is None else False
        self.default: int | str | float | None = default

        self.choices: list[OptionChoice] = self._handle_choices(choices)
        self.name_localizations: dict[str, str] = name_localizations or {}
        self.description_localizations: dict[str, str] = description_localizations or {}
        self.channel_types: list[discord.ChannelType] = channel_types or []
        self.min_value: int | float | None = min_value
        self.max_value: int | float | None = max_value
        self.min_length: int | None = min_length
        self.max_length: int | None = max_length
        self.autocomplete: AutocompleteFunction | None = autocomplete

    def _validate_max_value(self) -> None:
        if self._param_type not in (int, float, None):
            raise ValueError(
                f"max_value is only applicable for int and float parameter types, not {self._param_type}."
            )

    def _handle_type(self, param_type: ValidOptionType) -> None:
        if isinstance(param_type, SlashCommandOptionType):
            self._api_type = param_type
            return

        if (
            isinstance(param_type, type)
            and (
                issubclass(param_type, (Enum, DiscordEnum))  # type: ignore
            )
            and not self.choices
        ):
            self._parse_choices_from_enum(param_type)
            return

        api_type = OPTION_TYPE_TO_SLASH_OPTION_TYPE.get(param_type)
        if not api_type:
            if isinstance(param_type, type) and issubclass(param_type, Converter):  # type: ignore
                self.converter = param_type()
                api_type = SlashCommandOptionType.string
            elif isinstance(param_type, Converter):
                self.converter = param_type
                api_type = SlashCommandOptionType.string
            else:
                raise TypeError(f"Unsupported option type: {param_type}")

        self._api_type = api_type
        self._param_type = param_type

    def _handle_choices(self, choices: ValidChoicesType | None) -> list[OptionChoice]:
        if not choices:
            return []

        final_choices: list[OptionChoice] = []

        if isinstance(choices, type) and (issubclass(choices, (Enum, DiscordEnum))):
            return self._parse_choices_from_enum(choices)

        if isinstance(choices, Iterable):
            for choice in choices:
                if isinstance(choice, OptionChoice):
                    final_choices.append(choice)
                elif isinstance(choice, (str, int, float)):
                    final_choices.append(OptionChoice(name=str(choice), value=choice))
                else:
                    raise TypeError(
                        f"Invalid choice type: {type(choice)}. Choices must be OptionChoice instances or str/int/float."
                    )
        else:
            raise TypeError(
                f"Invalid choices type: {type(choices)}. Choices must be an iterable of OptionChoice or str/int/float, or an Enum class."
            )

        return final_choices

    def _parse_choices_from_enum(self, enum_cls: type[Enum]) -> list[OptionChoice]:
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
            self._param_type = int
        elif StrEnum and issubclass(enum_cls, StrEnum):
            self._api_type = SlashCommandOptionType.string
            self._param_type = str
        else:
            first_member_type: type = type(next(iter(enum_cls)).value)
            if not isinstance(first_member_type, (str, int, float)):
                raise TypeError(
                    f"Enum choices must have values of type str, int, or float. Found {type(first_member_type)} in {enum_cls}."
                )

            self._api_type = SlashCommandOptionType.from_datatype(first_member_type)
            self._param_type = first_member_type  # type: ignore

        return self._handle_choices(enum_cls)

    def to_dict(self) -> dict[str, Any]:
        if not self._api_type:
            raise ValueError("Option type has not been set.")

        base = {
            "type": self._api_type.value,
            "name": self.name,
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


class InspectedAnnotation:
    def __init__(
        self,
        name: str,
        annotation: ValidOptionType = str,
        is_optional: bool = False,
        is_union: bool = False,
        is_literal: bool = False,
        args: list[type] | None = None,
        default: type | None = None,
    ) -> None:
        self.name = name
        self.annotation = annotation
        self.is_optional = is_optional
        self.is_union = is_union
        self.is_literal = is_literal
        self.args = get_args(annotation) if args is None else args
        self.default = default

        self.channel_types: list[discord.ChannelType] = []

        self.inner_type: ValidOptionType = annotation
        self.api_type = SlashCommandOptionType.string

    def check(self) -> None:
        if isinstance(self.inner_type, SlashCommandOptionType):
            return

        if (
            isinstance(self.inner_type, type)
            and issubclass(self.inner_type, Converter)  # type: ignore
            or isinstance(self.inner_type, Converter)
        ):
            return

        api_type = OPTION_TYPE_TO_SLASH_OPTION_TYPE.get(self.inner_type)  # type: ignore
        if api_type:
            self.api_type = api_type

        if self.is_literal:
            if all(isinstance(arg, str) for arg in self.args):
                self.api_type = SlashCommandOptionType.string
            elif all(isinstance(arg, int) for arg in self.args):
                self.api_type = SlashCommandOptionType.integer
            elif all(isinstance(arg, float) for arg in self.args):
                self.api_type = SlashCommandOptionType.number
            else:
                raise TypeError(
                    f"Unsupported literal choice types in annotation for parameter {self.name}: {self.args}. "
                    f"All literal choices must be of the same type and must be str, int, or float."
                )
        elif self.is_union and self.args:
            if any(c in CLS_TO_CHANNEL_TYPE for c in self.args if isinstance(c, type)):
                self.api_type = SlashCommandOptionType.channel
                self.channel_types = [CLS_TO_CHANNEL_TYPE[c] for c in self.args]
            elif any(issubclass(c, (discord.Member, discord.User)) for c in self.args):
                self.api_type = SlashCommandOptionType.user
        elif self.is_union and not self.is_optional:
            raise TypeError(
                f"Unsupported Union annotation for parameter {self.name}: {self.annotation}. "
                f"Union types are not supported unless they are Optional or a Union of channel types or "
                f"a Union of Member/User types."
            )
        else:
            raise TypeError(
                f"Unsupported annotation type for parameter {self.name}: {self.annotation}. "
                f"Type must be a valid option type, a Converter, or a SlashCommandOptionType."
            )

        valid_default_types = OPTION_TYPE_TO_DEFAULT_TYPES.get(
            self.api_type, (str, int, float, type(None))
        )

        if self.default is not None and not isinstance(
            self.default, valid_default_types
        ):
            raise ValueError(
                f"Invalid default value for parameter {self.name}: {self.default}. "
                f"Default value must be of type {valid_default_types}."
            )


def inspect_annotations(func: Callable[..., Any]) -> dict[str, InspectedAnnotation]:
    signature = inspect.signature(
        func,
        globals=globals(),
        locals=locals(),
    )

    res: dict[str, InspectedAnnotation] = {}
    parameters = signature.parameters
    for param_name, param in parameters.items():
        obj = InspectedAnnotation(name=param_name, default=param.default)
        annotation = param.annotation
        if annotation is param.empty:
            continue

        origin = get_origin(annotation)
        obj.annotation = annotation

        if origin is Annotated:
            obj.inner_type = obj.args[0]
        elif origin is Union:
            obj.is_optional = type(None) in obj.args
            obj.args = [arg for arg in obj.args if arg is not type(None)]
            if len(obj.args) == 1 and obj.is_optional:
                obj.inner_type = obj.args[0]
        elif origin is Literal:
            obj.is_literal = True

        obj.check()
        res[param_name] = obj

    return res


# --- TEST CASES FOR inspect_annotations ---
from typing import Optional


class MyEnum(Enum):
    A = 1
    B = 2


def test_optional(a: Optional[int] = None):
    pass


def test_union(b: Union[int, str]):
    pass


def test_literal(c: Literal["foo", "bar"]):
    pass


def test_enum(d: MyEnum):
    pass


def test_converter(e: Converter):
    pass


def test_channel(f: discord.TextChannel):
    pass


def test_thread(g: discord.Thread):
    pass


def test_member_user(h: Union[discord.Member, discord.User]):
    pass


test_functions = [
    test_optional,
    test_union,
    test_literal,
    test_enum,
    test_converter,
    test_channel,
    test_thread,
    test_member_user,
]

for func in test_functions:
    print(f"\nTesting: {func.__name__}")
    inspected = inspect_annotations(func)
    for name, annotation in inspected.items():
        print(f"Parameter: {name}")
        print(f"  Annotation: {annotation.annotation}")
        print(f"  Is Optional: {annotation.is_optional}")
        print(f"  Is Union: {annotation.is_union}")
        print(f"  Is Literal: {annotation.is_literal}")
        print(f"  Args: {annotation.args}")
        print(f"  Default: {annotation.default}")
        print(f"  API Type: {annotation.api_type}")
        print(f"  Channel Types: {annotation.channel_types}")


# --- MULTI-PARAMETER TEST CASES ---
def test_multi_1(a: int, b: Optional[str] = None, c: Literal[1, 2, 3] = 1):
    pass


def test_multi_2(
    x: Union[discord.TextChannel, discord.VoiceChannel], y: MyEnum, z: Converter
):
    pass


def test_multi_3(
    p: discord.Member, q: Union[discord.Member, discord.User], r: float = 3.14
):
    pass


multi_param_functions = [
    test_multi_1,
    test_multi_2,
    test_multi_3,
]

for func in multi_param_functions:
    print(f"\nTesting: {func.__name__}")
    inspected = inspect_annotations(func)
    for name, annotation in inspected.items():
        print(f"Parameter: {name}")
        print(f"  Annotation: {annotation.annotation}")
        print(f"  Is Optional: {annotation.is_optional}")
        print(f"  Is Union: {annotation.is_union}")
        print(f"  Is Literal: {annotation.is_literal}")
        print(f"  Args: {annotation.args}")
        print(f"  Default: {annotation.default}")
        print(f"  API Type: {annotation.api_type}")
        print(f"  Channel Types: {annotation.channel_types}")
