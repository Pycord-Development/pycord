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

        self._underlying: CheckboxComponent = CheckboxComponent._raw_construct(
            type=ComponentType.checkbox,
            custom_id=custom_id,
            default=default,
            id=id,
        )
        self._value: bool | None = None

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
    def default(self) -> bool:
        """Whether this checkbox is selected by default or not. Defaults to ``False``"""
        return self._underlying.default

    @default.setter
    def default(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"default must be bool, not {value.__class__.__name__}")  # type: ignore
        self._underlying.default = bool(value)

    @property
    def value(self) -> str | None:
        """Whether this checkbox was selected or not by the user."""
        return self._value

    def to_component_dict(self) -> CheckboxComponentPayload:
        return self._underlying.to_dict()

    def refresh_state(self, data) -> None:
        self._value = data.get("value", None)

    def refresh_from_modal(
        self, interaction: Interaction, data: CheckboxComponentPayload
    ) -> None:
        return self.refresh_state(data)
