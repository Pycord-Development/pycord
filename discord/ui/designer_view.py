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

import asyncio
import os
from itertools import groupby
from typing import TYPE_CHECKING, Any, Callable, Iterator, TypeVar

from ..components import ActionRow as ActionRowComponent
from ..components import Button as ButtonComponent
from ..components import Component
from ..components import Container as ContainerComponent
from ..components import FileComponent
from ..components import Label as LabelComponent
from ..components import MediaGallery as MediaGalleryComponent
from ..components import Section as SectionComponent
from ..components import SelectMenu as SelectComponent
from ..components import Separator as SeparatorComponent
from ..components import TextDisplay as TextDisplayComponent
from ..components import Thumbnail as ThumbnailComponent
from ..components import _component_factory
from ..utils import find, get
from .action_row import ActionRow
from .item import Item, ItemCallbackType
from .view import View

__all__ = ("DesignerView", "_component_to_item", "_walk_all_components")


if TYPE_CHECKING:
    from typing_extensions import Self

    from ..interactions import Interaction, InteractionMessage
    from ..message import Message
    from ..state import ConnectionState
    from ..types.components import Component as ComponentPayload

V = TypeVar("V", bound="DesignerView", covariant=True)


def _walk_all_components(components: list[Component]) -> Iterator[Component]:
    for item in components:
        if isinstance(item, ActionRowComponent):
            yield from item.children
        else:
            yield item


def _walk_all_components_v2(components: list[Component]) -> Iterator[Component]:
    for item in components:
        if isinstance(item, ActionRowComponent):
            yield from item.children
        elif isinstance(item, (SectionComponent, ContainerComponent)):
            yield from item.walk_components()
        else:
            yield item


def _component_to_item(component: Component) -> Item[V]:

    if isinstance(component, ActionRowComponent):

        return ActionRow.from_component(component)
    if isinstance(component, ButtonComponent):
        from .button import Button

        return Button.from_component(component)
    if isinstance(component, SelectComponent):
        from .select import Select

        return Select.from_component(component)
    if isinstance(component, SectionComponent):
        from .section import Section

        return Section.from_component(component)
    if isinstance(component, TextDisplayComponent):
        from .text_display import TextDisplay

        return TextDisplay.from_component(component)
    if isinstance(component, ThumbnailComponent):
        from .thumbnail import Thumbnail

        return Thumbnail.from_component(component)
    if isinstance(component, MediaGalleryComponent):
        from .media_gallery import MediaGallery

        return MediaGallery.from_component(component)
    if isinstance(component, FileComponent):
        from .file import File

        return File.from_component(component)
    if isinstance(component, SeparatorComponent):
        from .separator import Separator

        return Separator.from_component(component)
    if isinstance(component, ContainerComponent):
        from .container import Container

        return Container.from_component(component)
    return Item.from_component(component)


