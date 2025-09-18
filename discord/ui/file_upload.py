from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ..components import FileUpload as FileUploadComponent
from ..enums import ComponentType
from ..message import Attachment

__all__ = ("FileUpload",)

if TYPE_CHECKING:
    from ..interactions import Interaction
    from ..types.components import FileUploadComponent as FileUploadComponentPayload


class FileUpload:
    """Represents a UI file upload field.

    .. versionadded:: 2.7

    Parameters
    ----------
    custom_id: Optional[:class:`str`]
        The ID of the input text field that gets received during an interaction.
    label: :class:`str`
        The label for the file upload field.
        Must be 45 characters or fewer.
    description: Optional[:class:`str`]
        The description for the file upload field.
        Must be 100 characters or fewer.
    min_values: Optional[:class:`int`]
        The minimum number of files that must be uploaded.
        Defaults to 0 and must be between 0 and 10, inclusive.
    max_values: Optional[:class:`int`]
        The maximum number of files that can be uploaded.
        Must be between 1 and 10, inclusive.
    required: Optional[:class:`bool`]
        Whether the file upload field is required or not. Defaults to ``True``.
    row: Optional[:class:`int`]
        The relative row this file upload field belongs to. A modal dialog can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "label",
        "required",
        "min_values",
        "max_values",
        "custom_id",
        "id",
        "description",
    )

    def __init__(
        self,
        *,
        custom_id: str | None = None,
        label: str,
        min_values: int | None = None,
        max_values: int | None = None,
        required: bool | None = True,
        row: int | None = None,
        id: int | None = None,
        description: str | None = None,
    ):
        super().__init__()
        if len(str(label)) > 45:
            raise ValueError("label must be 45 characters or fewer")
        if description and len(description) > 100:
            raise ValueError("description must be 100 characters or fewer")
        if min_values and (min_values < 0 or min_values > 10):
            raise ValueError("min_values must be between 0 and 10")
        if max_values and (max_values < 1 or max_values > 10):
            raise ValueError("max_length must be between 1 and 10")
        if not isinstance(custom_id, str) and custom_id is not None:
            raise TypeError(
                f"expected custom_id to be str, not {custom_id.__class__.__name__}"
            )
        custom_id = os.urandom(16).hex() if custom_id is None else custom_id
        self.label: str = str(label)
        self.description: str | None = description

        self._underlying: FileUploadComponent = FileUploadComponent._raw_construct(
            type=ComponentType.file_upload,
            custom_id=custom_id,
            min_values=min_values,
            max_values=max_values,
            required=required,
            id=id,
        )
        self._interaction: Interaction | None = None
        self._values: list[str] | None = None
        self.row = row
        self._rendered_row: int | None = None

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
        """The file upload's ID. If not provided by the user, it is set sequentially by Discord."""
        return self._underlying.id

    @property
    def custom_id(self) -> str:
        """The ID of the file upload field that gets received during an interaction."""
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
        """The minimum number of files that must be uploaded. Defaults to 0."""
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
    def required(self) -> bool | None:
        """Whether the input file upload is required or not. Defaults to ``True``."""
        return self._underlying.required

    @required.setter
    def required(self, value: bool | None):
        if not isinstance(value, bool):
            raise TypeError(f"required must be bool not {value.__class__.__name__}")  # type: ignore
        self._underlying.required = bool(value)

    @property
    def values(self) -> list[Attachment] | None:
        """The files that were uploaded to the field."""
        if self._interaction is None:
            return None
        attachments = []
        for attachment_id in self._values:
            attachment_data = self._interaction.data["resolved"]["attachments"][
                attachment_id
            ]
            attachments.append(
                Attachment(state=self._interaction._state, data=attachment_data)
            )
        return attachments

    @property
    def width(self) -> int:
        return 5

    def to_component_dict(self) -> FileUploadComponentPayload:
        return self._underlying.to_dict()

    def refresh_from_modal(self, interaction: Interaction, data: dict) -> None:
        self._interaction = interaction
        self._values = data.get("values", [])

    @staticmethod
    def uses_label() -> bool:
        return True
