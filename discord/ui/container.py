from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, TypeVar

from ..colour import Colour
from ..components import ActionRow
from ..components import Container as ContainerComponent
from ..components import _component_factory
from ..enums import ComponentType, SeparatorSpacingSize
from ..utils import find, get
from .action_row import ActionRow
from .button import Button
from .select import Select
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


C = TypeVar("C", bound="Container")
V = TypeVar("V", bound="View", covariant=True)


class Container(Item[V]):
    """Represents a UI Container.

    The current items supported are as follows:

    - :class:`discord.ui.ActionRow`
    - :class:`discord.ui.Section`
    - :class:`discord.ui.TextDisplay`
    - :class:`discord.ui.MediaGallery`
    - :class:`discord.ui.File`
    - :class:`discord.ui.Separator`

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
        "colour",
        "spoiler",
        "id",
    )

    def __init__(
        self,
        *items: Item,
        colour: int | Colour | None = None,
        color: int | Colour | None = None,
        spoiler: bool = False,
        id: int | None = None,
    ):
        super().__init__()

        self.items: list[Item] = []

        self._underlying = ContainerComponent._raw_construct(
            type=ComponentType.container,
            id=id,
            components=[],
            accent_color=None,
            spoiler=spoiler,
        )
        self.color = colour or color
        for i in items:
            self.add_item(i)

    def _add_component_from_item(self, item: Item):
        self._underlying.components.append(item._underlying)

    def _set_components(self, items: list[Item]):
        self._underlying.components.clear()
        for item in items:
            self._add_component_from_item(item)

    def add_item(self, item: Item) -> Self:
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

        if isinstance(item, (Button, Select)):
            raise TypeError(
                f"{item.__class__!r} cannot be added directly. Use ActionRow instead."
            )

        item._view = self.view
        if hasattr(item, "items"):
            item.view = self
        item.parent = self

        self.items.append(item)
        self._add_component_from_item(item)
        return self

    def remove_item(self, item: Item | str | int) -> Self:
        """Removes an item from the container. If an int or str is passed, it will remove by Item :attr:`id` or ``custom_id`` respectively.

        Parameters
        ----------
        item: Union[:class:`Item`, :class:`int`, :class:`str`]
            The item, ``id``, or item ``custom_id`` to remove from the container.
        """

        if isinstance(item, (str, int)):
            item = self.get_item(item)
        try:
            if isinstance(item, Container):
                self.items.remove(item)
            else:
                item.parent.remove_item(item)
        except ValueError:
            pass
        return self

    def get_item(self, id: str | int) -> Item | None:
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

    def add_row(
        self,
        *items: Item,
        id: int | None = None,
    ) -> Self:
        """Adds an :class:`ActionRow` to the container.

        To append a pre-existing :class:`ActionRow`, use :meth:`add_item` instead.

        Parameters
        ----------
        *items: Union[:class:`Button`, :class:`Select`]
            The items this action row contains.
        id: Optiona[:class:`int`]
            The action row's ID.
        """

        a = ActionRow(*items, id=id)

        return self.add_item(a)

    def add_section(
        self,
        *items: Item,
        accessory: Item,
        id: int | None = None,
    ) -> Self:
        """Adds a :class:`Section` to the container.

        To append a pre-existing :class:`Section`, use the
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

    def add_text(self, content: str, id: int | None = None) -> Self:
        """Adds a :class:`TextDisplay` to the container.

        Parameters
        ----------
        content: :class:`str`
            The content of the TextDisplay
        id: Optiona[:class:`int`]
            The text displays' ID.
        """

        text = TextDisplay(content, id=id)

        return self.add_item(text)

    def add_gallery(
        self,
        *items: Item,
        id: int | None = None,
    ) -> Self:
        """Adds a :class:`MediaGallery` to the container.

        To append a pre-existing :class:`MediaGallery`, use :meth:`add_item` instead.

        Parameters
        ----------
        *items: :class:`MediaGalleryItem`
            The media this gallery contains.
        id: Optiona[:class:`int`]
            The gallery's ID.
        """

        g = MediaGallery(*items, id=id)

        return self.add_item(g)

    def add_file(self, url: str, spoiler: bool = False, id: int | None = None) -> Self:
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

    def add_separator(
        self,
        *,
        divider: bool = True,
        spacing: SeparatorSpacingSize = SeparatorSpacingSize.small,
        id: int | None = None,
    ) -> Self:
        """Adds a :class:`Separator` to the container.

        Parameters
        ----------
        divider: :class:`bool`
            Whether the separator is a divider. Defaults to ``True``.
        spacing: :class:`~discord.SeparatorSpacingSize`
            The spacing size of the separator. Defaults to :attr:`~discord.SeparatorSpacingSize.small`.
        id: Optional[:class:`int`]
            The separator's ID.
        """

        s = Separator(divider=divider, spacing=spacing, id=id)

        return self.add_item(s)

    def copy_text(self) -> str:
        """Returns the text of all :class:`~discord.ui.TextDisplay` items in this container.
        Equivalent to the `Copy Text` option on Discord clients.
        """
        return "\n".join(t for i in self.items if (t := i.copy_text()))

    @property
    def spoiler(self) -> bool:
        """Whether the container has the spoiler overlay. Defaults to ``False``."""
        return self._underlying.spoiler

    @spoiler.setter
    def spoiler(self, spoiler: bool) -> None:
        self._underlying.spoiler = spoiler

    @property
    def colour(self) -> Colour | None:
        return self._underlying.accent_color

    @colour.setter
    def colour(self, value: int | Colour | None):  # type: ignore
        if value is None or isinstance(value, Colour):
            self._underlying.accent_color = value
        elif isinstance(value, int):
            self._underlying.accent_color = Colour(value=value)
        else:
            raise TypeError(
                "Expected discord.Colour, int, or None but received"
                f" {value.__class__.__name__} instead."
            )

    color = colour

    @Item.view.setter
    def view(self, value):
        self._view = value
        for item in self.items:
            item.parent = self
            item._view = value
            if hasattr(item, "items") or hasattr(item, "children"):
                item.view = value

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def is_dispatchable(self) -> bool:
        return any(item.is_dispatchable() for item in self.items)

    def is_persistent(self) -> bool:
        return all(item.is_persistent() for item in self.items)

    def refresh_component(self, component: ContainerComponent) -> None:
        self._underlying = component
        i = 0
        for y in component.components:
            x = self.items[i]
            x.refresh_component(y)
            i += 1

    def disable_all_items(self, *, exclusions: list[Item] | None = None) -> Self:
        """
        Disables all buttons and select menus in the container.

        Parameters
        ----------
        exclusions: Optional[List[:class:`Item`]]
            A list of items in `self.items` to not disable from the view.
        """
        for item in self.walk_items():
            if hasattr(item, "disabled") and (
                exclusions is None or item not in exclusions
            ):
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
        for item in self.items:
            if hasattr(item, "walk_items"):
                yield from item.walk_items()
            else:
                yield item

    def to_component_dict(self) -> ContainerComponentPayload:
        self._set_components(self.items)
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[C], component: ContainerComponent) -> C:
        from .view import _component_to_item

        items = [
            _component_to_item(c) for c in _walk_all_components(component.components)
        ]
        return cls(
            *items,
            colour=component.accent_color,
            spoiler=component.spoiler,
            id=component.id,
        )

    callback = None
