from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, ClassVar, Iterator, TypeVar

from ..components import Label as LabelComponent
from ..components import SelectOption, _component_factory
from ..enums import ButtonStyle, ChannelType, ComponentType, InputTextStyle
from ..utils import find, get
from .button import Button
from .item import Item, ItemCallbackType
from .select import Select
from .input_text import InputText

__all__ = ("Label",)

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..emoji import AppEmoji, GuildEmoji
    from ..partial_emoji import PartialEmoji, _EmojiTag
    from ..types.components import Label as LabelPayload
    from .view import View


L = TypeVar("L", bound="Label")
V = TypeVar("V", bound="View", covariant=True)


class Label(Item[V]):
    """Represents a UI Label used in :class:`discord.ui.DesignerModal`.

    The items currently supported are as follows:

    - :class:`discord.ui.Select`
    - :class:`discord.ui.InputText`

    .. versionadded:: 2.7

    Parameters
    ----------
    item: :class:`Item`
        The initial item in this label.
    label: :class:`str`
        The label text.
        Must be 45 characters or fewer.
    description: Optional[:class:`str`]
        The description for this label.
        Must be 100 characters or fewer.
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
        item: Item,
        *,
        label: str,
        description: str | None = None,
        id: int | None = None,
    ):
        super().__init__()

        self.item: Item = None

        self._underlying = LabelComponent._raw_construct(
            type=ComponentType.label,
            id=id,
            component=None,
            label=label,
            description=description,
        )

        self.set_item(item)

    def _set_component_from_item(self, item: Item):
        self._underlying.component = item._underlying

    def set_item(self, item: Item) -> Self:
        """Set this label's item.

        Parameters
        ----------
        item: :class:`Item`
            The item to set.
            Currently only supports :class:`~discord.ui.Select` and :class:`~discord.ui.InputText`.

        Raises
        ------
        TypeError
            An :class:`Item` was not passed.
        """

        if not isinstance(item, Item):
            raise TypeError(f"expected Item not {item.__class__!r}")
        if isinstance(item, InputText) and item.label:
            raise ValueError(f"InputText.label cannot be set inside Label")
        if self.view:
            item._view = self.view
        item.parent = self

        self.item = item
        self._set_component_from_item(item)
        return self

    def get_item(self, id: str | int) -> Item | None:
        """Get the item from this label if it matches the provided id.
        If an ``int`` is provided, the item will match by ``id``, otherwise by ``custom_id``.

        Parameters
        ----------
        id: Union[:class:`str`, :class:`int`]
            The id or custom_id of the item to match.

        Returns
        -------
        Optional[:class:`Item`]
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
        disabled: bool = False,
        id: int | None = None,
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
        disabled: :class:`bool`
            Whether the select is disabled or not. Defaults to ``False``.
        id: Optional[:class:`int`]
            The select menu's ID.
        """

        select = Select(
            select_type=select_type,
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options or [],
            channel_types=channel_types or [],
            disabled=disabled,
            id=id,
        )

        return self.set_item(select)

    @Item.view.setter
    def view(self, value):
        self._view = value
        self.item.parent = self
        self.item._view = value

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def is_dispatchable(self) -> bool:
        return self.item.is_dispatchable()

    def is_persistent(self) -> bool:
        return self.item.is_persistent()

    def refresh_component(self, component: LabelComponent) -> None:
        self._underlying = component
        self.item.refresh_component(component.component)

    def walk_items(self) -> Iterator[Item]:
        yield from [self.item]

    def to_component_dict(self) -> LabelPayload:
        self._set_component_from_item(self.item)
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[L], component: LabelComponent) -> L:
        from .view import _component_to_item

        item = _component_to_item(component.component)
        return cls(
            item,
            id=component.id,
            label=component.label,
            description=component.description
        )

    callback = None
