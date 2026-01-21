from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..components import FileUpload as FileUploadComponent
from ..enums import ComponentType
from ..message import Attachment
from .item import ModalItem

__all__ = ("FileUpload",)

if TYPE_CHECKING:
    from ..interactions import Interaction
    from ..types.components import FileUploadComponent as FileUploadComponentPayload


class FileUpload(ModalItem):
    """Represents a UI File Upload component.

    .. versionadded:: 2.7

    Parameters
    ----------
    custom_id: Optional[:class:`str`]
        The ID of the file upload field that gets received during an interaction.
    min_values: Optional[:class:`int`]
        The minimum number of files that must be uploaded.
        Defaults to 0 and must be between 0 and 10, inclusive.
    max_values: Optional[:class:`int`]
        The maximum number of files that can be uploaded.
        Must be between 1 and 10, inclusive.
    required: Optional[:class:`bool`]
        Whether the file upload field is required or not. Defaults to ``True``.
    id: Optional[:class:`int`]
        The file upload field's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
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

        self._underlying: FileUploadComponent = FileUploadComponent._raw_construct(
            type=ComponentType.file_upload,
            custom_id=custom_id,
            min_values=min_values,
            max_values=max_values,
            required=required,
            id=id,
        )
        self._attachments: list[Attachment] | None = None

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
    def min_values(self) -> int | None:
        """The minimum number of files that must be uploaded."""
        return self._underlying.min_values

    @min_values.setter
    def min_values(self, value: int | None):
        if value and not isinstance(value, int):
            raise TypeError(f"min_values must be None or int not {value.__class__.__name__}")  # type: ignore
        if value and (value < 0 or value > 10):
            raise ValueError("min_values must be between 0 and 10")
        self._underlying.min_values = value

    @property
    def max_values(self) -> int | None:
        """The maximum number of files that can be uploaded."""
        return self._underlying.max_values

    @max_values.setter
    def max_values(self, value: int | None):
        if value and not isinstance(value, int):
            raise TypeError(f"max_values must be None or int not {value.__class__.__name__}")  # type: ignore
        if value and (value < 1 or value > 10):
            raise ValueError("max_values must be between 1 and 10")
        self._underlying.max_values = value

    @property
    def required(self) -> bool:
        """Whether the input file upload is required or not. Defaults to ``True``."""
        return self._underlying.required

    @required.setter
    def required(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f"required must be bool not {value.__class__.__name__}")  # type: ignore
        self._underlying.required = bool(value)

    @property
    def values(self) -> list[Attachment] | None:
        """The files that were uploaded to the field."""
        return self._attachments

    def to_component_dict(self) -> FileUploadComponentPayload:
        return self._underlying.to_dict()

    def refresh_from_modal(self, interaction: Interaction, data: dict) -> None:
        values = data.get("values", [])
        self._attachments = [
            Attachment(
                state=interaction._state,
                data=interaction.data["resolved"]["attachments"][attachment_id],
            )
            for attachment_id in values
        ]
