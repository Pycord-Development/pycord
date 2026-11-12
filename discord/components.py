"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
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

from __future__ import annotations

from abc import ABC
from collections.abc import Iterator
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Literal,
    Protocol,
    TypeVar,
    cast,
    overload,
    runtime_checkable,
)

from typing_extensions import Self

from .asset import AssetMixin
from .colour import Colour
from .enums import (
    ButtonStyle,
    ChannelType,
    ComponentType,
    InputTextStyle,
    SelectDefaultValueType,
    SeparatorSpacingSize,
    try_enum,
)
from .flags import AttachmentFlags
from .partial_emoji import PartialEmoji, _EmojiTag
from .utils import MISSING, find, get_slots

if TYPE_CHECKING:
    from . import abc
    from .emoji import AppEmoji, GuildEmoji
    from .state import ConnectionState
    from .types.components import ActionRow as ActionRowPayload
    from .types.components import ButtonComponent as ButtonComponentPayload
    from .types.components import ChannelSelectMenu as ChannelSelectMenuPayload
    from .types.components import CheckboxComponent as CheckboxComponentPayload
    from .types.components import (
        CheckboxGroupComponent as CheckboxGroupComponentPayload,
    )
    from .types.components import CheckboxGroupOption as CheckboxGroupOptionPayload
    from .types.components import Component as ComponentPayload
    from .types.components import ContainerComponent as ContainerComponentPayload
    from .types.components import FileComponent as FileComponentPayload
    from .types.components import FileUploadComponent as FileUploadComponentPayload
    from .types.components import InputText as InputTextComponentPayload
    from .types.components import LabelComponent as LabelComponentPayload
    from .types.components import MediaGalleryComponent as MediaGalleryComponentPayload
    from .types.components import MediaGalleryItem as MediaGalleryItemPayload
    from .types.components import MentionableSelectMenu as MentionableSelectMenuPayload
    from .types.components import RadioGroupComponent as RadioGroupComponentPayload
    from .types.components import RadioGroupOption as RadioGroupOptionPayload
    from .types.components import RoleSelectMenu as RoleSelectMenuPayload
    from .types.components import SectionComponent as SectionComponentPayload
    from .types.components import SelectDefaultValue as SelectDefaultValuePayload
    from .types.components import SelectMenu as SelectMenuPayload
    from .types.components import SelectOption as SelectOptionPayload
    from .types.components import SeparatorComponent as SeparatorComponentPayload
    from .types.components import StringSelectMenu as StringSelectMenuPayload
    from .types.components import TextDisplayComponent as TextDisplayComponentPayload
    from .types.components import ThumbnailComponent as ThumbnailComponentPayload
    from .types.components import UnfurledMediaItem as UnfurledMediaItemPayload
    from .types.components import UserSelectMenu as UserSelectMenuPayload

__all__ = (
    "ActionRow",
    "Button",
    "Checkbox",
    "CheckboxGroup",
    "CheckboxGroupOption",
    "Component",
    "Container",
    "FileComponent",
    "FileUpload",
    "InputText",
    "Label",
    "MediaGallery",
    "MediaGalleryItem",
    "RadioGroup",
    "RadioGroupOption",
    "Section",
    "SelectDefaultValue",
    "SelectMenu",
    "SelectOption",
    "Separator",
    "TextDisplay",
    "Thumbnail",
    "UnfurledMediaItem",
)

T = TypeVar("T", bound="ComponentType")


@runtime_checkable
class _HasSubComponents(Protocol):
    def walk_components(self) -> Iterator[Component[Any]]: ...
    def get_component(self, id: str | int) -> Component[Any] | None: ...


class Component(ABC, Generic[T]):
    """Represents a Discord Bot UI Kit Component.

    The components supported by Discord in messages are as follows:

    - :class:`ActionRow`
    - :class:`Button`
    - :class:`SelectMenu`
    - :class:`Section`
    - :class:`TextDisplay`
    - :class:`Thumbnail`
    - :class:`MediaGallery`
    - :class:`FileComponent`
    - :class:`Separator`
    - :class:`Container`

    This class is abstract and cannot be instantiated.

    .. versionadded:: 2.0

    Attributes
    ----------
    type: :class:`ComponentType`
        The type of component.
    id: :class:`int`
        The component's ID. If not provided by the user, it is set sequentially by Discord.
        The ID `0` is treated as if no ID was provided.
    """

    __slots__: tuple[str, ...] = ("id", "type")

    __repr_info__: ClassVar[tuple[str, ...]]
    id: int | None
    type: T
    versions: tuple[int, ...]

    def __repr__(self) -> str:
        attrs = " ".join(f"{key}={getattr(self, key)!r}" for key in self.__repr_info__)
        return f"<{self.__class__.__name__} {attrs}>"

    @classmethod
    def _raw_construct(cls, **kwargs: Any) -> Self:
        self: Self = cls.__new__(cls)
        for slot in get_slots(cls):
            try:
                value = kwargs[slot]
            except KeyError:
                setattr(self, slot, None)
            else:
                setattr(self, slot, value)
        return self

    def to_dict(self) -> ComponentPayload:
        raise NotImplementedError

    def is_v2(self) -> bool:
        """Whether this component was introduced in Components V2."""
        return bool(self.versions) and 1 not in self.versions


class ActionRow(Component[Literal[ComponentType.action_row]], _HasSubComponents):
    """Represents a Discord Bot UI Kit Action Row.

    This is a component that holds up to 5 children components in a row.

    This inherits from :class:`Component`.

    .. versionadded:: 2.0

    Attributes
    ----------
    type: :class:`ComponentType`
        The type of component.
    children: List[:class:`Component`]
        The children components that this holds, if any.
    """

    __slots__: tuple[str, ...] = ("children",)

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (1, 2)

    def __init__(self, data: ActionRowPayload):
        self.type = ComponentType.action_row
        self.id: int | None = data.get("id")
        self.children: list[Button | InputText | SelectMenu] = [
            _component_factory(d) for d in data.get("components", [])
        ]

    @property
    def width(self):
        """Returns the sum of the item's widths."""
        t = 0
        for item in self.children:
            t += 1 if item.type is ComponentType.button else 5
        return t

    def to_dict(self) -> ActionRowPayload:
        payload: ActionRowPayload = {
            "type": self.type.value,
            "components": [child.to_dict() for child in self.children],
        }
        if self.id is not None:
            payload["id"] = self.id
        return payload

    def walk_components(self) -> Iterator[Button | InputText | SelectMenu]:
        yield from self.children

    @property
    def components(self) -> list[Button | InputText | SelectMenu]:
        return self.children

    def get_component(self, id: str | int) -> Button | InputText | SelectMenu | None:
        """Get a component from this action row. Roughly equivalent to `utils.get(row.children, ...)`.
        If an ``int`` is provided, the component will be retrieved by ``id``, otherwise by ``custom_id``.

        Parameters
        ----------
        id: :class:`str` | :class:`int`
            The custom_id or id of the component to get.

        Returns
        -------
        :class:`Component` | :obj:`None`
            The component with the matching ``id`` or ``custom_id`` if it exists.
        """
        if not id:
            return None
        attr = "id" if isinstance(id, int) else "custom_id"
        return find(lambda i: getattr(i, attr, None) == id, self.children)

    @classmethod
    def with_components(
        cls, *components: Button | InputText | SelectMenu, id: int | None = None
    ):
        return cls._raw_construct(
            type=ComponentType.action_row, id=id, children=[c for c in components]
        )


