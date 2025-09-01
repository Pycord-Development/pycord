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

from typing import TYPE_CHECKING, Any, Callable, Coroutine, Generic, TypeVar

from ..interactions import Interaction

__all__ = ("Item",)

if TYPE_CHECKING:
    from ..components import Component
    from ..enums import ComponentType
    from .view import View

I = TypeVar("I", bound="Item")
V = TypeVar("V", bound="View", covariant=True)
ItemCallbackType = Callable[[Any, I, Interaction], Coroutine[Any, Any, Any]]


class Item(Generic[V]):
    """Represents the base UI item that all UI components inherit from.

    The following are the original items:

    - :class:`discord.ui.Button`
    - :class:`discord.ui.Select`

    And the following are new items under the "Components V2" specification:

    - :class:`discord.ui.Section`
    - :class:`discord.ui.TextDisplay`
    - :class:`discord.ui.Thumbnail`
    - :class:`discord.ui.MediaGallery`
    - :class:`discord.ui.File`
    - :class:`discord.ui.Separator`
    - :class:`discord.ui.Container`

    .. versionadded:: 2.0

    .. versionchanged:: 2.7
        Added V2 Components.
    """

    __item_repr_attributes__: tuple[str, ...] = ("row",)

    def __init__(self):
        self._view: V | None = None
        self._row: int | None = None
        self._rendered_row: int | None = None
        self._underlying: Component | None = None
        # This works mostly well but there is a gotcha with
        # the interaction with from_component, since that technically provides
        # a custom_id most dispatchable items would get this set to True even though
        # it might not be provided by the library user. However, this edge case doesn't
        # actually affect the intended purpose of this check because from_component is
        # only called upon edit and we're mainly interested during initial creation time.
        self._provided_custom_id: bool = False
        self.parent: Item | View | None = self.view

    def to_component_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def refresh_component(self, component: Component) -> None:
        self._underlying = component

    def refresh_state(self, interaction: Interaction) -> None:
        return None

    def refresh_from_modal(self, interaction: Interaction, data: dict) -> None:
        return None

    @classmethod
    def from_component(cls: type[I], component: Component) -> I:
        return cls()

    @property
    def type(self) -> ComponentType:
        raise NotImplementedError

    def is_dispatchable(self) -> bool:
        return False

    def is_storable(self) -> bool:
        return False

    def is_persistent(self) -> bool:
        return not self.is_dispatchable() or self._provided_custom_id

    def uses_label(self) -> bool:
        return False

    def copy_text(self) -> str:
        return ""

    def __repr__(self) -> str:
        attrs = " ".join(
            f"{key}={getattr(self, key)!r}" for key in self.__item_repr_attributes__
        )
        return f"<{self.__class__.__name__} {attrs}>"

    @property
    def row(self) -> int | None:
        """Gets or sets the row position of this item within its parent view.

        The row position determines the vertical placement of the item in the UI.
        The value must be an integer between 0 and 39 (inclusive), or ``None`` to indicate
        that no specific row is set.

        Returns
        -------
        Optional[:class:`int`]
            The row position of the item, or ``None`` if not explicitly set.

        Raises
        ------
        ValueError
            If the row value is not ``None`` and is outside the range [0, 39].
        """
        return self._row

    @row.setter
    def row(self, value: int | None):
        if value is None:
            self._row = None
        elif 39 > value >= 0:
            self._row = value
        else:
            raise ValueError("row cannot be negative or greater than or equal to 39")

    @property
    def width(self) -> int:
        """Gets the width of the item in the UI layout.

        The width determines how much horizontal space this item occupies within its row.

        Returns
        -------
        :class:`int`
            The width of the item. Defaults to 1.
        """
        return 1

    @property
    def id(self) -> int | None:
        """Gets this item's ID.

        This can be set by the user when constructing an Item. If not, Discord will automatically provide one when the View is sent.

        Returns
        -------
        Optional[:class:`int`]
            The ID of this item, or ``None`` if the user didn't set one.
        """
        return self._underlying and self._underlying.id

    @id.setter
    def id(self, value) -> None:
        if not self._underlying:
            return
        self._underlying.id = value

    @property
    def view(self) -> V | None:
        """Gets the parent view associated with this item.

        The view refers to the container that holds this item. This is typically set
        automatically when the item is added to a view.

        Returns
        -------
        Optional[:class:`View`]
            The parent view of this item, or ``None`` if the item is not attached to any view.
        """
        return self._view

    async def callback(self, interaction: Interaction):
        """|coro|

        The callback associated with this UI item.

        This can be overridden by subclasses.

        Parameters
        ----------
        interaction: :class:`.Interaction`
            The interaction that triggered this UI item.
        """
