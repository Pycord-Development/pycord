from __future__ import annotations

import asyncio
import os
import sys
import time
from functools import partial
from itertools import groupby
from typing import TYPE_CHECKING, Any, Callable, TypeVar, Union

from ..enums import ComponentType
from ..utils import find
from .core import ComponentUI
from .input_text import InputText
from .item import Item
from .label import Label
from .select import Select
from .text_display import TextDisplay

__all__ = (
    "BaseModal",
    "Modal",
    "DesignerModal",
    "ModalStore",
)


if TYPE_CHECKING:
    from typing_extensions import Self

    from ..interactions import Interaction
    from ..state import ConnectionState

M = TypeVar("M", bound="Modal", covariant=True)

ModalItem = Union[Item[M]]


class BaseModal(ComponentUI):
    """Represents a UI modal.

    This object must be inherited to create a UI within Discord.

    .. versionadded:: 2.7

    Parameters
    ----------
    children: Union[:class:`Item`]
        The initial items that are displayed in the modal.
    title: :class:`str`
        The title of the modal.
        Must be 45 characters or fewer.
    custom_id: Optional[:class:`str`]
        The ID of the modal that gets received during an interaction.
        Must be 100 characters or fewer.
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "title",
        "children",
        "timeout",
    )

    def __init__(
        self,
        *children: ModalItem,
        title: str,
        custom_id: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._children: list[ModalItem] = list(children)
        if not isinstance(custom_id, str) and custom_id is not None:
            raise TypeError(
                f"expected custom_id to be str, not {custom_id.__class__.__name__}"
            )
        self._custom_id: str | None = custom_id or os.urandom(16).hex()
        if len(title) > 45:
            raise ValueError("title must be 45 characters or fewer")
        super().__init__(*children, timeout=timeout)
        self._title = title
        self._weights = _ModalWeights(self._children)
        self.loop = asyncio.get_event_loop()

    def __repr__(self) -> str:
        attrs = " ".join(
            f"{key}={getattr(self, key)!r}" for key in self.__item_repr_attributes__
        )
        return f"<{self.__class__.__name__} {attrs}>"

    def _start_listening_from_store(self, store: ModalStore) -> None:
        self.__cancel_callback = partial(store.remove_modal)
        if self.timeout:
            loop = asyncio.get_running_loop()
            if self.__timeout_task is not None:
                self.__timeout_task.cancel()

            self.__timeout_expiry = time.monotonic() + self.timeout
            self.__timeout_task = loop.create_task(self.__timeout_task_impl())

    def _dispatch_timeout(self):
        if self._stopped.done():
            return

        self._stopped.set_result(True)
        self.loop.create_task(
            self.on_timeout(), name=f"discord-ui-view-timeout-{self.custom_id}"
        )

    @property
    def title(self) -> str:
        """The title of the modal."""
        return self._title

    @title.setter
    def title(self, value: str):
        if len(value) > 45:
            raise ValueError("title must be 45 characters or fewer")
        if not isinstance(value, str):
            raise TypeError(f"expected title to be str, not {value.__class__.__name__}")
        self._title = value

    @property
    def children(self) -> list[ModalItem]:
        """The child components associated with the modal."""
        return self._children

    @children.setter
    def children(self, value: list[ModalItem]):
        for item in value:
            if not isinstance(item, (InputText, Item)):
                raise TypeError(
                    "all Modal children must be InputText or Item, not"
                    f" {item.__class__.__name__}"
                )
        self._children = value

    @property
    def custom_id(self) -> str:
        """The ID of the modal that gets received during an interaction."""
        return self._custom_id

    @custom_id.setter
    def custom_id(self, value: str):
        if not isinstance(value, str):
            raise TypeError(
                f"expected custom_id to be str, not {value.__class__.__name__}"
            )
        if len(value) > 100:
            raise ValueError("custom_id must be 100 characters or fewer")
        self._custom_id = value

    async def callback(self, interaction: Interaction):
        """|coro|

        The coroutine that is called when the modal is submitted.
        Should be overridden to handle the values submitted by the user.

        Parameters
        ----------
        interaction: :class:`~discord.Interaction`
            The interaction that submitted the modal.
        """
        self.stop()

    def add_item(self, item: ModalItem) -> Self:
        """Adds a component to the modal.

        Parameters
        ----------
        item: Union[class:`InputText`, :class:`Item`]
            The item to add to the modal 
        """

        if len(self._children) > 5:
            raise ValueError("You can only have up to 5 items in a modal.")

        if not isinstance(item, (Item, )):
            raise TypeError(f"expected Item, not {item.__class__!r}")

        self._children.append(item)
        return self

    def remove_item(self, item: ModalItem) -> Self:
        """Removes a component from the modal.

        Parameters
        ----------
        item: Union[class:`InputText`, :class:`Item`]
            The item to remove from the modal.
        """
        try:
            self._children.remove(item)
        except ValueError:
            pass
        return self

    def stop(self) -> None:
        """Stops listening to interaction events from the modal."""
        if not self._stopped.done():
            self._stopped.set_result(True)
        self.__timeout_expiry = None
        if self.__timeout_task is not None:
            self.__timeout_task.cancel()
            self.__timeout_task = None

    async def wait(self) -> bool:
        """Waits for the modal to be submitted."""
        return await self._stopped

    def to_dict(self):
        return {
            "title": self.title,
            "custom_id": self.custom_id,
            "components": self.to_components(),
        }

    async def on_error(self, error: Exception, interaction: Interaction) -> None:
        """|coro|

        A callback that is called when the modal's callback fails with an error.

        The default implementation prints the traceback to stderr.

        Parameters
        ----------
        error: :class:`Exception`
            The exception that was raised.
        interaction: :class:`~discord.Interaction`
            The interaction that led to the failure.
        """
        interaction.client.dispatch("modal_error", error, interaction)

    async def on_timeout(self) -> None:
        """|coro|

        A callback that is called when a modal's timeout elapses without being explicitly stopped.
        """

class Modal(BaseModal):
    """Represents a UI modal for InputText components.

    This object must be inherited to create a UI within Discord.

    .. versionadded:: 2.0

    .. versionchanged:: 2.7

        Now inherits from :class:`BaseModal`

    Parameters
    ----------
    children: Union[:class:`InputText`]
        The initial items that are displayed in the modal. Only supports :class:`discord.ui.InputText`; for newer modal features, see :class:`DesignerModal`.
    title: :class:`str`
        The title of the modal.
        Must be 45 characters or fewer.
    custom_id: Optional[:class:`str`]
        The ID of the modal that gets received during an interaction.
        Must be 100 characters or fewer.
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.
    """

    def __init__(
        self,
        *children: ModalItem,
        title: str,
        custom_id: str | None = None,
        timeout: float | None = None,
    ) -> None:
        super().__init__(*children, title=title, custom_id=custom_id, timeout=timeout)
        self._weights = _ModalWeights(self._children)

    @children.setter
    def children(self, value: list[ModalItem]):
        for item in value:
            if not isinstance(item, InputText):
                raise TypeError(
                    "all Modal children must be InputText, not"
                    f" {item.__class__.__name__}"
                )
        self._weights = _ModalWeights(self._children)
        self._children = value

    def to_components(self) -> list[dict[str, Any]]:
        def key(item: InputText) -> int:
            return item._rendered_row or 0

        children = sorted(self._children, key=key)
        components: list[dict[str, Any]] = []
        for _, group in groupby(children, key=key):
            children = [item.to_component_dict() for item in group]
            if not children:
                continue

            components.append(
                {
                    "type": 1,
                    "components": children,
                }
            )

        return components

    def add_item(self, item: InputText) -> Self:
        """Adds an InputText component to the modal.

        Parameters
        ----------
        item: :class:`InputText`
            The item to add to the modal
        """

        if not isinstance(item, InputText):
            raise TypeError(f"expected InputText not {item.__class__!r}")

        self._weights.add_item(item)
        super().add_item(item)
        return self

    def remove_item(self, item: ModalItem) -> Self:
        """Removes a component from the modal.

        Parameters
        ----------
        item: Union[class:`InputText`, :class:`Item`]
            The item to remove from the modal.
        """

        super().remove_item(item)
        try:
            self.__weights.remove_item(item)
        except ValueError:
            pass
        return self

class DesignerModal(BaseModal):
    """Represents a UI modal compatible with all modal features.

    This object must be inherited to create a UI within Discord.

    .. versionadded:: 2.7

    Parameters
    ----------
    children: Union[:class:`Item`]
        The initial items that are displayed in the modal..
    title: :class:`str`
        The title of the modal.
        Must be 45 characters or fewer.
    custom_id: Optional[:class:`str`]
        The ID of the modal that gets received during an interaction.
        Must be 100 characters or fewer.
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.
    """

    def __init__(
        self,
        *children: ModalItem,
        title: str,
        custom_id: str | None = None,
        timeout: float | None = None,
    ) -> None:
        super().__init__(*children, title=title, custom_id=custom_id, timeout=timeout)

    @children.setter
    def children(self, value: list[ModalItem]):
        for item in value:
            if not isinstance(item, Item):
                raise TypeError(
                    "all DesignerModal children must be Item, not"
                    f" {item.__class__.__name__}"
                )
        self._children = value

    def add_item(self, item: ModalItem) -> Self:
        """Adds a component to the modal.

        Parameters
        ----------
        item: Union[:class:`Item`]
            The item to add to the modal
        """

        if isinstance(item, (InputText, )):
            raise TypeError(f"DesignerModal does not accept InputText directly. Use Label instead.")

        super().add_item(item)
        return self


class _ModalWeights:
    __slots__ = ("weights",)

    def __init__(self, children: list[InputText]):
        self.weights: list[int] = [0, 0, 0, 0, 0]

        key = lambda i: sys.maxsize if i.row is None else i.row
        children = sorted(children, key=key)
        for row, group in groupby(children, key=key):
            for item in group:
                self.add_item(item)

    def find_open_space(self, item: InputText) -> int:
        for index, weight in enumerate(self.weights):
            if weight + item.width <= 5:
                return index

        raise ValueError("could not find open space for item")

    def add_item(self, item: InputText) -> None:
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

    def remove_item(self, item: InputText) -> None:
        if item._rendered_row is not None:
            self.weights[item._rendered_row] -= item.width
            item._rendered_row = None

    def clear(self) -> None:
        self.weights = [0, 0, 0, 0, 0]


class ModalStore:
    def __init__(self, state: ConnectionState) -> None:
        # (user_id, custom_id) : Modal
        self._modals: dict[tuple[int, str], BaseModal] = {}
        self._state: ConnectionState = state

    def add_modal(self, modal: BaseModal, user_id: int):
        self._modals[(user_id, modal.custom_id)] = modal
        modal._start_listening_from_store(self)

    def remove_modal(self, modal: BaseModal, user_id):
        modal.stop()
        self._modals.pop((user_id, modal.custom_id))

    async def dispatch(self, user_id: int, custom_id: str, interaction: Interaction):
        key = (user_id, custom_id)
        value = self._modals.get(key)
        if value is None:
            return
        interaction.modal = value

        try:
            components = [
                component
                for parent_component in interaction.data["components"]
                for component in (
                    parent_component.get("components")
                    or (
                        [parent_component.get("component")]
                        if parent_component.get("component")
                        else [parent_component]
                    )
                )
            ]
            for component, child in zip(components, value.children):
                child.refresh_from_modal(interaction, component)
            await value.callback(interaction)
            self.remove_modal(value, user_id)
        except Exception as e:
            return await value.on_error(e, interaction)
