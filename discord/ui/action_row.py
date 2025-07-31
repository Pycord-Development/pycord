from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, ClassVar, Iterator, TypeVar

from ..colour import Colour
from ..components import ActionRow as ActionRowComponent
from ..components import _component_factory
from ..enums import ComponentType, SeparatorSpacingSize
from ..utils import find, get
from .file import File
from .item import Item, ItemCallbackType
from .media_gallery import MediaGallery
from .section import Section
from .separator import Separator
from .text_display import TextDisplay
from .view import _walk_all_components

__all__ = ("Container",)

A = TypeVar("A", bound="ActionRow")
V = TypeVar("V", bound="View", covariant=True)

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.components import ContainerComponent as ContainerComponentPayload
    from .view import View
    from .button import Button
    from .select import Select

    ChildrenItemsTypes = Button | Select


class ActionRow(Item[V]):
    """Represents a UI ActionRow.

    The current items supported are as follows:

    - :class:`discord.ui.Button`
    - :class:`discord.ui.Select`

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`Item`
        The initial items in this container.
    colour: Union[:class:`Colour`, :class:`int`]
        The accent colour of the container. Aliased to ``color`` as well.
    spoiler: Optional[:class:`bool`]
        Whether this container has the spoiler overlay.
    id: Optional[:class:`int`]
        The container's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "items",
        "spoiler",
        "id",
    )

    __container_children_items__: ClassVar[list[ItemCallbackType]] = []

    def __init_subclass__(cls) -> None:
        children: list[ItemCallbackType] = []
        for base in reversed(cls.__mro__):
            for member in base.__dict__.values():
                if hasattr(member, "__discord_ui_model_type__"):
                    children.append(member)

        cls.__container_children_items__ = children

    def __init__(
        self,
        *items: ChildrenItemsTypes,
        colour: int | Colour | None = None,
        color: int | Colour | None = None,
        spoiler: bool = False,
        id: int | None = None,
    ):
        super().__init__()

        self.items: list[ChildrenItemsTypes] = []

        self._underlying = ActionRowComponent._raw_construct(
            type=ComponentType.action_row,
            id=id,
            children=[],
        )
        self.color = colour or color

        for i in items:
            self.add_item(i)

    def _add_component_from_item(self, item: ChildrenItemsTypes):
        self._underlying.components.append(item._underlying)

    def _set_components(self, items: list[ChildrenItemsTypes]):
        self._underlying.components.clear()
        for item in items:
            self._add_component_from_item(item)

    def add_item(self, item: ChildrenItemsTypes) -> Self:
        """Adds an item to the container.

        Parameters
        ----------
        item: :class:`Item`
            The item to add to the container.

        Raises
        ------
        TypeError
            An :class:`Item` was not passed.
        """

        if not isinstance(item, Item):
            raise TypeError(f"expected Item not {item.__class__!r}")

        item._view = self.view
        if hasattr(item, "items"):
            item.view = self
        item.parent = self

        self.items.append(item)
        self._add_component_from_item(item)
        return self

    def remove_item(self, item: ChildrenItemsTypes | str | int) -> Self:
        """Removes an item from the container. If an int or str is passed, it will remove by Item :attr:`id` or ``custom_id`` respectively.

        Parameters
        ----------
        item: Union[:class:`Item`, :class:`int`, :class:`str`]
            The item, ``id``, or item ``custom_id`` to remove from the container.
        """

        if isinstance(item, (str, int)):
            item = self.get_item(item)
        try:
            self.items.remove(item)
        except ValueError:
            pass
        return self

    def get_item(self, id: str | int) -> ChildrenItemsTypes | None:
        """Get an item from this container. Roughly equivalent to `utils.get(container.items, ...)`.
        If an ``int`` is provided, the item will be retrieved by ``id``, otherwise by ``custom_id``.
        This method will also search for nested items.

        Parameters
        ----------
        id: Union[:class:`str`, :class:`int`]
            The id or custom_id of the item to get.

        Returns
        -------
        Optional[:class:`Item`]
            The item with the matching ``id`` or ``custom_id`` if it exists.
        """
        if not id:
            return None
        attr = "id" if isinstance(id, int) else "custom_id"
        child = find(lambda i: getattr(i, attr, None) == id, self.items)
        if not child:
            for i in self.items:
                if hasattr(i, "get_item"):
                    if child := i.get_item(id):
                        return child
        return child

    def copy_text(self) -> str:
        """Returns the text of all :class:`~discord.ui.TextDisplay` items in this container.
        Equivalent to the `Copy Text` option on Discord clients.
        """
        return "\n".join(t for i in self.items if (t := i.copy_text()))

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def width(self) -> int:
        return 5

    def is_dispatchable(self) -> bool:
        return any(item.is_dispatchable() for item in self.items)

    def refresh_component(self, component: ActionRowComponent) -> None:
        self._underlying = component
        flattened = []
        for c in component.children:
            flattened.append(c)
        for i, y in enumerate(flattened):
            x = self.items[i]
            x.refresh_component(y)

    def disable_all_items(self, *, exclusions: list[ChildrenItemsTypes] | None = None) -> Self:
        """
        Disables all buttons and select menus in the ActionRow.

        Parameters
        ----------
        exclusions: Optional[List[:class:`Item`]]
            A list of items in `self.items` to not disable from the view.
        """
        for item in self.walk_items():
            if hasattr(item, "disabled") and (exclusions is None or item not in exclusions):
                item.disabled = True
        return self

    def enable_all_items(self, *, exclusions: list[ChildrenItemsTypes] | None = None) -> Self:
        """
        Enables all buttons and select menus in the container.

        Parameters
        ----------
        exclusions: Optional[List[:class:`Item`]]
            A list of items in `self.items` to not enable from the view.
        """
        for item in self.walk_items():
            if hasattr(item, "disabled") and (exclusions is None or item not in exclusions):
                item.disabled = False
        return self

    def walk_items(self) -> Iterator[ChildrenItemsTypes]:
        yield from self.items

    def to_component_dict(self) -> ContainerComponentPayload:
        self._set_components(self.items)
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[Self], component: ActionRowComponent) -> Self:
        from .view import _component_to_item  # noqa: PLC0415 # circular import

        items = [_component_to_item(c) for c in _walk_all_components(component.children)]
        return cls(
            *items,
            colour=component.accent_color,
            spoiler=component.spoiler,
            id=component.id,
        )

    callback = None
