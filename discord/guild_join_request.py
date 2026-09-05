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

import datetime
from typing import TYPE_CHECKING

from . import utils
from .enums import (
    JoinRequestAction,
    JoinRequestFormFieldType,
    JoinRequestStatus,
    try_enum,
)
from .mixins import Hashable

__all__ = ("FormResponse", "JoinRequest")

if TYPE_CHECKING:
    from .guild import Guild
    from .object import Object
    from .state import ConnectionState
    from .types.guild_join_request import FormResponse as FormResponsePayload
    from .types.guild_join_request import JoinRequest as JoinRequestPayload
    from .user import User


class FormResponse:
    """Represents a form response for a guild join request.

    .. versionadded:: 2.9

    Attributes
    ----------
    field_type: :class:`JoinRequestFormFieldType`
        The type of the form field.
    label: :class:`str` | :class:`None`
        The label of the form field, shown above the field.
    description: :class:`str` | :class:`None`
        The description of the form field, shown below the label.
    required: :class:`bool`
        Whether the form field is required to be filled out.
    values: Optional[List[:class:`str`]]
        The terms the applicant must agree to.

        Only set if the `field_type` is :attr:`JoinRequestFormFieldType.TERMS`.
    response: Optional[Union[:class:`str`, :class:`int`, :class:`bool`]]
        The response to the form field, depending on the `field_type`:

        - If the `field_type` is :attr:`JoinRequestFormFieldType.TEXT_INPUT` or :attr:`JoinRequestFormFieldType.PARAGRAPH`, this will be a :class:`str`.
        - If the `field_type` is :attr:`JoinRequestFormFieldType.MULTIPLE_CHOICE`, this will be an :class:`int` representing the index of the selected choice.
        - If the `field_type` is :attr:`JoinRequestFormFieldType.TERMS`, this will be a :class:`bool` indicating whether the applicant agreed to the terms.
    placeholder: Optional[:class:`str`]
        The placeholder text for the form field shown in empty text boxes.

        Only set if the `field_type` is :attr:`JoinRequestFormFieldType.TEXT_INPUT` or :attr:`JoinRequestFormFieldType.PARAGRAPH`.
    choices: Optional[List[:class:`str`]]
        The choices the applicant can select from.

        Only set if the `field_type` is :attr:`JoinRequestFormFieldType.MULTIPLE_CHOICE`.
    """

    def __init__(self, data: FormResponsePayload) -> None:
        self.field_type: JoinRequestFormFieldType = try_enum(
            JoinRequestFormFieldType, data["field_type"]
        )
        self.label: str | None = data.get("label")
        self.description: str | None = data.get("description")
        self.required: bool = data.get("required", False)

        self.values: list[str] | None = data.get("values")
        self.response: str | int | bool | None = data.get("response")
        self.placeholder: str | None = data.get("placeholder")
        self.choices: list[str] | None = data.get("choices")


