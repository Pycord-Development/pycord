from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, ClassVar, Iterator, TypeVar

from ..colour import Colour
from ..components import ActionRow as ActionRowComponent
from ..components import Container as ContainerComponent
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

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.components import ContainerComponent as ContainerComponentPayload
    from .view import View


AC = TypeVar("A", bound="ActionRow")
V = TypeVar("V", bound="View", covariant=True)


class ActionRow(Item[V]):
    """Represents a UI Action Row.

    The items supported are as follows:

    - :class:`discord.ui.Select`
    - :class:`discord.ui.Button` (in views)
    - :class:`discord.ui.InputText` (in modals)

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`Item`
        The initial items in this action row.
    id: Optional[:class:`int`]
        The action's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "items",
        "id",
    )

    __row_children_items__: ClassVar[list[ItemCallbackType]] = []

    def __init_subclass__(cls) -> None:
        children: list[ItemCallbackType] = []
        for base in reversed(cls.__mro__):
            for member in base.__dict__.values():
                if hasattr(member, "__discord_ui_model_type__"):
                    children.append(member)

        cls.__row_children_items__ = children

    def __init__(
        self,
        *items: Item,
        id: int | None = None,
    ):
        super().__init__()

        self.items: list[Item] = []

        self._underlying = ActionRowComponent._raw_construct(
            type=ComponentType.action_row,
            id=id,
            components=[],
        )

        for func in self.__row_children_items__:
            item: Item = func.__discord_ui_model_type__(
                **func.__discord_ui_model_kwargs__
            )
            item.callback = partial(func, self, item)
            self.add_item(item)
            setattr(self, func.__name__, item)
        for i in items:
            self.add_item(i)

    def _add_component_from_item(self, item: Item):
        self._underlying.components.append(item._underlying)

    def _set_components(self, items: list[Item]):
        self._underlying.components.clear()
        for item in items:
            self._add_component_from_item(item)

    def add_item(self, item: Item) -> Self:
        """Adds an item to the action row.

        Parameters
        ----------
        item: :class:`Item`
            The item to add to the action row.

        Raises
        ------
        TypeError
            An :class:`Item` was not passed.
        """

        if not isinstance(item, Item):
            raise TypeError(f"expected Item not {item.__class__!r}")

        item._view = self.view
        item.parent = self

        self.items.append(item)
        self._add_component_from_item(item)
        return self

    def remove_item(self, item: Item | str | int) -> Self:
        """Removes an item from the action row. If an int or str is passed, it will remove by Item :attr:`id` or ``custom_id`` respectively.

        Parameters
        ----------
        item: Union[:class:`Item`, :class:`int`, :class:`str`]
            The item, ``id``, or item ``custom_id`` to remove from the action row.
        """

        if isinstance(item, (str, int)):
            item = self.get_item(item)
        try:
            self.items.remove(item)
        except ValueError:
            pass
        return self

    def get_item(self, id: str | int) -> Item | None:
        """Get an item from this action row. Roughly equivalent to `utils.get(row.items, ...)`.
        If an ``int`` is provided, the item will be retrieved by ``id``, otherwise by ``custom_id``.

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
        return child

    def add_button(
        self,
        *,
        accessory: Item,
        id: int | None = None,
    ) -> Self:
        """Adds a :class:`Button` to the action row.

        To append a pre-existing :class:`Button`, use the
        :meth:`add_item` method, instead.

        Parameters
        ----------
        *items: :class:`Item`
            The items contained in this section, up to 3.
            Currently only supports :class:`~discord.ui.TextDisplay`.
        accessory: Optional[:class:`Item`]
            The section's accessory. This is displayed in the top right of the section.
            Currently only supports :class:`~discord.ui.Button` and :class:`~discord.ui.Thumbnail`.
        id: Optional[:class:`int`]
            The section's ID.
        """

        section = Section(*items, accessory=accessory, id=id)

        return self.add_item(section)

    def add_select(
        self, url: str, spoiler: bool = False, id: int | None = None
    ) -> Self:
        """Adds a :class:`TextDisplay` to the container.

        Parameters
        ----------
        url: :class:`str`
            The URL of this file's media. This must be an ``attachment://`` URL that references a :class:`~discord.File`.
        spoiler: Optional[:class:`bool`]
            Whether the file has the spoiler overlay. Defaults to ``False``.
        id: Optiona[:class:`int`]
            The file's ID.
        """

        f = File(url, spoiler=spoiler, id=id)

        return self.add_item(f)

    @Item.view.setter
    def view(self, value):
        self._view = value
        for item in self.items:
            item.parent = self
            item._view = value

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def width(self) -> int:
        return 5

    def is_dispatchable(self) -> bool:
        return any(item.is_dispatchable() for item in self.items)

    def is_persistent(self) -> bool:
        return all(item.is_persistent() for item in self.items)

    def refresh_component(self, component: ActionRowComponent) -> None:
        self._underlying = component
        i = 0
        for y in component.components:
            x = self.items[i]
            x.refresh_component(y)
            i += 1

    def disable_all_items(self, *, exclusions: list[Item] | None = None) -> Self:
        """
        Disables all items in this row.

        Parameters
        ----------
        exclusions: Optional[List[:class:`Item`]]
            A list of items in `self.items` to not disable from the view.
        """
        for item in self.walk_items():
            if exclusions is None or item not in exclusions:
                item.disabled = True
        return self

    def enable_all_items(self, *, exclusions: list[Item] | None = None) -> Self:
        """
        Enables all buttons and select menus in the container.

        Parameters
        ----------
        exclusions: Optional[List[:class:`Item`]]
            A list of items in `self.items` to not enable from the view.
        """
        for item in self.walk_items():
            if hasattr(item, "disabled") and (
                exclusions is None or item not in exclusions
            ):
                item.disabled = False
        return self

    def walk_items(self) -> Iterator[Item]:
        yield from self.items

    def to_component_dict(self) -> ContainerComponentPayload:
        self._set_components(self.items)
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[C], component: ActionRowComponent) -> C:
        from .view import _component_to_item

        items = [
            _component_to_item(c) for c in _walk_all_components(component.components)
        ]
        return cls(
            *items,
            id=component.id,
        )

    callback = None
