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
import sys
import time
from functools import partial
from itertools import groupby
from typing import TYPE_CHECKING, Any, ClassVar, Iterator, Sequence, TypeVar

from typing_extensions import Self

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
from ..utils import find
from .core import ItemInterface
from .item import ItemCallbackType, ViewItem

__all__ = (
    "BaseView",
    "View",
    "DesignerView",
    "_component_to_item",
    "_walk_all_components",
)


if TYPE_CHECKING:
    from ..interactions import Interaction, InteractionMessage
    from ..message import Message
    from ..state import ConnectionState
    from ..types.components import Component as ComponentPayload

V = TypeVar("V", bound="BaseView", covariant=True)


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


def _component_to_item(component: Component) -> ViewItem[V]:

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
    if isinstance(component, ActionRowComponent):
        from .action_row import ActionRow

        return ActionRow.from_component(component)
    if isinstance(component, LabelComponent):
        from .label import Label

        return Label.from_component(component)
    return ViewItem.from_component(component)


class _ViewWeights:
    __slots__ = ("weights",)

    def __init__(self, children: list[ViewItem[V]]):
        self.weights: list[int] = [0, 0, 0, 0, 0]

        key = lambda i: sys.maxsize if i.row is None else i.row
        children = sorted(children, key=key)
        for row, group in groupby(children, key=key):
            for item in group:
                self.add_item(item)

    def find_open_space(self, item: ViewItem[V]) -> int:
        for index, weight in enumerate(self.weights):
            # check if open space AND (next row has no items OR this is the last row)
            if (weight + item.width <= 5) and (
                (index < len(self.weights) - 1 and self.weights[index + 1] == 0)
                or index == len(self.weights) - 1
            ):
                return index

        raise ValueError("could not find open space for item")

    def add_item(self, item: ViewItem[V]) -> None:
        if item.row is not None:
            total = self.weights[item.row] + item.width
            if total > 5:
                raise ValueError(
                    f"item would not fit at row {item.row} ({total} > 5 width)"
                )
            self.weights[item.row] = total
            item._rendered_row = item.row
        else:
            index = self.find_open_space(item)
            self.weights[index] += item.width
            item._rendered_row = index

    def remove_item(self, item: ViewItem[V]) -> None:
        if item._rendered_row is not None:
            self.weights[item._rendered_row] -= item.width
            item._rendered_row = None

    def clear(self) -> None:
        self.weights = [0, 0, 0, 0, 0]


