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

from typing_extensions import Self

from ..components import CheckboxGroup as CheckboxGroupComponent
from ..components import CheckboxGroupOption
from ..enums import ComponentType
from ..utils import MISSING
from .item import ModalItem

__all__ = ("CheckboxGroup",)

if TYPE_CHECKING:
    from ..interactions import Interaction
    from ..types.components import (
        CheckboxGroupComponent as CheckboxGroupComponentPayload,
    )


class CheckboxGroup(ModalItem):
    """Represents a UI Checkbox Group component.

    .. versionadded:: 2.7.1

    Parameters
    ----------
    custom_id: Optional[:class:`str`]
        The ID of the checkbox group that gets received during an interaction.
    options: List[:class:`discord.CheckboxGroupOption`]
        A list of options that can be selected in this group.
    min_values: Optional[:class:`int`]
        The minimum number of options that must be selected.
        Defaults to 0 and must be between 0 and 10, inclusive.
    max_values: Optional[:class:`int`]
        The maximum number of options that can be selected.
        Must be between 1 and 10, inclusive.
    required: Optional[:class:`bool`]
        Whether an option selection is required or not. Defaults to ``True``.
    id: Optional[:class:`int`]
        The checkbox group's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "options",
        "required",
        "min_values",
        "max_values",
        "custom_id",
        "id",
    )

    def __init__(
        self,
        *,
        custom_id: str | None = None,
        options: list[CheckboxGroupOption] | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        required: bool = True,
        id: int | None = None,
    ):
        super().__init__()
        if min_values and (min_values < 0 or min_values > 10):
            raise ValueError("min_values must be between 0 and 10")
        if max_values and (max_values < 1 or max_values > 10):
            raise ValueError("max_values must be between 1 and 10")
        if custom_id is not None and not isinstance(custom_id, str):
            raise TypeError(
                f"expected custom_id to be str, not {custom_id.__class__.__name__}"
            )
        if not isinstance(required, bool):
            raise TypeError(f"required must be bool not {required.__class__.__name__}")  # type: ignore
        custom_id = os.urandom(16).hex() if custom_id is None else custom_id
        self._selected_values: list[str] = []

        self._underlying: CheckboxGroupComponent = self._generate_underlying(
            custom_id=custom_id,
            options=options or [],
            min_values=min_values,
            max_values=max_values,
            required=required,
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
        options: list[CheckboxGroupOption] | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        required: bool | None = None,
        id: int | None = None,
    ) -> CheckboxGroupComponent:
        super()._generate_underlying(CheckboxGroupComponent)
        return CheckboxGroupComponent._raw_construct(
            type=ComponentType.checkbox_group,
            custom_id=custom_id or self.custom_id,
            options=options if options is not None else self.options,
            min_values=min_values if min_values is not None else self.min_values,
            max_values=max_values if max_values is not None else self.max_values,
            required=required if required is not None else self.required,
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
    def min_values(self) -> int | None:
        """The minimum number of options that must be selected."""
        return self.underlying.min_values

    @min_values.setter
    def min_values(self, value: int | None):
        if value and not isinstance(value, int):
            raise TypeError(f"min_values must be None or int not {value.__class__.__name__}")  # type: ignore
        if value and (value < 0 or value > 10):
            raise ValueError("min_values must be between 0 and 10")
        self.underlying.min_values = value

    @property
    def max_values(self) -> int | None:
        """The maximum number of options that can be selected."""
        return self.underlying.max_values

    @max_values.setter
    def max_values(self, value: int | None):
        if value and not isinstance(value, int):
            raise TypeError(f"max_values must be None or int not {value.__class__.__name__}")  # type: ignore
        if value and (value < 1 or value > 10):
            raise ValueError("max_values must be between 1 and 10")
        self.underlying.max_values = value

    @property
    def required(self) -> bool:
        """Whether an option selection is required or not. Defaults to ``True``"""
        return self.underlying.required

    @required.setter
    def required(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"required must be bool, not {value.__class__.__name__}")  # type: ignore
        self.underlying.required = bool(value)

    @property
    def values(self) -> list[str]:
        """The values selected by the user."""
        return self._selected_values

    @property
    def options(self) -> list[CheckboxGroupOption]:
        """A list of options that can be selected in this group."""
        return self.underlying.options

    @options.setter
    def options(self, value: list[CheckboxGroupOption]):
        if not isinstance(value, list):
            raise TypeError("options must be a list of CheckboxGroupOption")
        if len(value) > 10:
            raise ValueError("you may only provide up to 10 options.")
        if not all(isinstance(obj, CheckboxGroupOption) for obj in value):
            raise TypeError("all list items must subclass CheckboxGroupOption")

        self.underlying.options = value

    def add_option(
        self,
        *,
        label: str,
        value: str = MISSING,
        description: str | None = None,
        default: bool = False,
    ) -> Self:
        """Adds an option to the checkbox group.

        To append a pre-existing :class:`discord.CheckboxGroupOption` use the
        :meth:`append_option` method instead.

        Parameters
        ----------
        label: :class:`str`
            The label of the option. This is displayed to users.
            Can only be up to 100 characters.
        value: :class:`str`
            The value of the option. This is not displayed to users.
            If not given, defaults to the label. Can only be up to 100 characters.
        description: Optional[:class:`str`]
            An additional description of the option, if any.
            Can only be up to 100 characters.
        default: :class:`bool`
            Whether this option is selected by default.

        Raises
        ------
        ValueError
            The number of options exceeds 10.
        """

        option = CheckboxGroupOption(
            label=label,
            value=value,
            description=description,
            default=default,
        )

        return self.append_option(option)

    def append_option(self, option: CheckboxGroupOption) -> Self:
        """Appends an option to the checkbox group.

        Parameters
        ----------
        option: :class:`discord.CheckboxGroupOption`
            The option to append to the checkbox group.

        Raises
        ------
        ValueError
            The number of options exceeds 10.
        """

        if len(self.underlying.options) >= 10:
            raise ValueError("maximum number of options already provided")

        self.underlying.options.append(option)
        return self

    def to_component_dict(self) -> CheckboxGroupComponentPayload:
        return self.underlying.to_dict()

    def refresh_state(self, data) -> None:
        self._selected_values = data.get("values", [])

    def refresh_from_modal(
        self, interaction: Interaction, data: CheckboxGroupComponentPayload
    ) -> None:
        return self.refresh_state(data)
