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

import os
from typing import TYPE_CHECKING

from ..components import Checkbox as CheckboxComponent
from ..enums import ComponentType
from .item import ModalItem

__all__ = ("Checkbox",)

if TYPE_CHECKING:
    from ..interactions import Interaction
    from ..types.components import CheckboxComponent as CheckboxComponentPayload


class Checkbox(ModalItem):
    """Represents a UI Checkbox component.

    .. versionadded:: 2.7.1

    Parameters
    ----------
    custom_id: Optional[:class:`str`]
        The ID of the checkbox that gets received during an interaction.
    default: Optional[:class:`bool`]
        Whether this checkbox is selected by default or not.
    id: Optional[:class:`int`]
        The checkbox's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "default",
        "custom_id",
        "id",
    )

    def __init__(
        self,
        *,
        custom_id: str | None = None,
        default: bool = False,
        id: int | None = None,
    ):
        super().__init__()
        if custom_id is not None and not isinstance(custom_id, str):
            raise TypeError(
                f"expected custom_id to be str, not {custom_id.__class__.__name__}"
            )
        if not isinstance(default, bool):
            raise TypeError(f"default must be bool, not {default.__class__.__name__}")  # type: ignore
        custom_id = os.urandom(16).hex() if custom_id is None else custom_id
        self._value: bool | None = None

        self._underlying: CheckboxComponent = self._generate_underlying(
            custom_id=custom_id,
            default=default,
            id=id,
        )

    def __repr__(self) -> str:
        attrs = " ".join(
            f"{key}={getattr(self, key)!r}" for key in self.__item_repr_attributes__
        )
        return f"<{self.__class__.__name__} {attrs}>"

    def _generate_underlying(
        self,
        custom_id: str | None = None,
        default: bool | None = None,
        id: int | None = None,
    ) -> CheckboxComponent:
        super()._generate_underlying(CheckboxComponent)
        return CheckboxComponent._raw_construct(
            type=ComponentType.checkbox,
            custom_id=custom_id or self.custom_id,
            required=default if default is not None else self.default,
            id=id or self.id,
        )

    @property
    def custom_id(self) -> str:
        """The custom id that gets received during an interaction."""
        return self.underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str):
        if not isinstance(value, str):
            raise TypeError(
                f"custom_id must be None or str not {value.__class__.__name__}"
            )
        if value and len(value) > 100:
            raise ValueError("custom_id must be 100 characters or fewer")
        self.underlying.custom_id = value

    @property
    def default(self) -> bool:
        """Whether this checkbox is selected by default or not. Defaults to ``False``"""
        return self.underlying.default

    @default.setter
    def default(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"default must be bool, not {value.__class__.__name__}")  # type: ignore
        self.underlying.default = bool(value)

    @property
    def value(self) -> bool | None:
        """Whether this checkbox was selected or not by the user. This will be ``None`` if the checkbox has not been submitted via a modal yet."""
        return self._value

    def to_component_dict(self) -> CheckboxComponentPayload:
        return self.underlying.to_dict()

    def refresh_state(self, data) -> None:
        self._value = data.get("value", None)

    def refresh_from_modal(
        self, interaction: Interaction, data: CheckboxComponentPayload
    ) -> None:
        return self.refresh_state(data)
