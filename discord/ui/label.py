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

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Iterator, Literal, TypeVar, overload

from ..components import Label as LabelComponent
from ..components import SelectDefaultValue, SelectOption, _component_factory
from ..enums import ButtonStyle, ChannelType, ComponentType, InputTextStyle
from ..utils import find, get
from .button import Button
from .input_text import InputText
from .item import ItemCallbackType, ModalItem
from .select import Select

__all__ = ("Label",)

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..emoji import AppEmoji, GuildEmoji
    from ..interaction import Interaction
    from ..partial_emoji import PartialEmoji, _EmojiTag
    from ..types.components import LabelComponent as LabelComponentPayload
    from .modal import DesignerModal


L = TypeVar("L", bound="Label")
M = TypeVar("M", bound="DesignerModal", covariant=True)


class Label(ModalItem[M]):
    """Represents a UI Label used in :class:`discord.ui.DesignerModal`.

    The items currently supported are as follows:

    - :class:`discord.ui.Select`
    - :class:`discord.ui.InputText`

    .. versionadded:: 2.7

    Parameters
    ----------
    item: :class:`ModalItem`
        The initial item attached to this label.
    label: :class:`str`
        The label text. Must be 45 characters or fewer.
    description: Optional[:class:`str`]
        The description for this label. Must be 100 characters or fewer.
    id: Optional[:class:`int`]
        The label's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "item",
        "id",
        "label",
        "description",
    )

    def __init__(
        self,
        label: str,
        item: ModalItem = None,
        *,
        description: str | None = None,
        id: int | None = None,
    ):
        super().__init__()

        self.item: ModalItem = None

        self._underlying = LabelComponent._raw_construct(
            type=ComponentType.label,
            id=id,
            component=None,
            label=label,
            description=description,
        )

        if item:
            self.set_item(item)

    @ModalItem.modal.setter
    def modal(self, value):
        self._modal = value
        if self.item:
            self.item.modal = value

    def _set_component_from_item(self, item: ModalItem):
        self._underlying.component = item._underlying

    def set_item(self, item: ModalItem) -> Self:
        """Set this label's item.

        Parameters
        ----------
        item: Union[:class:`ModalItem`, :class:`InputText`]
            The item to set.
            Currently only supports :class:`~discord.ui.Select` and :class:`~discord.ui.InputText`.

        Raises
        ------
        TypeError
            A :class:`ModalItem` was not passed.
        """

        if not isinstance(item, ModalItem):
            raise TypeError(f"expected ModalItem not {item.__class__!r}")
        if isinstance(item, InputText) and item.label:
            raise ValueError(f"InputText.label cannot be set inside Label")
        if self.modal:
            item.modal = self.modal
        item.parent = self

        self.item = item
        self._set_component_from_item(item)
        return self

    def get_item(self, id: str | int) -> ModalItem | None:
        """Get the item from this label if it matches the provided id.
        If an ``int`` is provided, the item will match by ``id``, otherwise by ``custom_id``.

        Parameters
        ----------
        id: Union[:class:`str`, :class:`int`]
            The id or custom_id of the item to match.

        Returns
        -------
        Optional[:class:`ModalItem`]
            The item if its ``id`` or ``custom_id`` matches.
        """
        if not id:
            return None
        attr = "id" if isinstance(id, int) else "custom_id"
        if getattr(self.item, attr, None) != id:
            return None
        return self.item

    def set_input_text(
        self,
        *,
        style: InputTextStyle = InputTextStyle.short,
        custom_id: str | None = None,
        placeholder: str | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        required: bool | None = True,
        value: str | None = None,
        id: int | None = None,
    ) -> Self:
        """Set this label's item to an input text.

        To set a pre-existing :class:`InputText`, use the
        :meth:`set_item` method, instead.

        Parameters
        ----------
        style: :class:`~discord.InputTextStyle`
            The style of the input text field.
        custom_id: Optional[:class:`str`]
            The ID of the input text field that gets received during an interaction.
        placeholder: Optional[:class:`str`]
            The placeholder text that is shown if nothing is selected, if any.
            Must be 100 characters or fewer.
        min_length: Optional[:class:`int`]
            The minimum number of characters that must be entered.
            Defaults to 0 and must be less than 4000.
        max_length: Optional[:class:`int`]
            The maximum number of characters that can be entered.
            Must be between 1 and 4000.
        required: Optional[:class:`bool`]
            Whether the input text field is required or not. Defaults to ``True``.
        value: Optional[:class:`str`]
            Pre-fills the input text field with this value.
            Must be 4000 characters or fewer.
        id: Optional[:class:`int`]
            The button's ID.
        """

        text = InputText(
            style=style,
            custom_id=custom_id,
            placeholder=placeholder,
            min_length=min_length,
            max_length=max_length,
            required=required,
            value=value,
            id=id,
        )

        return self.set_item(text)

    @overload
    def set_select(
        self,
        select_type: Literal[ComponentType.string_select] = ...,
        *,
        custom_id: str | None = ...,
        placeholder: str | None = ...,
        min_values: int = ...,
        max_values: int = ...,
        options: list[SelectOption] | None = ...,
        required: bool = ...,
        id: int | None = ...,
    ) -> None: ...

    @overload
    def set_select(
        self,
        select_type: Literal[ComponentType.channel_select] = ...,
        *,
        custom_id: str | None = ...,
        placeholder: str | None = ...,
        min_values: int = ...,
        max_values: int = ...,
        channel_types: list[ChannelType] | None = ...,
        required: bool = ...,
        id: int | None = ...,
        default_values: Sequence[SelectDefaultValue] | None = ...,
    ) -> None: ...

    @overload
    def set_select(
        self,
        select_type: Literal[
            ComponentType.user_select,
            ComponentType.role_select,
            ComponentType.mentionable_select,
        ] = ...,
        *,
        custom_id: str | None = ...,
        placeholder: str | None = ...,
        min_values: int = ...,
        max_values: int = ...,
        required: bool = ...,
        id: int | None = ...,
        default_values: Sequence[SelectDefaultValue] | None = ...,
    ) -> None: ...

    def set_select(
        self,
        select_type: ComponentType = ComponentType.string_select,
        *,
        custom_id: str | None = None,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        options: list[SelectOption] | None = None,
        channel_types: list[ChannelType] | None = None,
        required: bool = True,
        id: int | None = None,
        default_values: Sequence[SelectDefaultValue] | None = ...,
    ) -> Self:
        """Set this label's item to a select menu.

        Parameters
        ----------
        select_type: :class:`discord.ComponentType`
            The type of select to create. Must be one of
            :attr:`discord.ComponentType.string_select`, :attr:`discord.ComponentType.user_select`,
            :attr:`discord.ComponentType.role_select`, :attr:`discord.ComponentType.mentionable_select`,
            or :attr:`discord.ComponentType.channel_select`.
        custom_id: :class:`str`
            The custom ID of the select menu that gets received during an interaction.
            If not given then one is generated for you.
        placeholder: Optional[:class:`str`]
            The placeholder text that is shown if nothing is selected, if any.
        min_values: :class:`int`
            The minimum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        max_values: :class:`int`
            The maximum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        options: List[:class:`discord.SelectOption`]
            A list of options that can be selected in this menu.
            Only valid for selects of type :attr:`discord.ComponentType.string_select`.
        channel_types: List[:class:`discord.ChannelType`]
            A list of channel types that can be selected in this menu.
            Only valid for selects of type :attr:`discord.ComponentType.channel_select`.
        required: :class:`bool`
            Whether the select is required or not. Defaults to ``True``.
        id: Optional[:class:`int`]
            The select menu's ID.
        default_values: Optional[Sequence[Union[:class:`discord.SelectDefaultValue`, :class:`discord.abc.Snowflake`]]]
            The default values of this select. Only applicable if :attr:`.select_type` is not :attr:`discord.ComponentType.string_select`.

            These can be either :class:`discord.SelectDefaultValue` instances or models, which will be converted into :class:`discord.SelectDefaultValue`
            instances.
        """

        select = Select(
            select_type=select_type,
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options or [],
            channel_types=channel_types or [],
            required=required,
            id=id,
            default_values=default_values,
        )

        return self.set_item(select)

    @property
    def label(self) -> str:
        """The label text. Must be 45 characters or fewer."""
        return self._underlying.label

    @label.setter
    def label(self, value: str) -> None:
        self._underlying.label = value

    @property
    def description(self) -> str | None:
        """The description for this label. Must be 100 characters or fewer."""
        return self._underlying.description

    @description.setter
    def description(self, value: str | None) -> None:
        self._underlying.description = value

    def is_dispatchable(self) -> bool:
        return self.item.is_dispatchable()

    def is_persistent(self) -> bool:
        return self.item.is_persistent()

    def refresh_component(self, component: LabelComponent) -> None:
        self._underlying = component
        self.item.refresh_component(component.component)

    def walk_items(self) -> Iterator[ModalItem]:
        yield from [self.item]

    def to_component_dict(self) -> LabelComponentPayload:
        self._set_component_from_item(self.item)
        return super().to_component_dict()

    def refresh_from_modal(
        self, interaction: Interaction, data: LabelComponentPayload
    ) -> None:
        return self.item.refresh_from_modal(interaction, data.get("component", {}))

    @classmethod
    def from_component(cls: type[L], component: LabelComponent) -> L:
        from .view import _component_to_item

        item = _component_to_item(component.component)
        return cls(
            item,
            id=component.id,
            label=component.label,
            description=component.description,
        )
