from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..components import RadioGroup as RadioGroupComponent
from ..components import RadioGroupOption
from ..enums import ComponentType
from .item import ModalItem

__all__ = ("RadioGroup",)

if TYPE_CHECKING:
    from ..interactions import Interaction
    from ..types.components import RadioGroupComponent as RadioGroupComponentPayload


class RadioGroup(ModalItem):
    """Represents a UI Radio Group component.

    .. versionadded:: 2.7.1

    Parameters
    ----------
    custom_id: Optional[:class:`str`]
        The ID of the radio group that gets received during an interaction.
    options: List[:class:`discord.RadioGroupOption`]
        A list of options that can be selected from this group.
    required: Optional[:class:`bool`]
        Whether an option selection is required or not. Defaults to ``True``.
    id: Optional[:class:`int`]
        The radio group's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "options",
        "required",
        "custom_id",
        "id",
    )

    def __init__(
        self,
        *,
        custom_id: str | None = None,
        options: list[RadioGroupOption] | None = None,
        required: bool = True,
        id: int | None = None,
    ):
        super().__init__()
        if custom_id is not None and not isinstance(custom_id, str):
            raise TypeError(
                f"expected custom_id to be str, not {custom_id.__class__.__name__}"
            )
        if not isinstance(required, bool):
            raise TypeError(f"required must be bool not {required.__class__.__name__}")  # type: ignore
        custom_id = os.urandom(16).hex() if custom_id is None else custom_id

        self._underlying: RadioGroupComponent = RadioGroupComponent._raw_construct(
            type=ComponentType.radio_group,
            custom_id=custom_id,
            options=options or [],
            required=required,
            id=id,
        )
        self._selected_value: str | None = None

    def __repr__(self) -> str:
        attrs = " ".join(
            f"{key}={getattr(self, key)!r}" for key in self.__item_repr_attributes__
        )
        return f"<{self.__class__.__name__} {attrs}>"

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def id(self) -> int | None:
        """The ID of this component. If not provided by the user, it is set sequentially by Discord."""
        return self._underlying.id

    @property
    def custom_id(self) -> str:
        """The custom id that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str):
        if not isinstance(value, str):
            raise TypeError(
                f"custom_id must be None or str not {value.__class__.__name__}"
            )
        self._underlying.custom_id = value

    @property
    def required(self) -> bool:
        """Whether an option selection is required or not. Defaults to ``True``"""
        return self._underlying.required

    @required.setter
    def required(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"required must be bool, not {value.__class__.__name__}")  # type: ignore
        self._underlying.required = bool(value)

    @property
    def value(self) -> str | None:
        """The value selected by the user."""
        return self._selected_value

    def to_component_dict(self) -> RadioGroupComponentPayload:
        return self._underlying.to_dict()

    def refresh_state(self, data) -> None:
        self._selected_value = data.get("value", None)

    def refresh_from_modal(
        self, interaction: Interaction, data: RadioGroupComponentPayload
    ) -> None:
        return self.refresh_state(data)
