from __future__ import annotations

import asyncio
import os
import sys
from itertools import groupby
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from .input_text import InputText

__all__ = (
    "Modal",
    "ModalStore",
)


if TYPE_CHECKING:
    from ..interactions import Interaction
    from ..state import ConnectionState


class Modal:
    """Represents a UI Modal dialog.

    This object must be inherited to create a UI within Discord.

    .. versionadded:: 2.0

    Parameters
    ----------
    title: :class:`str`
        The title of the modal dialog.
        Must be 45 characters or fewer.
    custom_id: Optional[:class:`str`] = None
        The ID of the modal dialog that gets received during an interaction.
    """

    def __init__(self, title: str, custom_id: Optional[str] = None) -> None:
        if not (isinstance(custom_id, str) or custom_id is None):
            raise TypeError(f"expected custom_id to be str, not {custom_id.__class__.__name__}")

        self.custom_id = custom_id or os.urandom(16).hex()
        self.title = title
        self.children: List[InputText] = []
        self.__weights = _ModalWeights(self.children)
        loop = asyncio.get_running_loop()
        self._stopped: asyncio.Future[bool] = loop.create_future()

    async def callback(self, interaction: Interaction):
        """|coro|
        The coroutine that is called when the modal dialog is submitted.
        Should be overridden to handle the values submitted by the user.

        Parameters
        -----------
        interaction: :class:`~discord.Interaction`
            The interaction that submitted the modal dialog.
        """
        self.stop()

    def to_components(self) -> List[Dict[str, Any]]:
        def key(item: InputText) -> int:
            return item._rendered_row or 0

        children = sorted(self.children, key=key)
        components: List[Dict[str, Any]] = []
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

    def add_item(self, item: InputText):
        """Adds an InputText component to the modal dialog.

        Parameters
        ----------
        item: :class:`InputText`
            The item to add to the modal dialog
        """

        if len(self.children) > 5:
            raise ValueError("You can only have up to 5 items in a modal dialog.")

        if not isinstance(item, InputText):
            raise TypeError(f"expected InputText not {item.__class__!r}")

        self.__weights.add_item(item)
        self.children.append(item)

    def remove_item(self, item: InputText):
        """Removes an InputText component from the modal dialog.

        Parameters
        ----------
        item: :class:`InputText`
            The item to remove from the modal dialog.
        """
        try:
            self.children.remove(item)
        except ValueError:
            pass

    def stop(self) -> None:
        """Stops listening to interaction events from the modal dialog."""
        if not self._stopped.done():
            self._stopped.set_result(True)

    async def wait(self) -> bool:
        """Waits for the modal dialog to be submitted."""
        return await self._stopped

    def to_dict(self):
        return {
            "title": self.title,
            "custom_id": self.custom_id,
            "components": self.to_components(),
        }


class _ModalWeights:
    __slots__ = ("weights",)

    def __init__(self, children: List[InputText]):
        self.weights: List[int] = [0, 0, 0, 0, 0]

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
                raise ValueError(f"item would not fit at row {item.row} ({total} > 5 width)")
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
        self._modals: Dict[Tuple[int, str], Modal] = {}
        self._state: ConnectionState = state

    def add_modal(self, modal: Modal, user_id: int):
        self._modals[(user_id, modal.custom_id)] = modal

    def remove_modal(self, modal: Modal, user_id):
        self._modals.pop((user_id, modal.custom_id))

    async def dispatch(self, user_id: int, custom_id: str, interaction: Interaction):
        key = (user_id, custom_id)
        value = self._modals.get(key)
        if value is None:
            return

        components = [
            component
            for parent_component in interaction.data["components"]
            for component in parent_component["components"]
        ]
        for component in components:
            for child in value.children:
                if child.custom_id == component["custom_id"]:  # type: ignore
                    child.refresh_state(component)
                    break
        await value.callback(interaction)
        self.remove_modal(value, user_id)