class DesignerView:
    """Represents a UI view for v2 components.

    This object must be inherited to create a UI within Discord.

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`Item`
        The initial items attached to this view.
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the UI before no longer accepting input. Defaults to 180.0.
        If ``None`` then there is no timeout.

    Attributes
    ----------
    timeout: Optional[:class:`float`]
        Timeout from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.
    children: List[:class:`Item`]
        The list of items attached to this view.
    disable_on_timeout: :class:`bool`
        Whether to disable the view's items when the timeout is reached. Defaults to ``False``.
    message: Optional[:class:`.Message`]
        The message that this view is attached to.
        If ``None`` then the view has not been sent with a message.
    parent: Optional[:class:`.Interaction`]
        The parent interaction which this view was sent from.
        If ``None`` then the view was not sent using :meth:`InteractionResponse.send_message`.
    """

    def __init__(
        self,
        *children: Item[V],
        timeout: float | None = 180.0,
        disable_on_timeout: bool = False,
    ):
        self.timeout = timeout
        self.disable_on_timeout = disable_on_timeout
        self.items: list[Item[V]] = []
        for item in children:
            self.add_item(item)

        loop = asyncio.get_running_loop()
        self.id: str = os.urandom(16).hex()
        self.__cancel_callback: Callable[[View], None] | None = None
        self.__timeout_expiry: float | None = None
        self.__timeout_task: asyncio.Task[None] | None = None
        self.__stopped: asyncio.Future[bool] = loop.create_future()
        self._message: Message | InteractionMessage | None = None
        self.parent: Interaction | None = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} timeout={self.timeout} children={len(self.children)}>"

    def to_components(self) -> list[dict[str, Any]]:
        return [item.to_component_dict() for item in self.children]

    @classmethod
    def from_message(
        cls, message: Message, /, *, timeout: float | None = 180.0
    ) -> View:
        """Converts a message's components into a :class:`DesignerView`.

        The :attr:`.Message.components` of a message are read-only
        and separate types from those in the ``discord.ui`` namespace.
        In order to modify and edit message components they must be
        converted into a :class:`View` first.

        Parameters
        ----------
        message: :class:`.Message`
            The message with components to convert into a view.
        timeout: Optional[:class:`float`]
            The timeout of the converted view.

        Returns
        -------
        :class:`View`
            The converted view. This always returns a :class:`View` and not
            one of its subclasses.
        """
        view = DesignerView(timeout=timeout)
        for component in message.components:
            view.add_item(_component_to_item(component))
        return view

    @classmethod
    def from_dict(
        cls,
        data: list[Component],
        /,
        *,
        timeout: float | None = 180.0,
    ) -> View:
        """Converts a list of component dicts into a :class:`DesignerView`.

        Parameters
        ----------
        data: List[:class:`.Component`]
            The list of components to convert into a view.
        timeout: Optional[:class:`float`]
            The timeout of the converted view.

        Returns
        -------
        :class:`DesignerView`
            The converted view. This always returns a :class:`View` and not
            one of its subclasses.
        """
        view = DesignerView(timeout=timeout)
        components = [_component_factory(d) for d in data]
        for component in components:
            view.add_item(_component_to_item(component))
        return view

    def add_item(self, item: Item[V]) -> Self:
        """Adds an item to the view.

        Parameters
        ----------
        item: :class:`Item`
            The item to add to the view.

        Raises
        ------
        TypeError
            An :class:`Item` was not passed.
        ValueError
            Maximum number of items has been exceeded (40)
        """

        if len(self.children) >= 40:
            raise ValueError("maximum number of children exceeded")

        if not isinstance(item, Item):
            raise TypeError(f"expected Item not {item.__class__!r}")

        if item.uses_label():
            raise ValueError(
                f"cannot use label, description or required on select menus in views."
            )

        item.parent = self
        item._view = self
        if hasattr(item, "items"):
            item.view = self
        self.children.append(item)
        return self

    def remove_item(self, item: Item[V] | int | str) -> Self:
        """Removes an item from the view. If an :class:`int` or :class:`str` is passed,
        the item will be removed by Item ``id`` or ``custom_id`` respectively.

        Parameters
        ----------
        item: Union[:class:`Item`, :class:`int`, :class:`str`]
            The item, item ``id``, or item ``custom_id`` to remove from the view.
        """

        if isinstance(item, (str, int)):
            item = self.get_item(item)
        try:
            item.parent.remove_item(item)
        except ValueError:
            pass
        return self

    def clear_items(self) -> None:
        """Removes all items from the view."""
        self.children.clear()
        return self

    def get_item(self, id: str | int) -> Item[V] | None:
        """Gets an item from the view. Roughly equal to `utils.get(view.children, ...)`.
        If an :class:`int` is provided, the item will be retrieved by ``id``, otherwise by  ``custom_id``.
        This method will also search nested items.

        Parameters
        ----------
        id: Union[:class:`str`, :class:`int`]
            The id of the item to get

        Returns
        -------
        Optional[:class:`Item`]
            The item with the matching ``custom_id`` or ``id`` if it exists.
        """
        if not id:
            return None
        attr = "id" if isinstance(id, int) else "custom_id"
        child = find(lambda i: getattr(i, attr, None) == id, self.children)
        if not child:
            for i in self.children:
                if hasattr(i, "get_item"):
                    if child := i.get_item(id):
                        return child
        return child

    __timeout_task_impl = View._View__timeout_task_impl
    _expires_at = View._expires_at
    _scheduled_task = View._scheduled_task
    _start_listening_from_store = View._start_listening_from_store
    _dispatch_timeout = View._dispatch_timeout
    _dispatch_item = View._dispatch_item
    stop = View.stop
    wait = View.wait
    is_finished = View.is_finished
    is_dispatching = View.is_dispatching
    interaction_check = View.interaction_check
    on_timeout = View.on_timeout
    on_check_failure = View.on_check_failure
    on_error = View.on_error

    def refresh(self, components: list[Component]):
        # Refreshes view data using discord's values
        # Assumes the components and items are identical
        if not components:
            return

        i = 0
        for c in components:
            try:
                item = self.children[i]
            except:
                break
            else:
                item.refresh_component(c)
                i += 1

    def is_dispatchable(self) -> bool:
        return any(item.is_dispatchable() for item in self.children)

    def is_persistent(self) -> bool:
        """Whether the view is set up as persistent.

        A persistent view has all buttons and selects with a set ``custom_id`` and
        a :attr:`timeout` set to ``None``.
        """
        return self.timeout is None and all(
            item.is_persistent() for item in self.children
        )

    def is_components_v2(self) -> bool:
        """Whether the view contains V2 components.

        A view containing V2 components cannot be sent alongside message content or embeds.
        This always returns ``True`` in :class:`DesignerView`, regardless of its :attr:`items`
        """
        return True

    def disable_all_items(self, *, exclusions: list[Item[V]] | None = None) -> None:
        """
        Disables all buttons and select menus in the view.

        Parameters
        ----------
        exclusions: Optional[List[:class:`Item`]]
            A list of items in `self.children` to not disable from the view.
        """
        for child in self.children:
            if hasattr(child, "disabled") and (
                exclusions is None or child not in exclusions
            ):
                child.disabled = True
            if hasattr(child, "disable_all_items"):
                child.disable_all_items(exclusions=exclusions)
        return self

    def enable_all_items(self, *, exclusions: list[Item[V]] | None = None) -> None:
        """
        Enables all buttons and select menus in the view.

        Parameters
        ----------
        exclusions: Optional[List[:class:`Item`]]
            A list of items in `self.children` to not enable from the view.
        """
        for child in self.children:
            if hasattr(child, "disabled") and (
                exclusions is None or child not in exclusions
            ):
                child.disabled = False
            if hasattr(child, "enable_all_items"):
                child.enable_all_items(exclusions=exclusions)
        return self

    def walk_children(self) -> Iterator[Item]:
        for item in self.children:
            if hasattr(item, "walk_items"):
                yield from item.walk_items()
            else:
                yield item

    def copy_text(self) -> str:
        """Returns the text of all :class:`~discord.ui.TextDisplay` items in this View.
        Equivalent to the `Copy Text` option on Discord clients.
        """
        return "\n".join(t for i in self.children if (t := i.copy_text()))

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value
