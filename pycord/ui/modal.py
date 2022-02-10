from __future__ import annotations

import os
from itertools import groupby
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from .input_text import InputText
from .view import _ViewWeights

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
    """

    def __init__(self, title: str, custom_id: Optional[str] = None) -> None:
        self.custom_id = custom_id or os.urandom(16).hex()
        self.title = title
        self.children: List[InputText] = []
        self.__weights = _ViewWeights(self.children)

    async def callback(self, interaction: Interaction):
        """|coro|
        The coroutine that is called when the modal dialog is submitted.
        Should be overridden to handle the values submitted by the user.

        Parameters
        -----------
        interaction: :class:`~discord.Interaction`
            The interaction that submitted the modal dialog.
        """
        pass

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
        else:
            self.__weights.remove_item(item)

    def to_dict(self):
        return {
            "title": self.title,
            "custom_id": self.custom_id,
            "components": self.to_components(),
        }


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
