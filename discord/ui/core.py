"""
The MIT License (MIT)

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
import time
from itertools import groupby
from typing import TYPE_CHECKING, Any, Callable

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

__all__ = "ComponentUI"


if TYPE_CHECKING:
    from typing_extensions import Self

    from ..interactions import Interaction, InteractionMessage
    from ..message import Message
    from ..state import ConnectionState
    from ..types.components import Component as ComponentPayload


class ComponentUI:
    """The base structure for classes that contain :class:`~discord.ui.Item`.

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`Item`
        The initial items contained in this structure.
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the UI before no longer accepting input. Defaults to 180.0.
        If ``None`` then there is no timeout.

    Attributes
    ----------
    timeout: Optional[:class:`float`]
        Timeout from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.
    children: List[:class:`Item`]
        The list of children attached to this structure.
    """

    def __init__(
        self,
        *items: Item,
        timeout: float | None = 180.0,
    ):
        self.timeout = timeout
        self.children: list[Item] = []
        for item in items:
            self.add_item(item)

        loop = asyncio.get_running_loop()
        self.__cancel_callback: Callable[[View], None] | None = None
        self.__timeout_expiry: float | None = None
        self.__timeout_task: asyncio.Task[None] | None = None
        self.__stopped: asyncio.Future[bool] = loop.create_future()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} timeout={self.timeout} children={len(self.children)}>"

    async def __timeout_task_impl(self) -> None:
        while True:
            # Guard just in case someone changes the value of the timeout at runtime
            if self.timeout is None:
                return

            if self.__timeout_expiry is None:
                return self._dispatch_timeout()

            # Check if we've elapsed our currently set timeout
            now = time.monotonic()
            if now >= self.__timeout_expiry:
                return self._dispatch_timeout()

            # Wait N seconds to see if timeout data has been refreshed
            await asyncio.sleep(self.__timeout_expiry - now)

    @property
    def _expires_at(self) -> float | None:
        if self.timeout:
            return time.monotonic() + self.timeout
        return None

    def _dispatch_timeout(self):
        raise NotImplementedError

    def to_components(self) -> list[dict[str, Any]]:
        return [item.to_component_dict() for item in self.children]

    def get_item(self, custom_id: str | int) -> Item | None:
        """Gets an item from this structure. Roughly equal to `utils.get(self.children, ...)`.
        If an :class:`int` is provided, the item will be retrieved by ``id``, otherwise by  ``custom_id``.
        This method will also search nested items.

        Parameters
        ----------
        custom_id: Union[:class:`str`, :class:`int`]
            The id of the item to get

        Returns
        -------
        Optional[:class:`Item`]
            The item with the matching ``custom_id`` or ``id`` if it exists.
        """
        if not custom_id:
            return None
        attr = "id" if isinstance(custom_id, int) else "custom_id"
        child = find(lambda i: getattr(i, attr, None) == custom_id, self.children)
        if not child:
            for i in self.children:
                if hasattr(i, "get_item"):
                    if child := i.get_item(custom_id):
                        return child
        return child

    def add_item(self, item: Item) -> Self:
        raise NotImplementedError

    def remove_item(self, item: Item) -> Self:
        raise NotImplementedError

    def clear_items(self) -> None:
        raise NotImplementedError

    async def on_timeout(self) -> None:
        """|coro|

        A callback that is called when this structure's timeout elapses without being explicitly stopped.
        """
