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
from operator import attrgetter
from typing import TYPE_CHECKING, Any, Callable

from ..utils import find, get
from .item import Item, ItemCallbackType

__all__ = ("ItemInterface",)


if TYPE_CHECKING:
    from typing_extensions import Self

    from .view import View


class ItemInterface:
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
    store: Optional[:class:`bool`]
        Whether this interface should be stored for callback listening. Setting it to ``False`` will ignore callbacks and prevent item values from being refreshed. Defaults to ``True``.
    """

    def __init__(
        self,
        *items: Item,
        timeout: float | None = 180.0,
        store: bool = True,
    ):
        self.timeout: float | None = timeout
        self.children: list[Item] = []
        for item in items:
            self.add_item(item)

        loop = asyncio.get_running_loop()
        self._cancel_callback: Callable[[View], None] | None = None
        self._timeout_expiry: float | None = None
        self._timeout_task: asyncio.Task[None] | None = None
        self._stopped: asyncio.Future[bool] = loop.create_future()
        self._store = store

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} timeout={self.timeout} children={len(self.children)}>"

    async def _timeout_task_impl(self) -> None:
        while True:
            # Guard just in case someone changes the value of the timeout at runtime
            if self.timeout is None:
                return

            if self._timeout_expiry is None:
                return self._dispatch_timeout()

            # Check if we've elapsed our currently set timeout
            now = time.monotonic()
            if now >= self._timeout_expiry:
                return self._dispatch_timeout()

            # Wait N seconds to see if timeout data has been refreshed
            await asyncio.sleep(self._timeout_expiry - now)

    @property
    def _expires_at(self) -> float | None:
        if self.timeout:
            return time.monotonic() + self.timeout
        return None

    def _dispatch_timeout(self):
        raise NotImplementedError

    def to_components(self) -> list[dict[str, Any]]:
        return [item.to_component_dict() for item in self.children]

    def get_item(self, custom_id: str | int | None = None, **attrs: Any) -> Item | None:
        r"""Gets an item from this structure. Roughly equal to `utils.get(self.children, **attrs)`.
        If an :class:`int` is provided, the item will be retrieved by ``id``, otherwise by  ``custom_id``.
        This method will also search nested items.
        If ``attrs`` are provided, it will check them by logical AND as done in :func:`~utils.get`.
        To have a nested attribute search (i.e. search by ``x.y``) then pass in ``x__y`` as the keyword argument.

        Examples
        ---------

        Basic usage:

        .. code-block:: python3

            container = my_view.get(1234)

        Attribute matching:

        .. code-block:: python3

            button = my_view.get(label='Click me!', style=discord.ButtonStyle.danger)

        Parameters
        ----------
        custom_id: Optional[Union[:class:`str`, :class:`int`]]
            The id of the item to get
        \*\*attrs
            Keyword arguments that denote attributes to search with.

        Returns
        -------
        Optional[:class:`Item`]
            The item with the matching ``custom_id``, ``id``, or ``attrs`` if it exists.
        """
        if not (custom_id or attrs):
            return None
        child = None
        if custom_id:
            attr = "id" if isinstance(custom_id, int) else "custom_id"
            child = find(lambda i: getattr(i, attr, None) == custom_id, self.children)
            if not child:
                for i in self.children:
                    if hasattr(i, "get_item"):
                        if child := i.get_item(custom_id):
                            return child
        elif attrs:
            _all = all
            attrget = attrgetter
            for i in self.children:
                converted = [
                    (attrget(attr.replace("__", ".")), value)
                    for attr, value in attrs.items()
                ]
                try:
                    if _all(pred(i) == value for pred, value in converted):
                        return i
                except:
                    pass
                if hasattr(i, "get_item"):
                    if child := i.get_item(custom_id, **attrs):
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