class JoinRequest(Hashable):
    __slots__ = (
        "_state",
        "id",
        "guild",
        "guild_id",
        "user",
        "user_id",
        "created_at",
        "reviewed_at",
        "status",
        "rejection_status",
        "form_responses",
        "actioned_by_user",
    )

    """Represents a guild join request.

    .. versionadded:: 2.9

    Attributes
    ----------
    id: :class:`int`
        The join request ID.
    guild_id: :class:`int`
        The guild ID.
    user_id: :class:`int`
        The user ID of the requester.
    created_at: :class:`datetime.datetime`
        When the join request was created.
    reviewed_at: Optional[:class:`datetime.datetime`]
        When the join request was reviewed, if applicable.
    status: Optional[:class:`JoinRequestStatus`]
        The status of the application, if applicable.
    rejection_status: Optional[:class:`str`]
        The rejection status of the join request, if applicable.
    user: Optional[:class:`discord.User`]
        The user who made the join request. This is only available if the join request was fetched with the ``with_user`` parameter set to ``True``.
    form_responses: Optional[List[:class:`discord.FormResponse`]]
        The form responses of the join request, if applicable. This is only available if the join request was fetched with the ``with_form_responses`` parameter set to ``True``.
    actioned_by_user: Optional[:class:`discord.User`]
        The user who actioned the join request, if applicable. This is only available if the join request was fetched with the ``with_actioned_by_user`` parameter set to ``True``.
    """

    def __init__(
        self, *, guild: Guild, state: ConnectionState, data: JoinRequestPayload
    ) -> None:
        self._state: ConnectionState = state

        self.guild: Guild = guild
        self.guild_id: int = int(data["guild_id"])

        self.id: int = int(data["id"])
        self.created_at: datetime.datetime = utils.parse_time(data["created_at"])
        self.reviewed_at: datetime.datetime | None = utils.parse_time(
            data.get("reviewed_at")
        )

        status = data.get("status")
        self.status: JoinRequestStatus | None = (
            try_enum(JoinRequestStatus, status) if status is not None else None
        )
        self.rejection_status: str | None = data.get("rejection_status")

        user = data.get("user")
        self.user: User | None = state.create_user(user) if user is not None else None
        self.user_id: int = int(data["user_id"])

        form_responses = data.get("form_responses")
        self.form_responses: list[FormResponse] | None = (
            [FormResponse(r) for r in form_responses]
            if form_responses is not None
            else None
        )

        actioned_by_user = data.get("actioned_by_user")
        self.actioned_by_user: User | None = (
            state.create_user(actioned_by_user)
            if actioned_by_user is not None
            else None
        )

    @classmethod
    def partial(cls, *, guild: Guild, request_id: Object | int) -> JoinRequest:
        """Creates a partial join request object.

        This is useful for creating a join request object when you only have the guild and request ID.
        This can be only be used to take action on the join request, and will not have any other values available.

        Parameters
        ----------
        guild: :class:`discord.Guild`
            The guild the join request belongs to.
        request_id: :class:`discord.Object` | :class:`int`
            The ID of the join request.

            if a :class:`discord.Object` is provided, the ID will be extracted from it.

        Returns
        -------
        :class:`JoinRequest`
            The partial join request object.
        """
        data = {
            "id": request_id.id if not isinstance(request_id, int) else request_id,
            "guild_id": guild.id,
            "user_id": 0,  # Placeholder
            "created_at": utils.utcnow().isoformat(),
            "status": "SUBMITTED",
        }
        return cls(
            guild=guild,
            state=guild._state,
            data=data,  # type: ignore
        )

    async def take_action(
        self, action: JoinRequestAction, rejection_reason: str | None = None
    ) -> JoinRequest:
        """|coro|

        Takes action on this join request application.

        You can only take action on a join request if the status is :attr:`JoinRequestStatus.SUBMITTED`.
        If the join request has already been approved or denied, this will raise :exc:`ValueError`.

        This requires the :attr:`~Permissions.kick_members` permission.

        Parameters
        ----------
        action: :class:`JoinRequestAction`
            The action to take on the join request.
        rejection_reason: Optional[:class:`str`]
            The reason for rejecting the join request. This is optional and can be used to provide feedback to the user.

            Only applicable if the `action` is :attr:`JoinRequestAction.REJECT`.

        Returns
        -------
        :class:`JoinRequest`
            The updated join request.

        Raises
        ------
        ValueError
            The join request status is not :attr:`JoinRequestStatus.SUBMITTED`.
        Forbidden
            You do not have permission to take action on the join request.
            Or the `status` is not :attr:`JoinRequestStatus.SUBMITTED`.
        HTTPException
            Taking action on the join request failed.
        """
        if self.status is not JoinRequestStatus.SUBMITTED:
            raise ValueError(
                "You can only take action on a join request if the status is SUBMITTED."
            )
        data = await self._state.http.action_guild_join_request(
            self.guild_id,
            self.id,
            action=action.value,
            rejection_reason=rejection_reason,
        )
        return self.__class__(guild=self.guild, state=self._state, data=data)