class BaseView(ItemInterface):
    """The base class for UI views used in messages.

    .. versionadded:: 2.7
    """

    __discord_ui_view__: ClassVar[bool] = True
    MAX_ITEMS: int

    def __init__(
        self,
        *items: ViewItem[V],
        timeout: float | None = 180.0,
        disable_on_timeout: bool = False,
        store: bool = True,
    ):
        super().__init__(*items, timeout=timeout, store=store)
        self.disable_on_timeout = disable_on_timeout
        self.id: str = os.urandom(16).hex()
        self._message: Message | InteractionMessage | None = None
        self.parent: Interaction | None = None

    def add_item(self, item: ViewItem[V]) -> Self:
        """Adds an item to the view.

        Parameters
        ----------
        item: :class:`ViewItem`
            The item to add to the view.

        Raises
        ------
        TypeError
            An :class:`ViewItem` was not passed.
        ValueError
            Maximum number of children has been exceeded
        """

        if len(self.children) >= self.MAX_ITEMS:
            raise ValueError("maximum number of children exceeded")

        if not isinstance(item, ViewItem):
            raise TypeError(f"expected ViewItem not {item.__class__!r}")

        item.parent = self
        item._view = self
        self.children.append(item)
        return self

    def remove_item(self, item: ViewItem[V] | int | str) -> None:
        """Removes an item from the view. If an :class:`int` or :class:`str` is passed,
        the item will be removed by ViewItem ``id`` or ``custom_id`` respectively.

        Parameters
        ----------
        item: Union[:class:`ViewItem`, :class:`int`, :class:`str`]
            The item, item ``id``, or item ``custom_id`` to remove from the view.
        """

        if isinstance(item, (str, int)):
            item = self.get_item(item)
        try:
            if isinstance(item.parent, BaseView):
                self.children.remove(item)
            else:
                item.parent.remove_item(item)
        except ValueError:
            pass
        return self

    def clear_items(self) -> None:
        """Removes all items from this view."""
        self.children.clear()
        return self

    async def interaction_check(self, interaction: Interaction) -> bool:
        """|coro|

        A callback that is called when an interaction happens within the view
        that checks whether the view should process item callbacks for the interaction.

        This is useful to override if, for example, you want to ensure that the
        interaction author is a given user.

        The default implementation of this returns ``True``.

        If this returns ``False``, :meth:`on_check_failure` is called.

        .. note::

            If an exception occurs within the body then the check
            is considered a failure and :meth:`on_error` is called.

        Parameters
        ----------
        interaction: :class:`~discord.Interaction`
            The interaction that occurred.

        Returns
        -------
        :class:`bool`
            Whether the view children's callbacks should be called.
        """
        return True

    async def on_timeout(self) -> None:
        """|coro|

        A callback that is called when a view's timeout elapses without being explicitly stopped.
        """
        if self.disable_on_timeout:
            self.disable_all_items()

            if not self._message or self._message.flags.ephemeral:
                message = self.parent
            else:
                message = self.message

            if message:
                m = await message.edit(view=self)
                if m:
                    self._message = m

    async def on_check_failure(self, interaction: Interaction) -> None:
        """|coro|
        A callback that is called when a :meth:`BaseView.interaction_check` returns ``False``.
        This can be used to send a response when a check failure occurs.

        Parameters
        ----------
        interaction: :class:`~discord.Interaction`
            The interaction that occurred.
        """

    async def on_error(
        self, error: Exception, item: ViewItem[V], interaction: Interaction
    ) -> None:
        """|coro|

        A callback that is called when an item's callback or :meth:`interaction_check`
        fails with an error.

        The default implementation prints the traceback to stderr.

        Parameters
        ----------
        error: :class:`Exception`
            The exception that was raised.
        item: :class:`ViewItem`
            The item that failed the dispatch.
        interaction: :class:`~discord.Interaction`
            The interaction that led to the failure.
        """
        interaction.client.dispatch("view_error", error, item, interaction)

    def is_components_v2(self) -> bool:
        """Whether the view contains V2 components.

        A view containing V2 components cannot be sent alongside message content or embeds.
        """
        return any([item._underlying.is_v2() for item in self.children])

    async def _scheduled_task(self, item: ViewItem[V], interaction: Interaction):
        try:
            if self.timeout:
                self._timeout_expiry = time.monotonic() + self.timeout

            allow = await self.interaction_check(interaction)
            if not allow:
                return await self.on_check_failure(interaction)

            await item.callback(interaction)
        except Exception as e:
            return await self.on_error(e, item, interaction)

    def _start_listening_from_store(self, store: ViewStore) -> None:
        self._cancel_callback = partial(store.remove_view)
        if self.timeout:
            loop = asyncio.get_running_loop()
            if self._timeout_task is not None:
                self._timeout_task.cancel()

            self._timeout_expiry = time.monotonic() + self.timeout
            self._timeout_task = loop.create_task(self._timeout_task_impl())

    def _dispatch_timeout(self):
        if self._stopped.done():
            return

        self._stopped.set_result(True)
        asyncio.create_task(
            self.on_timeout(), name=f"discord-ui-view-timeout-{self.id}"
        )

    def _dispatch_item(self, item: ViewItem[V], interaction: Interaction):
        if self._stopped.done():
            return

        if interaction.message:
            self.message = interaction.message

        asyncio.create_task(
            self._scheduled_task(item, interaction),
            name=f"discord-ui-view-dispatch-{self.id}",
        )

    def is_finished(self) -> bool:
        """Whether the view has finished interacting."""
        return self._stopped.done()

    def is_dispatchable(self) -> bool:
        return any(item.is_dispatchable() for item in self.children)

    def is_dispatching(self) -> bool:
        """Whether the view has been added for dispatching purposes."""
        return self._cancel_callback is not None

    def is_persistent(self) -> bool:
        """Whether the view is set up as persistent.

        A persistent view has all their components with a set ``custom_id`` and
        a :attr:`timeout` set to ``None``.
        """
        return self.timeout is None and all(
            item.is_persistent() for item in self.children
        )

    def stop(self) -> None:
        """Stops listening to interaction events from this view.

        This operation cannot be undone.
        """
        if not self._stopped.done():
            self._stopped.set_result(False)

        self._timeout_expiry = None
        if self._timeout_task is not None:
            self._timeout_task.cancel()
            self._timeout_task = None

        if self._cancel_callback:
            self._cancel_callback(self)
            self._cancel_callback = None

    async def wait(self) -> bool:
        """Waits until the view has finished interacting.

        A view is considered finished when :meth:`stop`
        is called, or it times out.

        Returns
        -------
        :class:`bool`
            If ``True``, then the view timed out. If ``False`` then
            the view finished normally.
        """
        return await self._stopped

    def disable_all_items(self, *, exclusions: list[ViewItem[V]] | None = None) -> Self:
        """
        Disables all buttons and select menus in the view.

        Parameters
        ----------
        exclusions: Optional[List[:class:`ViewItem`]]
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

    def enable_all_items(self, *, exclusions: list[ViewItem[V]] | None = None) -> Self:
        """
        Enables all buttons and select menus in the view.

        Parameters
        ----------
        exclusions: Optional[List[:class:`ViewItem`]]
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

    def copy_text(self) -> str:
        """Returns the text of all :class:`~discord.ui.TextDisplay` items in this View.
        Equivalent to the `Copy Text` option on Discord clients.
        """
        return "\n".join(t for i in self.children if (t := i.copy_text()))

    def walk_children(self) -> Iterator[ViewItem]:
        for item in self.children:
            if hasattr(item, "walk_items"):
                yield from item.walk_items()
            else:
                yield item

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value