class Button(Component[Literal[ComponentType.button]]):
    """Represents a button from the Discord Bot UI Kit.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.Button` instead.

    .. versionadded:: 2.0

    Attributes
    ----------
    style: :class:`.ButtonStyle`
        The style of the button.
    custom_id: :class:`str` | :obj:`None`
        The ID of the button that gets received during an interaction.
        If this button is for a URL, it does not have a custom ID.
    url: :class:`str` | :obj:`None`
        The URL this button sends you to.
    disabled: :class:`bool`
        Whether the button is disabled or not.
    label: :class:`str` | :obj:`None`
        The label of the button, if any.
    emoji: :class:`PartialEmoji` | :obj:`None`
        The emoji of the button, if available.
    sku_id: :class:`int` | :obj:`None`
        The ID of the SKU this button refers to.
    """

    __slots__: tuple[str, ...] = (
        "custom_id",
        "disabled",
        "emoji",
        "label",
        "sku_id",
        "style",
        "url",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (1, 2)

    def __init__(self, data: ButtonComponentPayload):
        self.type = ComponentType.button
        self.id: int | None = data.get("id")
        self.style: ButtonStyle = try_enum(ButtonStyle, data["style"])
        self.label: str | None = data.get("label")
        self.emoji: PartialEmoji | None
        if e := data.get("emoji"):
            self.emoji = PartialEmoji.from_dict(e)
        else:
            self.emoji = None
        self.custom_id: str | None = data.get("custom_id")
        self.sku_id: int | None = (
            int(sku_id) if (sku_id := data.get("sku_id")) else None
        )
        self.url: str | None = data.get("url")
        self.disabled: bool = data.get("disabled", False)

    def to_dict(self) -> ButtonComponentPayload:
        payload: ButtonComponentPayload = {
            "type": self.type.value,
            "style": self.style.value,
            "disabled": self.disabled,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.custom_id:
            payload["custom_id"] = self.custom_id
        if self.label:
            payload["label"] = self.label
        if self.url:
            payload["url"] = self.url
        if self.emoji:
            payload["emoji"] = self.emoji.to_dict()
        if self.sku_id:
            payload["sku_id"] = self.sku_id
        return payload


SelectMenuTypes = Literal[
    ComponentType.string_select,
    ComponentType.role_select,
    ComponentType.user_select,
    ComponentType.channel_select,
    ComponentType.mentionable_select,
]


class SelectMenu(Component[SelectMenuTypes]):
    """Represents a select menu from the Discord Bot UI Kit.

    A select menu is functionally the same as a dropdown, however
    on mobile it renders a bit differently.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.Select` instead.

    .. versionadded:: 2.0

    .. versionchanged:: 2.3

        Added support for :attr:`ComponentType.user_select`, :attr:`ComponentType.role_select`,
        :attr:`ComponentType.mentionable_select`, and :attr:`ComponentType.channel_select`.

    .. versionchanged:: 2.7

        Added the :attr:`required` attribute for use in modals.

    Attributes
    ----------
    type: :class:`ComponentType`
        The select menu's type.
    custom_id: :class:`str`
        The ID of the select menu that gets received during an interaction.
    placeholder: :class:`str` | :obj:`None`
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 0 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    options: List[:class:`SelectOption`]
        A list of options that can be selected in this menu.
        Will be an empty list for all component types
        except for :attr:`ComponentType.string_select`.
    channel_types: List[:class:`ChannelType`]
        A list of channel types that can be selected.
        Will be an empty list for all component types
        except for :attr:`ComponentType.channel_select`.
    disabled: :class:`bool`
        Whether the select is disabled or not. Not usable in modals. Defaults to ``False``.
    required: :class:`bool`
        Whether the select is required or not. Only useable in modals. Defaults to ``True``.
    """

    __slots__: tuple[str, ...] = (
        "channel_types",
        "custom_id",
        "default_values",
        "disabled",
        "max_values",
        "min_values",
        "options",
        "placeholder",
        "required",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (1, 2)

    def __init__(self, data: SelectMenuPayload):
        self.type = cast(SelectMenuTypes, try_enum(ComponentType, data["type"]))
        self.id: int | None = data.get("id")
        self.custom_id: str = data["custom_id"]
        self.placeholder: str | None = data.get("placeholder")
        self.min_values: int = data.get("min_values", 1)
        self.max_values: int = data.get("max_values", 1)
        self.disabled: bool = data.get("disabled", False)
        self.required: bool | None = data.get("required", True)
        self.options: list[SelectOption] = [
            SelectOption.from_dict(option) for option in data.get("options", [])
        ]
        self.channel_types: list[ChannelType] = [
            try_enum(ChannelType, ct) for ct in data.get("channel_types", [])
        ]
        self.default_values: list[SelectDefaultValue] = SelectDefaultValue._from_data(
            data.get("default_values")
        )

    def to_dict(self) -> SelectMenuPayload:
        payload: Any = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "disabled": self.disabled,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.placeholder:
            payload["placeholder"] = self.placeholder
        if self.required is not None:
            payload["required"] = self.required
        if self.type is ComponentType.string_select:
            payload["options"] = [op.to_dict() for op in self.options]
        if self.type is ComponentType.channel_select and self.channel_types:
            payload["channel_types"] = [ct.value for ct in self.channel_types]
        if self.type is not ComponentType.string_select:
            payload["default_values"] = [dv.to_dict() for dv in self.default_values]

        return cast("SelectMenuPayload", payload)


class InputText(Component[Literal[ComponentType.input_text]]):
    """Represents an Input Text field from the Discord Bot UI Kit.
    This inherits from :class:`Component`.

    Attributes
    ----------
    style: :class:`.InputTextStyle`
        The style of the input text field.
    custom_id: :class:`str`
        The custom ID of the input text field that gets received during an interaction.
    label: :class:`str`
        The label for the input text field.
    placeholder: :class:`str` | :obj:`None`
        The placeholder text that is shown if nothing is selected, if any.
    min_length: :class:`int` | :obj:`None`
        The minimum number of characters that must be entered
        Defaults to 0
    max_length: :class:`int` | :obj:`None`
        The maximum number of characters that can be entered
    required: :class:`bool`
        Whether the input text field is required or not. Defaults to `True`.
    value: :class:`str` | :obj:`None`
        The value that has been entered in the input text field.
    id: :class:`int` | :obj:`None`
        The input text's ID.
    """

    __slots__: tuple[str, ...] = (
        "custom_id",
        "id",
        "label",
        "max_length",
        "min_length",
        "placeholder",
        "required",
        "style",
        "type",
        "value",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (1, 2)

    def __init__(self, data: InputTextComponentPayload):
        self.type = ComponentType.input_text
        self.id: int | None = data.get("id")
        self.custom_id = data["custom_id"]
        self.style: InputTextStyle = try_enum(InputTextStyle, data["style"])
        self.min_length: int | None = data.get("min_length", None)
        self.max_length: int | None = data.get("max_length", None)
        self.required: bool | None = data.get("required", True)
        self.value: str | None = data.get("value", None)
        self.placeholder: str | None = data.get("placeholder", None)
        self.label: str | None = data.get("label", None)

    def to_dict(self) -> InputTextComponentPayload:
        payload: InputTextComponentPayload = {
            "type": self.type.value,
            "style": self.style.value,
            "custom_id": self.custom_id,
        }
        if self.id:
            payload["id"] = self.id
        if self.min_length:
            payload["min_length"] = self.min_length
        if self.max_length:
            payload["max_length"] = self.max_length
        if self.required is not None:
            payload["required"] = self.required
        if self.value:
            payload["value"] = self.value
        if self.placeholder:
            payload["placeholder"] = self.placeholder
        if self.label:
            payload["label"] = self.label
        return payload


class SelectDefaultValue:
    r"""Represents a :class:`discord.SelectMenu`\s default value.

    This is only applicable to selects of type other than :attr:`ComponentType.string_select`.

    .. versionadded:: 2.7

    Parameters
    ----------
    object: :class:`abc.Snowflake`
        The model type this select default value is based of.

        Below, is a table defining the model instance type and the default value type it will be mapped:

        +-----------------------------------+--------------------------------------------------------------------------+
        | Model Type                        | Default Value Type                                                       |
        +-----------------------------------+--------------------------------------------------------------------------+
        | :class:`discord.User`             | :attr:`discord.SelectDefaultValueType.user`                              |
        +-----------------------------------+--------------------------------------------------------------------------+
        | :class:`discord.Member`           | :attr:`discord.SelectDefaultValueType.user`                              |
        +-----------------------------------+--------------------------------------------------------------------------+
        | :class:`discord.Role`             | :attr:`discord.SelectDefaultValueType.role`                              |
        +-----------------------------------+--------------------------------------------------------------------------+
        | :class:`discord.abc.GuildChannel` | :attr:`discord.SelectDefaultValueType.channel`                           |
        +-----------------------------------+--------------------------------------------------------------------------+
        | :class:`discord.Object`           | depending on :attr:`discord.Object.type`, it will be mapped to any above |
        +-----------------------------------+--------------------------------------------------------------------------+

        If you pass a model that is not defined in the table, ``TypeError`` will be raised.

        .. note::

            The :class:`discord.abc.GuildChannel` protocol includes :class:`discord.TextChannel`, :class:`discord.VoiceChannel`, :class:`discord.StageChannel`,
            :class:`discord.ForumChannel`, :class:`discord.Thread`, :class:`discord.MediaChannel`. This list is not exhaustive, and is bound to change
            based of the new channel types Discord adds.

    id: :class:`int`
        The ID of the default value. This cannot be used with ``object``.
    type: :class:`SelectDefaultValueType`
        The default value type. This cannot be used with ``object``.

    Raises
    ------
    TypeError
        You did not provide any parameter, you provided all parameters, or you provided ``id`` but not ``type``.
    """

    __slots__ = ("id", "type")

    @overload
    def __init__(
        self,
        object: abc.Snowflake,
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        /,
        *,
        id: int,
        type: SelectDefaultValueType,
    ) -> None: ...

    def __init__(
        self,
        object: abc.Snowflake = MISSING,
        /,
        *,
        id: int = MISSING,
        type: SelectDefaultValueType = MISSING,
    ) -> None:
        self.id: int = id
        self.type: SelectDefaultValueType = type
        if object is not MISSING:
            if any(p is not MISSING for p in (id, type)):
                raise TypeError("you cannot pass id or type when passing object")
            _ = self._handle_model(object, inst=self)
        elif id is not MISSING and type is not MISSING:
            self.id = id
            self.type = type
        else:
            raise TypeError("you must provide an object model, or an id and type")

    def __repr__(self) -> str:
        return f"<SelectDefaultValue id={self.id} type={self.type}>"

    @classmethod
    def _from_data(
        cls, default_values: list[SelectDefaultValuePayload] | None
    ) -> list[SelectDefaultValue]:
        if not default_values:
            return []
        return [
            cls(id=int(d["id"]), type=try_enum(SelectDefaultValueType, d["type"]))
            for d in default_values
        ]

    @classmethod
    def _handle_model(
        cls,
        model: abc.Snowflake,
        select_type: ComponentType | None = None,
        inst: SelectDefaultValue | None = None,
    ) -> SelectDefaultValue:
        # preventing >circular imports<
        from discord import Member, Object, Role, User, abc
        from discord.user import _UserTag

        instances_mapping: dict[
            type, tuple[tuple[ComponentType, ...], SelectDefaultValueType]
        ] = {
            Role: (
                (ComponentType.role_select, ComponentType.mentionable_select),
                SelectDefaultValueType.role,
            ),
            User: (
                (ComponentType.user_select, ComponentType.mentionable_select),
                SelectDefaultValueType.user,
            ),
            Member: (
                (ComponentType.user_select, ComponentType.mentionable_select),
                SelectDefaultValueType.user,
            ),
            _UserTag: (
                (ComponentType.user_select, ComponentType.mentionable_select),
                SelectDefaultValueType.user,
            ),
            abc.GuildChannel: (
                (ComponentType.channel_select,),
                SelectDefaultValueType.channel,
            ),
        }

        obj_id = model.id
        obj_type = model.__class__

        if isinstance(model, Object):
            obj_type = model.type

        sel_types = None
        def_type = None

        for typ, (st, dt) in instances_mapping.items():
            if issubclass(obj_type, typ):
                sel_types = st
                def_type = dt
                break

        if sel_types is None or def_type is None:
            raise TypeError(
                f"{obj_type.__name__} is not a valid instance for a select default value"
            )

        # we can't actually check select types when not in a select context
        if select_type is not None and select_type not in sel_types:
            raise TypeError(
                f"{model.__class__.__name__} objects can not be set as a default value for {select_type.value} selects",
            )

        if inst is None:
            return cls(id=obj_id, type=def_type)
        else:
            inst.id = obj_id
            inst.type = def_type
            return inst

    def to_dict(self) -> SelectDefaultValuePayload:
        return {
            "id": self.id,
            "type": self.type.value,
        }


class SelectOption:
    """Represents a :class:`discord.SelectMenu`'s option.

    These can be created by users.

    .. versionadded:: 2.0

    Attributes
    ----------
    label: :class:`str`
        The label of the option. This is displayed to users.
        Can only be up to 100 characters.
    value: :class:`str`
        The value of the option. This is not displayed to users.
        If not provided when constructed then it defaults to the
        label. Can only be up to 100 characters.
    description: :class:`str` | :obj:`None`
        An additional description of the option, if any.
        Can only be up to 100 characters.
    default: :class:`bool`
        Whether this option is selected by default.
    """

    __slots__: tuple[str, ...] = (
        "_emoji",
        "default",
        "description",
        "label",
        "value",
    )

    def __init__(
        self,
        *,
        label: str,
        value: str = MISSING,
        description: str | None = None,
        emoji: str | GuildEmoji | AppEmoji | PartialEmoji | None = None,
        default: bool = False,
    ) -> None:
        if len(label) > 100:
            raise ValueError("label must be 100 characters or fewer")

        if value is not MISSING and len(value) > 100:
            raise ValueError("value must be 100 characters or fewer")

        if description is not None and len(description) > 100:
            raise ValueError("description must be 100 characters or fewer")

        self.label = label
        self.value = label if value is MISSING else value
        self.description = description
        self._emoji = None
        self.emoji = emoji
        self.default = default

    def __repr__(self) -> str:
        return (
            "<SelectOption"
            f" label={self.label!r} value={self.value!r} description={self.description!r} "
            f"emoji={self.emoji!r} default={self.default!r}>"
        )

    def __str__(self) -> str:
        base = f"{self.emoji} {self.label}" if self.emoji else self.label
        if self.description:
            return f"{base}\n{self.description}"
        return base

    @property
    def emoji(self) -> str | GuildEmoji | AppEmoji | PartialEmoji | None:
        """The emoji of the option, if available."""
        return self._emoji

    @staticmethod
    def _coerce_emoji(value: object) -> PartialEmoji:
        if isinstance(value, PartialEmoji):
            return value
        if isinstance(value, str):
            return PartialEmoji.from_str(value)
        if isinstance(value, _EmojiTag):
            return value._to_partial()
        raise TypeError(
            f"expected emoji to be str, GuildEmoji, AppEmoji, or PartialEmoji, not {type(value).__name__}"
        )

    @emoji.setter
    def emoji(self, value: str | GuildEmoji | AppEmoji | PartialEmoji | None) -> None:
        self._emoji = None if value is None else self._coerce_emoji(value)

    @classmethod
    def from_dict(cls, data: SelectOptionPayload) -> SelectOption:
        if e := data.get("emoji"):
            emoji = PartialEmoji.from_dict(e)
        else:
            emoji = None

        return cls(
            label=data["label"],
            value=data["value"],
            description=data.get("description"),
            emoji=emoji,
            default=data.get("default", False),
        )

    def to_dict(self) -> SelectOptionPayload:
        payload: SelectOptionPayload = {
            "label": self.label,
            "value": self.value,
            "default": self.default,
        }

        if self.emoji:
            payload["emoji"] = self._coerce_emoji(self.emoji).to_dict()

        if self.description:
            payload["description"] = self.description

        return payload


class Section(Component[Literal[ComponentType.section]], _HasSubComponents):
    """Represents a Section from Components V2.

    This is a component that groups other components together with an additional component to the right as the accessory.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.Section` instead.

    .. versionadded:: 2.7

    Attributes
    ----------
    components: List[:class:`Component`]
        The components contained in this section. Currently supports :class:`TextDisplay`.
    accessory: :class:`Component`
        The accessory attached to this Section. Currently supports :class:`Button` and :class:`Thumbnail`.
    """

    __slots__: tuple[str, ...] = ("accessory", "components")

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(
        self, data: SectionComponentPayload, state: ConnectionState | None = None
    ):
        self.type = ComponentType.section
        self.id: int | None = data.get("id")
        self.components = [
            _component_factory(d, state=state) for d in data.get("components", [])
        ]
        self.accessory = _component_factory(data["accessory"], state=state)

    def to_dict(self) -> SectionComponentPayload:
        payload: SectionComponentPayload = {
            "type": self.type.value,
            "components": [c.to_dict() for c in self.components],
            "accessory": self.accessory.to_dict(),
        }
        if self.id is not None:
            payload["id"] = self.id
        return payload

    def walk_components(self) -> Iterator[TextDisplay | Button | Thumbnail]:
        yield from self.components
        if self.accessory:
            yield self.accessory

    def get_component(self, id: str | int) -> TextDisplay | Button | Thumbnail | None:
        """Get a component from this section. Roughly equivalent to `utils.get(section.walk_components(), ...)`.
        If an ``int`` is provided, the component will be retrieved by ``id``, otherwise by ``custom_id``.

        Parameters
        ----------
        id: :class:`str` | :class:`int`
            The custom_id or id of the component to get.

        Returns
        -------
        :class:`Component` | :obj:`None`
            The component with the matching ``id`` or ``custom_id`` if it exists.
        """
        if not id:
            return None
        attr = "id" if isinstance(id, int) else "custom_id"
        if self.accessory and id == getattr(self.accessory, attr, None):
            return self.accessory
        component = find(lambda i: getattr(i, attr, None) == id, self.components)
        return component


class TextDisplay(Component[Literal[ComponentType.text_display]]):
    """Represents a Text Display from Components V2.

    This is a component that displays text.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.TextDisplay` instead.

    .. versionadded:: 2.7

    Attributes
    ----------
    content: :class:`str`
        The component's text content.
    """

    __slots__: tuple[str, ...] = ("content",)

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(self, data: TextDisplayComponentPayload):
        self.type = ComponentType.text_display
        self.id: int | None = data.get("id")
        self.content: str = data.get("content")

    def to_dict(self) -> TextDisplayComponentPayload:
        payload: TextDisplayComponentPayload = {
            "type": self.type.value,
            "content": self.content,
        }
        if self.id is not None:
            payload["id"] = self.id
        return payload


class UnfurledMediaItem(AssetMixin):
    """Represents an Unfurled Media Item used in Components V2.

    This is used as an underlying component for other media-based components such as :class:`Thumbnail`, :class:`FileComponent`, and :class:`MediaGalleryItem`.

    .. versionadded:: 2.7

    Attributes
    ----------
    url: :class:`str`
        The URL of this media item. This can either be an arbitrary URL or an ``attachment://`` URL to work with local files.
    """

    def __init__(self, url: str):
        self._state = None
        self._url: str = url
        self._static_url: str | None = (
            url if url and url.startswith("attachment://") else None
        )
        self.proxy_url: str | None = None
        self.height: int | None = None
        self.width: int | None = None
        self.content_type: str | None = None
        self.flags: AttachmentFlags | None = None
        self.attachment_id: int | None = None

    def __repr__(self) -> str:
        return (
            f"<UnfurledMediaItem url={self.url!r} attachment_id={self.attachment_id}>"
        )

    def __str__(self) -> str:
        return self.url or self.__repr__()

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str) -> None:  # pyright: ignore[reportIncompatibleVariableOverride]
        self._url = value
        self._static_url = (
            value if value and value.startswith("attachment://") else None
        )

    @classmethod
    def from_dict(
        cls, data: UnfurledMediaItemPayload, state: ConnectionState | None = None
    ) -> UnfurledMediaItem:
        r = cls(data.get("url"))
        r.proxy_url = data.get("proxy_url")
        r.height = data.get("height")
        r.width = data.get("width")
        r.content_type = data.get("content_type")
        r.flags = AttachmentFlags._from_value(data.get("flags", 0))
        r.attachment_id = int(aid) if (aid := data.get("attachment_id")) else None
        r._state = state
        return r

    def to_dict(self) -> UnfurledMediaItemPayload:
        return {"url": self._static_url or self.url}


class Thumbnail(Component[Literal[ComponentType.thumbnail]]):
    """Represents a Thumbnail from Components V2.

    This is a component that displays media, such as images and videos.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.Thumbnail` instead.

    .. versionadded:: 2.7

    Attributes
    ----------
    media: :class:`UnfurledMediaItem`
        The component's underlying media object.
    description: :class:`str` | :obj:`None`
        The thumbnail's description, up to 1024 characters.
    spoiler: :class:`bool` | :obj:`None`
        Whether the thumbnail has the spoiler overlay.
    """

    __slots__: tuple[str, ...] = (
        "description",
        "media",
        "spoiler",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(
        self, data: ThumbnailComponentPayload, state: ConnectionState | None = None
    ):
        self.type = ComponentType.thumbnail
        self.id: int | None = data.get("id")
        self.media: UnfurledMediaItem = (
            umi := data.get("media")
        ) and UnfurledMediaItem.from_dict(umi, state=state)
        self.description: str | None = data.get("description")
        self.spoiler: bool | None = data.get("spoiler")

    @property
    def url(self) -> str:
        """Returns the URL of this thumbnail's underlying media item."""
        return self.media.url

    def to_dict(self) -> ThumbnailComponentPayload:
        payload: ThumbnailComponentPayload = {
            "type": self.type.value,
            "media": self.media.to_dict(),
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.description:
            payload["description"] = self.description
        if self.spoiler is not None:
            payload["spoiler"] = self.spoiler
        return payload


class MediaGalleryItem:
    """Represents an item used in the :class:`MediaGallery` component.

    This is used as an underlying component for other media-based components such as :class:`Thumbnail`, :class:`FileComponent`, and :class:`MediaGalleryItem`.

    .. versionadded:: 2.7

    Parameters
    ----------
    url: :class:`str`
        The URL of this gallery item. This can either be an arbitrary URL or an ``attachment://`` URL to work with local files.
    description: :class:`str`
        The gallery item's description, up to 1024 characters.
    spoiler: :class:`bool`
        Whether the gallery item is a spoiler.

    Attributes
    ----------
    media: :class:`UnfurledMediaItem`
        The media for this gallery item.
    description: :class:`str`
        The gallery item's description.
    spoiler: :class:`bool`
        Whether the gallery item is a spoiler.
    """

    def __init__(
        self, url: str, *, description: str | None = None, spoiler: bool = False
    ):
        self._state = None
        self.media: UnfurledMediaItem = UnfurledMediaItem(url)
        self.description: str | None = description
        self.spoiler: bool | None = spoiler

    @property
    def url(self) -> str:
        return self.media.url

    def is_dispatchable(self) -> bool:
        return False

    @classmethod
    def from_dict(
        cls, data: MediaGalleryItemPayload, state: ConnectionState | None = None
    ) -> MediaGalleryItem:
        media = (umi := data.get("media")) and UnfurledMediaItem.from_dict(
            umi, state=state
        )
        description = data.get("description")
        spoiler = data.get("spoiler", False)

        r = cls(
            url=media.url,
            description=description,
            spoiler=spoiler,
        )
        r._state = state
        r.media = media
        return r

    def to_dict(self) -> MediaGalleryItemPayload:
        payload: MediaGalleryItemPayload = {"media": self.media.to_dict()}
        if self.description:
            payload["description"] = self.description
        if self.spoiler is not None:
            payload["spoiler"] = self.spoiler
        return payload


class MediaGallery(Component[Literal[ComponentType.media_gallery]]):
    """Represents a Media Gallery from Components V2.

    This is a component that displays up to 10 different :class:`MediaGalleryItem` objects.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.MediaGallery` instead.

    .. versionadded:: 2.7

    Attributes
    ----------
    items: List[:class:`MediaGalleryItem`]
        The media this gallery contains.
    """

    __slots__: tuple[str, ...] = ("items",)

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(
        self, data: MediaGalleryComponentPayload, state: ConnectionState | None = None
    ):
        self.type = ComponentType.media_gallery
        self.id: int | None = data.get("id")
        self.items: list[MediaGalleryItem] = [
            MediaGalleryItem.from_dict(d, state=state) for d in data.get("items", [])
        ]

    def to_dict(self) -> MediaGalleryComponentPayload:
        payload: MediaGalleryComponentPayload = {
            "type": self.type.value,
            "items": [i.to_dict() for i in self.items],
        }
        if self.id is not None:
            payload["id"] = self.id
        return payload


class FileComponent(Component[Literal[ComponentType.file]]):
    """Represents a File from Components V2.

    This component displays a downloadable file in a message.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.File` instead.

    .. versionadded:: 2.7

    Attributes
    ----------
    file: :class:`UnfurledMediaItem`
        The file's media item.
    name: :class:`str` | :obj:`None`
        The file's name.
    size: :class:`int` | :obj:`None`
        The file's size in bytes.
    spoiler: :class:`bool` | :obj:`None`
        Whether the file has the spoiler overlay.
    """

    __slots__: tuple[str, ...] = (
        "file",
        "name",
        "size",
        "spoiler",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(
        self, data: FileComponentPayload, state: ConnectionState | None = None
    ):
        self.type = ComponentType.file
        self.id: int | None = data.get("id")
        self.name: str | None = data.get("name")
        self.size: int | None = data.get("size")
        self.file: UnfurledMediaItem = UnfurledMediaItem.from_dict(
            data.get("file", {}), state=state
        )
        self.spoiler: bool | None = data.get("spoiler")

    def to_dict(self) -> FileComponentPayload:
        payload: FileComponentPayload = {
            "type": self.type.value,
            "file": self.file.to_dict(),
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.spoiler is not None:
            payload["spoiler"] = self.spoiler
        return payload


class Separator(Component[Literal[ComponentType.separator]]):
    """Represents a Separator from Components V2.

    This is a component that visually separates components.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.Separator` instead.

    .. versionadded:: 2.7

    Attributes
    ----------
    divider: :class:`bool`
        Whether the separator will show a horizontal line in addition to vertical spacing.
    spacing: :class:`SeparatorSpacingSize`
        The separator's spacing size.
    """

    __slots__: tuple[str, ...] = (
        "divider",
        "spacing",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(self, data: SeparatorComponentPayload):
        self.type = ComponentType.separator
        self.id: int | None = data.get("id")
        self.divider: bool = data.get("divider", True)
        self.spacing: SeparatorSpacingSize = try_enum(
            SeparatorSpacingSize, data.get("spacing", 1)
        )

    def to_dict(self) -> SeparatorComponentPayload:
        payload: SeparatorComponentPayload = {
            "type": self.type.value,
            "divider": self.divider,
            "spacing": self.spacing.value,
        }
        if self.id is not None:
            payload["id"] = self.id
        return payload


ContainerTypes = Literal[
    ComponentType.action_row,
    ComponentType.text_display,
    ComponentType.section,
    ComponentType.media_gallery,
    ComponentType.separator,
    ComponentType.file,
]


class Container(Component[Literal[ComponentType.container]], _HasSubComponents):
    """Represents a Container from Components V2.

    This is a component that contains different :class:`Component` objects.
    It may only contain:

    - :class:`ActionRow`
    - :class:`TextDisplay`
    - :class:`Section`
    - :class:`MediaGallery`
    - :class:`Separator`
    - :class:`FileComponent`

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.Container` instead.

    .. versionadded:: 2.7

    Attributes
    ----------
    components: List[:class:`Component`]
        The components contained in this container.
    accent_color: :class:`Colour` | :obj:`None`
        The accent color of the container.
    spoiler: :class:`bool` | :obj:`None`
        Whether the entire container has the spoiler overlay.
    """

    __slots__: tuple[str, ...] = (
        "accent_color",
        "components",
        "spoiler",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(
        self, data: ContainerComponentPayload, state: ConnectionState | None = None
    ):
        self.type = ComponentType.container
        self.id: int | None = data.get("id")
        self.accent_color: Colour | None = (
            Colour(c) if (c := data.get("accent_color")) else None
        )
        self.spoiler: bool | None = data.get("spoiler")
        self.components = [
            _component_factory(d, state=state) for d in data.get("components", [])
        ]

    @property
    def accent_colour(self) -> Colour | None:
        """Alias for :attr:`accent_color`."""
        return self.accent_color

    def to_dict(self) -> ContainerComponentPayload:
        payload: ComponentPayload = {
            "type": self.type.value,
            "components": [c.to_dict() for c in self.components],
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.accent_color:
            payload["accent_color"] = self.accent_color.value
        if self.spoiler is not None:
            payload["spoiler"] = self.spoiler
        return payload

    def walk_components(self) -> Iterator[Component[Any]]:
        for c in self.components:
            if isinstance(c, _HasSubComponents):
                yield from c.walk_components()
            else:
                yield c

    def get_component(self, id: str | int) -> Component[Any] | None:
        """Get a component from this container. Roughly equivalent to `utils.get(container.components, ...)`.
        If an ``int`` is provided, the component will be retrieved by ``id``, otherwise by ``custom_id``.
        This method will also search for nested components.

        Parameters
        ----------
        id: :class:`str` | :class:`int`
            The custom_id or id of the component to get.

        Returns
        -------
        :class:`Component` | :obj:`None`
            The component with the matching ``id`` or ``custom_id`` if it exists.
        """
        if not id:
            return None
        attr = "id" if isinstance(id, int) else "custom_id"
        for i in self.components:
            if getattr(i, attr, None) == id:
                return i
            if isinstance(i, _HasSubComponents) and (component := i.get_component(id)):
                return component
        return None


class Label(Component[Literal[ComponentType.label]]):
    """Represents a Label used in modals as the top-level component.

    This is a component that allows you to add additional text to another component.
    ``component`` may only be:

    - :class:`InputText`
    - :class:`SelectMenu`

    This inherits from :class:`Component`.

    .. versionadded:: 2.7

    Attributes
    ----------
    component: :class:`Component`
        The component contained in this label. Currently supports :class:`InputText` and :class:`SelectMenu`.
    label: :class:`str`
        The main text associated with this label's ``component``, up to 45 characters.
    description: :class:`str` | :obj:`None`
        The description associated with this label's ``component``, up to 100 characters.
    """

    __slots__: tuple[str, ...] = ("component", "description", "label")

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(self, data: LabelComponentPayload):
        self.type = ComponentType.label
        self.id: int | None = data.get("id")
        self.component = _component_factory(data["component"])
        self.label: str = data["label"]
        self.description: str | None = data.get("description")

    def to_dict(self) -> LabelComponentPayload:
        payload: LabelComponentPayload = {
            "type": self.type.value,
            "component": self.component.to_dict(),
            "label": self.label,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.description:
            payload["description"] = self.description
        return payload

    def walk_components(
        self,
    ) -> Iterator[
        SelectMenu | InputText | FileUpload | RadioGroup | Checkbox | CheckboxGroup
    ]:
        yield from [self.component]


class FileUpload(Component[Literal[ComponentType.file_upload]]):
    """Represents an File Upload component from the Discord Bot UI Kit.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.FileUpload` instead.

    .. versionadded:: 2.7

    Attributes
    ----------
    custom_id: :class:`str` | :obj:`None`
        The custom ID of the file upload field that gets received during an interaction.
    min_values: :class:`int` | :obj:`None`
        The minimum number of files that must be uploaded.
    max_values: :class:`int` | :obj:`None`
        The maximum number of files that can be uploaded.
    required: :class:`bool`
        Whether the file upload field is required or not. Defaults to `True`.
    id: :class:`int` | :obj:`None`
        The file upload's ID.
    file_types: list[:class:`str`] | :obj:`None`
        The file types that can be uploaded to this FileUpload. Only filters by file extension.
    """

    __slots__: tuple[str, ...] = (
        "custom_id",
        "file_types",
        "id",
        "max_values",
        "min_values",
        "required",
        "type",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(self, data: FileUploadComponentPayload):
        self.type = ComponentType.file_upload
        self.id: int | None = data.get("id")
        self.custom_id = data["custom_id"]
        self.min_values: int | None = data.get("min_values", None)
        self.max_values: int | None = data.get("max_values", None)
        self.required: bool | None = data.get("required", True)
        self.file_types: list[str] | None = data.get("file_types")

    def to_dict(self) -> FileUploadComponentPayload:
        payload: FileUploadComponentPayload = {
            "type": self.type.value,
            "custom_id": self.custom_id,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.min_values is not None:
            payload["min_values"] = self.min_values
        if self.max_values is not None:
            payload["max_values"] = self.max_values
        if self.required is not None:
            payload["required"] = self.required
        if self.file_types is not None:
            payload["file_types"] = self.file_types
        return payload


class RadioGroup(Component[Literal[ComponentType.radio_group]]):
    """Represents an Radio Group component from the Discord Bot UI Kit.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.RadioGroup` instead.

    .. versionadded:: 2.8

    Attributes
    ----------
    custom_id: :class:`str`
        The custom ID of the radio group that gets received during an interaction.
    options: List[:class:`RadioGroupOption`]
        A list of options that can be selected in this group, between 2 and 10.
    required: :class:`bool`
        Whether the radio group requires a selection or not. Defaults to ``True``.
    id: :class:`int` | :obj:`None`
        The radio group's ID.
    """

    __slots__: tuple[str, ...] = (
        "custom_id",
        "id",
        "options",
        "required",
        "type",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(self, data: RadioGroupComponentPayload):
        self.type = ComponentType.radio_group
        self.id: int | None = data.get("id")
        self.custom_id = data.get("custom_id")
        self.options: list[RadioGroupOption] = [
            RadioGroupOption.from_dict(option) for option in data.get("options", [])
        ]
        self.required: bool | None = data.get("required", True)

    def to_dict(self) -> RadioGroupComponentPayload:
        payload: RadioGroupComponentPayload = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "options": [opt.to_dict() for opt in self.options],
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.required is not None:
            payload["required"] = self.required
        return payload


class RadioGroupOption:
    """Represents a :class:`discord.RadioGroup`'s option.

    These can be created by users.

    .. versionadded:: 2.8

    Attributes
    ----------
    label: :class:`str`
        The label of the option. This is displayed to users.
        Can only be up to 100 characters.
    value: :class:`str`
        The value of the option. This is not displayed to users.
        If not provided when constructed then it defaults to the
        label. Can only be up to 100 characters.
    description: :class:`str` | :obj:`None`
        An additional description of the option, if any.
        Can only be up to 100 characters.
    default: :class:`bool`
        Whether this option is selected by default. Only 1 option should be set to default within a :class:`discord.RadioGroup`.
    """

    __slots__: tuple[str, ...] = (
        "default",
        "description",
        "label",
        "value",
    )

    def __init__(
        self,
        *,
        label: str,
        value: str = MISSING,
        description: str | None = None,
        default: bool = False,
    ) -> None:
        if len(label) > 100:
            raise ValueError("label must be 100 characters or fewer")

        if value is not MISSING and len(value) > 100:
            raise ValueError("value must be 100 characters or fewer")

        if description is not None and len(description) > 100:
            raise ValueError("description must be 100 characters or fewer")

        self.label = label
        self.value = label if value is MISSING else value
        self.description = description
        self.default = default

    def __repr__(self) -> str:
        return (
            "<RadioGroupOption"
            f" label={self.label!r} value={self.value!r} description={self.description!r} "
            f"default={self.default!r}>"
        )

    def __str__(self) -> str:
        if self.description:
            return f"{self.label}\n{self.description}"
        return self.label

    @classmethod
    def from_dict(cls, data: RadioGroupOptionPayload) -> RadioGroupOption:
        return cls(
            label=data["label"],
            value=data["value"],
            description=data.get("description"),
            default=data.get("default", False),
        )

    def to_dict(self) -> RadioGroupOptionPayload:
        payload: RadioGroupOptionPayload = {
            "label": self.label,
            "value": self.value,
            "default": self.default,
        }

        if self.description:
            payload["description"] = self.description

        return payload


class CheckboxGroup(Component[Literal[ComponentType.checkbox_group]]):
    """Represents an Checkbox Group component from the Discord Bot UI Kit.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.CheckboxGroup` instead.

    .. versionadded:: 2.8

    Attributes
    ----------
    custom_id: :class:`str` | :obj:`None`
        The custom ID of the checkbox group that gets received during an interaction.
    options: List[:class:`CheckboxGroupOption`]
        A list of options that can be selected in this group.
    min_values: :class:`int` | :obj:`None`
        The minimum number of options that must be selected.
        Defaults to 1 and must be between 0 and 25. If set to 0, :attr:`required` must be ``False``.
    max_values: :class:`int` | :obj:`None`
        The maximum number of options that can be selected.
        Must be between 1 and 10.
    required: :class:`bool`
        Whether the checkbox group requires a selection or not. Defaults to ``True``.
    id: :class:`int` | :obj:`None`
        The checkbox group's ID.
    """

    __slots__: tuple[str, ...] = (
        "custom_id",
        "id",
        "max_values",
        "min_values",
        "options",
        "required",
        "type",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(self, data: CheckboxGroupComponentPayload):
        self.type = ComponentType.checkbox_group
        self.id: int | None = data.get("id")
        self.custom_id = data.get("custom_id")
        self.options: list[CheckboxGroupOption] = [
            CheckboxGroupOption.from_dict(option) for option in data.get("options", [])
        ]
        self.min_values: int | None = data.get("min_values", None)
        self.max_values: int | None = data.get("max_values", None)
        self.required: bool | None = data.get("required", True)

    def to_dict(self) -> CheckboxGroupComponentPayload:
        payload: CheckboxGroupComponentPayload = {
            "type": 22,
            "custom_id": self.custom_id,
            "options": [opt.to_dict() for opt in self.options],
        }
        if self.id is not None:
            payload["id"] = self.id

        if self.min_values is not None:
            payload["min_values"] = self.min_values

        if self.max_values is not None:
            payload["max_values"] = self.max_values

        if self.required is not None:
            payload["required"] = self.required

        return payload


class CheckboxGroupOption:
    """Represents a :class:`discord.CheckboxGroup`'s option.

    These can be created by users.

    .. versionadded:: 2.8

    Attributes
    ----------
    label: :class:`str`
        The label of the option. This is displayed to users.
        Can only be up to 100 characters.
    value: :class:`str`
        The value of the option. This is not displayed to users.
        If not provided when constructed then it defaults to the
        label. Can only be up to 100 characters.
    description: :class:`str` | :obj:`None`
        An additional description of the option, if any.
        Can only be up to 100 characters.
    default: :class:`bool`
        Whether this option is selected by default.
    """

    __slots__: tuple[str, ...] = (
        "default",
        "description",
        "label",
        "value",
    )

    def __init__(
        self,
        *,
        label: str,
        value: str = MISSING,
        description: str | None = None,
        default: bool = False,
    ) -> None:
        if len(label) > 100:
            raise ValueError("label must be 100 characters or fewer")

        if value is not MISSING and len(value) > 100:
            raise ValueError("value must be 100 characters or fewer")

        if description is not None and len(description) > 100:
            raise ValueError("description must be 100 characters or fewer")

        self.label = label
        self.value = label if value is MISSING else value
        self.description = description
        self.default = default

    def __repr__(self) -> str:
        return (
            "<CheckboxGroupOption"
            f" label={self.label!r} value={self.value!r} description={self.description!r} "
            f"default={self.default!r}>"
        )

    def __str__(self) -> str:
        if self.description:
            return f"{self.label}\n{self.description}"
        return self.label

    @classmethod
    def from_dict(cls, data: CheckboxGroupOptionPayload) -> CheckboxGroupOption:
        return cls(
            label=data["label"],
            value=data["value"],
            description=data.get("description"),
            default=data.get("default", False),
        )

    def to_dict(self) -> CheckboxGroupOptionPayload:
        payload: CheckboxGroupOptionPayload = {
            "label": self.label,
            "value": self.value,
            "default": self.default,
        }

        if self.description:
            payload["description"] = self.description

        return payload


class Checkbox(Component[Literal[ComponentType.checkbox]]):
    """Represents an Checkbox component from the Discord Bot UI Kit.

    This inherits from :class:`Component`.

    .. note::

        This class is not useable by end-users; see :class:`discord.ui.Checkbox` instead.

    .. versionadded:: 2.8

    Attributes
    ----------
    custom_id: :class:`str` | :obj:`None`
        The custom ID of the checkbox group that gets received during an interaction.
    default: :class:`bool` | :obj:`None`
        Whether this checkbox is selected by default.
    id: :class:`int` | :obj:`None`
        The checkbox group's ID.
    """

    __slots__: tuple[str, ...] = (
        "custom_id",
        "default",
        "id",
        "type",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__
    versions: tuple[int, ...] = (2,)

    def __init__(self, data: CheckboxComponentPayload):
        self.type = ComponentType.checkbox
        self.id: int | None = data.get("id")
        self.custom_id = data.get("custom_id")
        self.default: bool | None = data.get("default", False)

    def to_dict(self) -> CheckboxComponentPayload:
        payload: CheckboxComponentPayload = {
            "type": self.type.value,
            "custom_id": self.custom_id,
        }
        if self.id is not None:
            payload["id"] = self.id

        if self.default is not None:
            payload["default"] = self.default

        return payload


COMPONENT_MAPPINGS = {
    1: ActionRow,
    2: Button,
    3: SelectMenu,
    4: InputText,
    5: SelectMenu,
    6: SelectMenu,
    7: SelectMenu,
    8: SelectMenu,
    9: Section,
    10: TextDisplay,
    11: Thumbnail,
    12: MediaGallery,
    13: FileComponent,
    14: Separator,
    17: Container,
    18: Label,
    19: FileUpload,
    21: RadioGroup,
    22: CheckboxGroup,
    23: Checkbox,
}

STATE_COMPONENTS = (Section, Container, Thumbnail, MediaGallery, FileComponent)


@overload
def _component_factory(
    data: ActionRowPayload, state: ConnectionState | None = None
) -> ActionRow: ...
@overload
def _component_factory(
    data: ButtonComponentPayload, state: ConnectionState | None = None
) -> Button: ...
@overload
def _component_factory(
    data: StringSelectMenuPayload
    | UserSelectMenuPayload
    | RoleSelectMenuPayload
    | MentionableSelectMenuPayload
    | ChannelSelectMenuPayload,
    state: ConnectionState | None = None,
) -> SelectMenu: ...
@overload
def _component_factory(
    data: InputTextComponentPayload, state: ConnectionState | None = None
) -> InputText: ...
@overload
def _component_factory(
    data: SectionComponentPayload, state: ConnectionState | None = None
) -> Section: ...
@overload
def _component_factory(
    data: TextDisplayComponentPayload, state: ConnectionState | None = None
) -> TextDisplay: ...
@overload
def _component_factory(
    data: ThumbnailComponentPayload, state: ConnectionState | None = None
) -> Thumbnail: ...
@overload
def _component_factory(
    data: MediaGalleryComponentPayload, state: ConnectionState | None = None
) -> MediaGallery: ...
@overload
def _component_factory(
    data: FileComponentPayload, state: ConnectionState | None = None
) -> FileComponent: ...
@overload
def _component_factory(
    data: SeparatorComponentPayload, state: ConnectionState | None = None
) -> Separator: ...
@overload
def _component_factory(
    data: ContainerComponentPayload, state: ConnectionState | None = None
) -> Container: ...
@overload
def _component_factory(
    data: LabelComponentPayload, state: ConnectionState | None = None
) -> Label: ...
@overload
def _component_factory(
    data: FileUploadComponentPayload, state: ConnectionState | None = None
) -> FileUpload: ...
@overload
def _component_factory(
    data: RadioGroupComponentPayload, state: ConnectionState | None = None
) -> RadioGroup: ...
@overload
def _component_factory(
    data: CheckboxGroupComponentPayload, state: ConnectionState | None = None
) -> CheckboxGroup: ...
@overload
def _component_factory(
    data: CheckboxComponentPayload, state: ConnectionState | None = None
) -> Checkbox: ...
def _component_factory(
    data: ComponentPayload, state: ConnectionState | None = None
) -> Component[Any]:
    component_type = data["type"]
    if cls := COMPONENT_MAPPINGS.get(component_type):
        if issubclass(cls, STATE_COMPONENTS):
            return cls(cast(Any, data), state=state)
        else:
            return cls(cast(Any, data))
    else:
        as_enum = try_enum(ComponentType, component_type)
        return Component[Any]._raw_construct(type=as_enum)
