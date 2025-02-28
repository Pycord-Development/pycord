from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, TypeVar, ClassVar

from ..colour import Colour
from ..components import ActionRow
from ..components import Container as ContainerComponent
from ..components import _component_factory
from ..enums import ComponentType, SeparatorSpacingSize
from .file import File
from .item import Item
from .media_gallery import MediaGallery
from .section import Section
from .separator import Separator
from .text_display import TextDisplay
from .view import _walk_all_components
from .item import Item, ItemCallbackType

__all__ = ("Container",)

if TYPE_CHECKING:
    from ..types.components import ContainerComponent as ContainerComponentPayload
    from .view import View


C = TypeVar("C", bound="Container")
V = TypeVar("V", bound="View", covariant=True)


class Container(Item[V]):
    """Represents a UI Container. Containers may contain up to 10 items.

    The current items supported are:

    - :class:`discord.ui.Button`
    - :class:`discord.ui.Select`
    - :class:`discord.ui.Section`
    - :class:`discord.ui.TextDisplay`
    - :class:`discord.ui.MediaGallery`
    - :class:`discord.ui.File`
    - :class:`discord.ui.Separator`

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`Item`
        The initial items in this container, up to 10.
    colour: Union[:class:`Colour`, :class:`int`]
        The accent colour of the container. Aliased to ``color`` as well.
    """

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
        *items: Item,
        colour: int | Colour | None = None,
        color: int | Colour | None = None,
        spoiler: bool = False,
    ):
        super().__init__()

        self.items = []
        self._color = colour
        for func in self.__container_children_items__:
            item: Item = func.__discord_ui_model_type__(
                **func.__discord_ui_model_kwargs__
            )
            item.callback = partial(func, self.view, item)
            if self.view:
                setattr(self.view, func.__name__, item)
            self.add_item(item)

        self._underlying = ContainerComponent._raw_construct(
            type=ComponentType.container,
            id=None,
            components=[],
            accent_color=colour,
            spoiler=spoiler,
        )
        for i in items:
            self.add_item(i)

    def add_item(self, item: Item) -> None:
        """Adds an item to the container.

        Parameters
        ----------
        item: :class:`Item`
            The item to add to the container.

        Raises
        ------
        TypeError
            An :class:`Item` was not passed.
        ValueError
            Maximum number of items has been exceeded (10).
        """

        if not isinstance(item, Item):
            raise TypeError(f"expected Item not {item.__class__!r}")
        
        item._view = self.view

        self.items.append(item)

        # reuse weight system?

        if item._underlying.is_v2():
            self._underlying.components.append(item._underlying)
        else:
            for row in reversed(self._underlying.components):
                if (
                    isinstance(row, ActionRow) and row.width + item.width <= 5
                ):  # If a valid ActionRow exists
                    row.children.append(item._underlying)
                    break
            else:
                row = ActionRow.with_components(item._underlying)
                self._underlying.components.append(row)

    def add_section(self, *items: Item, accessory: Item):
        """Adds a :class:`Section` to the container.

        To append a pre-existing :class:`Section` use the
        :meth:`add_item` method instead.

        Parameters
        ----------
        *items: :class:`Item`
            The items contained in this section, up to 3.
            Currently only supports :class:`~discord.ui.TextDisplay`.
        accessory: Optional[:class:`Item`]
            The section's accessory. This is displayed in the top right of the section.
            Currently only supports :class:`~discord.ui.Button` and :class:`~discord.ui.Thumbnail`.
        """
        # accept raw strings?

        section = Section(*items, accessory=accessory)

        self.add_item(section)

    def add_text(self, content: str) -> None:
        """Adds a :class:`TextDisplay` to the container.

        Parameters
        ----------
        content: :class:`str`
            The content of the TextDisplay
        """

        text = TextDisplay(content)

        self.add_item(text)

    def add_gallery(
        self,
        *items: Item,
    ):
        """Adds a :class:`MediaGallery` to the container.

        To append a pre-existing :class:`MediaGallery` use the
        :meth:`add_item` method instead.

        Parameters
        ----------
        *items: List[:class:`MediaGalleryItem`]
            The media this gallery contains.
        """
        # accept raw urls?

        g = MediaGallery(*items)

        self.add_item(g)

    def add_file(self, url: str, spoiler: bool = False) -> None:
        """Adds a :class:`TextDisplay` to the container.

        Parameters
        ----------
        url: :class:`str`
            The URL of this file's media. This must be an ``attachment://`` URL that references a :class:`~discord.File`.
        spoiler: Optional[:class:`bool`]
            Whether the file is a spoiler. Defaults to ``False``.
        """

        f = File(url, spoiler=spoiler)

        self.add_item(f)

    def add_separator(
        self,
        *,
        divider: bool = True,
        spacing: SeparatorSpacingSize = SeparatorSpacingSize.small,
    ) -> None:
        """Adds a :class:`Separator` to the container.

        Parameters
        ----------
        divider: :class:`bool`
            Whether the separator is a divider. Defaults to ``True``.
        spacing: :class:`~discord.SeparatorSpacingSize`
            The spacing size of the separator. Defaults to :attr:`~discord.SeparatorSpacingSize.small`.
        """

        s = Separator(divider=divider, spacing=spacing)

        self.add_item(s)

    @property
    def spoiler(self) -> bool:
        """Whether the container is a spoiler. Defaults to ``False``."""
        return self._spoiler

    @spoiler.setter
    def spoiler(self, spoiler: bool) -> None:
        self._spoiler = spoiler
        self._underlying.spoiler = spoiler

    @property
    def colour(self) -> Colour | None:
        return getattr(self, "_colour", None)

    @colour.setter
    def colour(self, value: int | Colour | None):  # type: ignore
        if value is None or isinstance(value, Colour):
            self._colour = value
        elif isinstance(value, int):
            self._colour = Colour(value=value)
        else:
            raise TypeError(
                "Expected discord.Colour, int, or None but received"
                f" {value.__class__.__name__} instead."
            )
        self._underlying.accent_color = self.colour

    color = colour

    @view.setter
    def view(self, value):
        self._view = value
        for item in self.items:
            item._view = value

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def width(self) -> int:
        return 5

    def to_component_dict(self) -> ContainerComponentPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[C], component: ContainerComponent) -> C:
        from .view import _component_to_item

        items = [
            _component_to_item(c) for c in _walk_all_components(component.components)
        ]
        return cls(*items, colour=component.accent_color, spoiler=component.spoiler)

    callback = None