class View(BaseView):
    """Represents a legacy UI view for V1 components :class:`~discord.ui.Button` and :class:`~discord.ui.Select`.

    This object must be inherited to create a UI within Discord.

    .. versionadded:: 2.0

    .. versionchanged:: 2.7

        Now inherits from :class:`BaseView`

    Parameters
    ----------
    *items: :class:`ViewItem`
        The initial items attached to this view.
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the UI before no longer accepting input. Defaults to 180.0.
        If ``None`` then there is no timeout.

    Attributes
    ----------
    timeout: Optional[:class:`float`]
        Timeout from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.
    children: List[:class:`ViewItem`]
        The list of children attached to this view.
    disable_on_timeout: :class:`bool`
        Whether to disable the view when the timeout is reached. Defaults to ``False``.
    message: Optional[:class:`.Message`]
        The message that this view is attached to.
        If ``None`` then the view has not been sent with a message.
    parent: Optional[:class:`.Interaction`]
        The parent interaction which this view was sent from.
        If ``None`` then the view was not sent using :meth:`InteractionResponse.send_message`.
    store: Optional[:class:`bool`]
        Whether this view should be stored for callback listening. Setting it to ``False`` will ignore item callbacks and prevent their values from being refreshed. Defaults to ``True``.
    """

    __view_children_items__: ClassVar[list[ItemCallbackType]] = []
    MAX_ITEMS: int = 25

    def __init_subclass__(cls) -> None:
        children: list[ItemCallbackType] = []
        for base in reversed(cls.__mro__):
            for member in base.__dict__.values():
                if hasattr(member, "__discord_ui_model_type__"):
                    children.append(member)

        if len(children) > 40:
            raise TypeError("View cannot have more than 40 children")

        cls.__view_children_items__ = children

    def __init__(
        self,
        *items: ViewItem[V],
        timeout: float | None = 180.0,
        disable_on_timeout: bool = False,
        store: bool = True,
    ):
        super().__init__(
            timeout=timeout, disable_on_timeout=disable_on_timeout, store=store
        )

        for func in self.__view_children_items__:
            item: ViewItem[V] = func.__discord_ui_model_type__(
                **func.__discord_ui_model_kwargs__
            )
            item.callback = partial(func, self, item)
            item._view = self
            item.parent = self
            setattr(self, func.__name__, item)
            self.children.append(item)

        self.__weights = _ViewWeights(self.children)
        for item in items:
            self.add_item(item)

    def to_components(self) -> list[dict[str, Any]]:
        def key(item: ViewItem[V]) -> int:
            return item._rendered_row or 0

        children = sorted(self.children, key=key)
        components: list[dict[str, Any]] = []
        for _, group in groupby(children, key=key):
            items = list(group)
            children = [item.to_component_dict() for item in items]
            if not children:
                continue

            components.append(
                {
                    "type": 1,
                    "components": children,
                }
            )

        return components

    @classmethod
    def from_message(
        cls, message: Message, /, *, timeout: float | None = 180.0
    ) -> View:
        """Converts a message's components into a :class:`View`.

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
        view = View(timeout=timeout)
        for component in _walk_all_components(message.components):
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
        """Converts a list of component dicts into a :class:`View`.

        Parameters
        ----------
        data: List[:class:`.Component`]
            The list of components to convert into a view.
        timeout: Optional[:class:`float`]
            The timeout of the converted view.

        Returns
        -------
        :class:`View`
            The converted view. This always returns a :class:`View` and not
            one of its subclasses.
        """
        view = View(timeout=timeout)
        components = [_component_factory(d) for d in data]
        for component in _walk_all_components(components):
            view.add_item(_component_to_item(component))

    def add_item(self, item: ViewItem[V]) -> Self:
        """Adds an item to the view. Attempting to add a :class:`~discord.ui.ActionRow` will add its children instead.

        Parameters
        ----------
        item: :class:`ViewItem`
            The item to add to the view.

        Raises
        ------
        TypeError
            An :class:`ViewItem` was not passed.
        ValueError
            Maximum number of children has been exceeded (25)
            or the row the item is trying to be added to is full.
        """

        if item._underlying.is_v2():
            raise ValueError(
                f"cannot use V2 components in View. Use DesignerView instead."
            )
        if isinstance(item._underlying, ActionRowComponent):
            for i in item.children:
                self.add_item(i)
            return self

        super().add_item(item)
        self.__weights.add_item(item)
        return self

    def remove_item(self, item: ViewItem[V] | int | str) -> None:
        """Removes an item from the view. If an :class:`int` or :class:`str` is passed,
        the item will be removed by Item ``id`` or ``custom_id`` respectively.

        Parameters
        ----------
        item: Union[:class:`ViewItem`, :class:`int`, :class:`str`]
            The item, item ``id``, or item ``custom_id`` to remove from the view.
        """

        super().remove_item(item)
        try:
            self.__weights.remove_item(item)
        except ValueError:
            pass
        return self

    def clear_items(self) -> None:
        """Removes all items from the view."""
        super().clear_items()
        self.__weights.clear()
        return self

    def refresh(self, components: list[Component]):
        # This is pretty hacky at the moment
        old_state: dict[tuple[int, str], ViewItem[V]] = {
            (item.type.value, item.custom_id): item for item in self.children if item.is_dispatchable()  # type: ignore
        }
        children: list[ViewItem[V]] = [
            item for item in self.children if not item.is_dispatchable()
        ]
        for component in _walk_all_components(components):
            try:
                older = old_state[(component.type.value, component.custom_id)]  # type: ignore
            except (KeyError, AttributeError):
                item = _component_to_item(component)
                if not item.is_dispatchable():
                    continue
                children.append(item)
            else:
                older.refresh_component(component)
                children.append(older)

        self.children = children

    def is_components_v2(self) -> bool:
        """Whether the view contains V2 components.

        A view containing V2 components cannot be sent alongside message content or embeds.

        This is always ``False`` for :class:`View`.
        """
        return False


class DesignerView(BaseView):
    """Represents a UI view compatible with v2 components.

    This object must be inherited to create a UI within Discord.

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`ViewItem`
        The initial items attached to this view.
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the UI before no longer accepting input. Defaults to 180.0.
        If ``None`` then there is no timeout.

    Attributes
    ----------
    timeout: Optional[:class:`float`]
        Timeout from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.
    children: List[:class:`ViewItem`]
        The list of items attached to this view.
    disable_on_timeout: :class:`bool`
        Whether to disable the view's items when the timeout is reached. Defaults to ``False``.
    message: Optional[:class:`.Message`]
        The message that this view is attached to.
        If ``None`` then the view has not been sent with a message.
    parent: Optional[:class:`.Interaction`]
        The parent interaction which this view was sent from.
        If ``None`` then the view was not sent using :meth:`InteractionResponse.send_message`.
    store: Optional[:class:`bool`]
        Whether this view should be stored for callback listening. Setting it to ``False`` will ignore item callbacks and prevent their values from being refreshed. Defaults to ``True``.
    """

    MAX_ITEMS: int = 40

    def __init_subclass__(cls) -> None:
        for base in reversed(cls.__mro__):
            for member in base.__dict__.values():
                if hasattr(member, "__discord_ui_model_type__"):
                    raise ValueError(
                        "The @button and @select decorators are incompatible with DesignerView. Use ActionRow instead."
                    )

    def __init__(
        self,
        *items: ViewItem[V],
        timeout: float | None = 180.0,
        disable_on_timeout: bool = False,
        store: bool = True,
    ):
        super().__init__(
            *items, timeout=timeout, disable_on_timeout=disable_on_timeout, store=store
        )

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

    def add_item(self, item: ViewItem[V]) -> Self:
        """Adds an item to the view.

        Parameters
        ----------
        item: :class:`ViewItem`
            The item to add to the view.

        Raises
        ------
        TypeError
            An :class:`ViewItem` was not passed.
        ValueError
            Maximum number of items has been exceeded (40)
        """

        if isinstance(item._underlying, (SelectComponent, ButtonComponent)):
            raise ValueError(
                f"cannot add Select or Button to DesignerView directly. Use ActionRow instead."
            )

        super().add_item(item)
        if hasattr(item, "items"):
            item.view = self
        return self

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

    def is_components_v2(self) -> bool:
        return len(self.children) > 5 or super().is_components_v2()


class ViewStore:
    def __init__(self, state: ConnectionState):
        # (component_type, message_id, custom_id): (BaseView, ViewItem)
        self._views: dict[tuple[int, int | None, str], tuple[BaseView, ViewItem[V]]] = (
            {}
        )
        # message_id: View
        self._synced_message_views: dict[int, BaseView] = {}
        self._state: ConnectionState = state

    @property
    def persistent_views(self) -> Sequence[BaseView]:
        views = {
            view.id: view
            for (_, (view, _)) in self._views.items()
            if view.is_persistent()
        }
        return list(views.values())

    def __verify_integrity(self):
        to_remove: list[tuple[int, int | None, str]] = []
        for k, (view, _) in self._views.items():
            if view.is_finished():
                to_remove.append(k)

        for k in to_remove:
            del self._views[k]

    def add_view(self, view: BaseView, message_id: int | None = None):
        if not view._store:
            return
        self.__verify_integrity()

        view._start_listening_from_store(self)
        for item in view.walk_children():
            if item.is_storable():
                self._views[(item.type.value, message_id, item.custom_id)] = (view, item)  # type: ignore

        if message_id is not None:
            self._synced_message_views[message_id] = view

    def remove_view(self, view: BaseView):
        for item in view.walk_children():
            if item.is_storable():
                self._views.pop((item.type.value, item.custom_id), None)  # type: ignore

        for key, value in self._synced_message_views.items():
            if value.id == view.id:
                self.remove_message_view(key)
                break

    def remove_message_view(self, message_id)
        del self._synced_message_views[message_id]

    def dispatch(self, component_type: int, custom_id: str, interaction: Interaction):
        self.__verify_integrity()
        message_id: int | None = interaction.message and interaction.message.id
        key = (component_type, message_id, custom_id)
        # Fallback to None message_id searches in case a persistent view
        # was added without an associated message_id
        value = self._views.get(key) or self._views.get(
            (component_type, None, custom_id)
        )
        if value is None:
            return

        view, item = value
        interaction.view = view
        item.refresh_state(interaction)
        view._dispatch_item(item, interaction)

    def is_message_tracked(self, message_id: int):
        return message_id in self._synced_message_views

    def remove_message_tracking(self, message_id: int) -> BaseView | None:
        return self._synced_message_views.pop(message_id, None)

    def update_from_message(self, message_id: int, components: list[ComponentPayload]):
        # pre-req: is_message_tracked == true
        view = self._synced_message_views[message_id]
        components = [_component_factory(d, state=self._state) for d in components]
        view.refresh(components)
