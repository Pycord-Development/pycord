from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional, TypeVar

from ..components import InputText as InputTextComponent
from ..enums import InputTextStyle
from ..utils import MISSING
from .item import Item

__all__ = ("InputText",)

if TYPE_CHECKING:
    from ..types.components import InputText as InputTextComponentPayload

V = TypeVar("V", bound="View", covariant=True)


class InputText(Item[V]):
    """Represents a UI text input field.

    Parameters
    ----------
    style: :class:`discord.InputTextStyle`
        The style of the input text field.
    custom_id: Optional[:class:`str`]
        The ID of the input text field that gets received during an interaction.
    label: Optional[:class:`str`]
        The label for the input text field, if any.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    min_length: Optional[:class:`int`]
        The minimum number of characters that must be entered
        Defaults to 0
    max_length: Optional[:class:`int`]
        The maximum number of characters that can be entered
    required: Optional[:class:`bool`]
        Whether the input text field is required or not. Defaults to `True`.
    value: Optional[:class:`str`]
        Pre-fills the input text field with this value
    row: Optional[:class:`int`]
        The relative row this button belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """

    def __init__(
        self,
        style: InputTextStyle = InputTextStyle.short,
        custom_id: str = MISSING,
        label: Optional[str] = None,
        placeholder: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        required: Optional[bool] = True,
        value: Optional[str] = None,
        row: Optional[int] = None,
    ):
        super().__init__()
        custom_id = os.urandom(16).hex() if custom_id is MISSING else custom_id
        self._underlying = InputTextComponent._raw_construct(
            style=style,
            custom_id=custom_id,
            label=label,
            placeholder=placeholder,
            min_length=min_length,
            max_length=max_length,
            required=required,
            value=value,
        )
        self._input_value = None
        self.row = row

    @property
    def style(self) -> InputTextStyle:
        """:class:`discord.InputTextStyle`: The style of the input text field."""
        return self._underlying.style

    @style.setter
    def style(self, value: InputTextStyle):
        if not isinstance(value, InputTextStyle):
            raise TypeError("style must be of type InputTextStyle")
        self._underlying.style = value

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the input text field that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str):
        if not isinstance(value, str):
            raise TypeError("custom_id must be None or str")
        self._underlying.custom_id = value

    @property
    def placeholder(self) -> Optional[str]:
        """Optional[:class:`str`]: The placeholder text that is shown before anything is entered, if any."""
        return self._underlying.placeholder

    @placeholder.setter
    def placeholder(self, value: Optional[str]):
        if value and not isinstance(value, str):
            raise TypeError("placeholder must be None or str")
        self._underlying.placeholder = value

    @property
    def min_length(self) -> Optional[int]:
        """Optional[:class:`int`]: The minimum number of characters that must be entered. Defaults to `0`."""
        return self._underlying.min_length

    @min_length.setter
    def min_length(self, value: Optional[int]):
        if value and not isinstance(value, int):
            raise TypeError("min_length must be None or int")
        self._underlying.min_length = value

    @property
    def max_length(self) -> Optional[int]:
        """Optional[:class:`int`]: The maximum number of characters that can be entered."""
        return self._underlying.max_length

    @max_length.setter
    def max_length(self, value: Optional[int]):
        if value and not isinstance(value, int):
            raise TypeError("min_length must be None or int")
        self._underlying.max_length = value

    @property
    def required(self) -> Optional[bool]:
        """Optional[:class:`bool`]: Whether the input text field is required or not. Defaults to `True`."""
        return self._underlying.required

    @required.setter
    def required(self, value: Optional[bool]):
        if not isinstance(value, bool):
            raise TypeError("required must be bool")

    @property
    def value(self) -> Optional[str]:
        """Optionan[:class:`str`]: Pre-fills the input text field with this value."""
        return self._underlying.value

    @value.setter
    def value(self, value: Optional[str]):
        if value and not isinstance(value, str):
            raise TypeError("value must be None or str")
        self._underlying.value = value

    def to_component_dict(self) -> InputTextComponentPayload:
        return self._underlying.to_dict()

    def refresh_state(self, data) -> None:
        self._input_value = data["value"]
