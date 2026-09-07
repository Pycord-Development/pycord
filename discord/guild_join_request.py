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
from typing import TYPE_CHECKING, Literal, overload

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
    from .abc import Snowflake
    from .guild import Guild
    from .state import ConnectionState
    from .types.guild_join_request import FormResponse as FormResponsePayload
    from .types.guild_join_request import JoinRequest as JoinRequestPayload
    from .user import User


class PartialJoinRequest(Hashable):
    """Represents a partial guild join request.

    .. versionadded:: 2.9

    Attributes
    ----------
    id: :class:`int`
        The ID of the join request application.
    guild_id: :class:`int`
        The ID of the guild the join request belongs to.
    guild: :class:`discord.Guild`
        The guild the join request belongs to.
    application_status: :class:`JoinRequestStatus`
        The status of the join request application.
    """

    __slots__ = ("_state", "application_status", "guild", "guild_id", "id")

    def __init__(
        self,
        *,
        guild: Snowflake | Guild | int,
        request: JoinRequest | Snowflake | int,
        state: ConnectionState,
        application_status: JoinRequestStatus | str | None = None,
    ) -> None:
        self._state: ConnectionState = state

        self.id: int = request.id if not isinstance(request, int) else request
        self.guild_id: int = guild.id if not isinstance(guild, int) else guild

        self.application_status: JoinRequestStatus | None = (
            try_enum(JoinRequestStatus, application_status)
            if not isinstance(application_status, JoinRequestStatus)
            else application_status
        )

    @property
    def guild(self) -> Guild | None:
        """Optional[:class:`discord.Guild`]: The guild the join request belongs to.

        This will be :data:`None` if the guild is not found in the internal cache.
        """
        return self._state._get_guild(self.guild_id)

    @overload
    async def take_action(
        self, action: Literal[JoinRequestAction.APPROVE]
    ) -> JoinRequest: ...

    @overload
    async def take_action(
        self,
        action: Literal[JoinRequestAction.REJECT],
        *,
        rejection_reason: str | None = ...,
    ) -> JoinRequest: ...

    @overload
    async def take_action(
        self, action: JoinRequestAction, *, rejection_reason: str | None = ...
    ) -> JoinRequest: ...

    async def take_action(
        self, action: JoinRequestAction, *, rejection_reason: str | None = None
    ) -> JoinRequest:
        """|coro|

        Take action on this join request application.

        You can only take action on a join request if the status is :attr:`JoinRequestStatus.SUBMITTED`.
        If :attr:`PartialJoinRequest.application_status` is available and not :attr:`JoinRequestStatus.SUBMITTED`,
        this will raise :exc:`ValueError`.

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
        if (
            self.application_status
            and self.application_status is not JoinRequestStatus.SUBMITTED
        ):
            raise ValueError(
                f"Cannot take action on a join request with status {self.application_status}."
            )
        data = await self._state.http.action_guild_join_request(
            self.guild_id,
            self.id,
            action=action.value,
            rejection_reason=rejection_reason,
        )
        return JoinRequest(state=self._state, data=data)


class JoinRequest(PartialJoinRequest):
    __slots__ = (
        "actioned_by",
        "created_at",
        "form_responses",
        "rejection_reason",
        "reviewed_at",
        "status",
        "user",
        "user_id",
    )

    """Represents a guild join request.

    .. versionadded:: 2.9

    Attributes
    ----------
    id: :class:`int`
        The join request ID.
    guild_id: :class:`int`
        The ID of the guild the join request belongs to.
    guild: :class:`discord.Guild`
        The guild the join request belongs to.
    user_id: :class:`int`
        The ID of the user who made the join request.
    user: :class:`discord.User`
        The user who made the join request.
    created_at: :class:`datetime.datetime`
        When the join request was created.
    reviewed_at: :class:`datetime.datetime` | :data:`None`
        When the join request was reviewed, if applicable.
    application_status: :class:`JoinRequestStatus` | :data:`None`
        The status of the application, if applicable.
    rejection_reason: :class:`str` | :data:`None`
        The reason the join request was rejected, if applicable.
    form_responses: list[:class:`discord.FormResponse`]
        The form responses of the join request, if applicable.
    actioned_by: :class:`discord.User` | :data:`None`
        The user who actioned the join request, if applicable.
    """

    def __init__(self, *, state: ConnectionState, data: JoinRequestPayload) -> None:
        super().__init__(
            guild=int(data["guild_id"]),
            request=int(data["id"]),
            application_status=data.get("application_status"),
            state=state,
        )

        self.created_at: datetime.datetime = utils.parse_time(data["created_at"])
        self.reviewed_at: datetime.datetime | None = utils.parse_time(
            data.get("reviewed_at")
        )
        self.rejection_reason: str | None = data.get("rejection_reason")

        user = data.get("user")
        self.user: User | None = (
            self._state.create_user(user) if user is not None else None
        )
        self.user_id: int = int(data["user_id"])

        form_responses = data.get("form_responses", [])
        self.form_responses: list[FormResponse] = [
            FormResponse(r) for r in form_responses
        ]

        actioned_by_user = data.get("actioned_by_user")
        self.actioned_by: User | None = (
            self._state.create_user(actioned_by_user)
            if actioned_by_user is not None
            else None
        )

    @classmethod
    def partial(
        cls,
        *,
        guild: Guild,
        request: JoinRequest | Snowflake | int,
    ) -> PartialJoinRequest:
        """Creates a partial join request object.

        This is useful for creating a join request object when you only have the guild and request ID.
        This will return a :class:`PartialJoinRequest` object, which can only be used to take action on
        the join request.

        Parameters
        ----------
        guild: :class:`discord.Guild`
            The guild the join request belongs to.
        request: :class:`discord.Snowflake` | :class:`discord.JoinRequest` | :class:`int`
            The join request to create a partial object for.

            If a :class:`discord.abc.Snowflake` or :class:`discord.JoinRequest` is provided,
            the ID will be extracted from it.

        Returns
        -------
        :class:`PartialJoinRequest`
            The partial join request object.
        """
        return PartialJoinRequest(guild=guild, request=request, state=guild._state)


class FormResponse:
    """Represents a form response for a guild join request.

    .. versionadded:: 2.9
        If the join request has already been approved or rejected, this will raise :exc:`ValueError`.

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
        - If the `field_type` is :attr:`JoinRequestFormFieldType.MULTIPLE_CHOICE`, this will be an :class:`str` representing the selected choice by the applicant.
            Also see :attr:`choice_index` for the index of the selected choice.
        - If the `field_type` is :attr:`JoinRequestFormFieldType.TERMS`, this will be a :class:`bool` indicating whether the applicant agreed to the terms.
    placeholder: Optional[:class:`str`]
        The placeholder text for the form field shown in empty text boxes.

        Only set if the `field_type` is :attr:`JoinRequestFormFieldType.TEXT_INPUT` or :attr:`JoinRequestFormFieldType.PARAGRAPH`.
    choices: Optional[List[:class:`str`]]
        The choices the applicant can select from.

        Only set if the `field_type` is :attr:`JoinRequestFormFieldType.MULTIPLE_CHOICE`.
    choice_index: :class:`int` | :data:`None`:
        The index of the selected choice for multiple choice form fields. Only set if the `field_type` is
        :attr:`JoinRequestFormFieldType.MULTIPLE_CHOICE`.
    """

    def __init__(self, data: FormResponsePayload) -> None:
        self.field_type: JoinRequestFormFieldType = try_enum(
            JoinRequestFormFieldType, data["field_type"]
        )
        self.label: str | None = data.get("label")
        self.description: str | None = data.get("description")
        self.required: bool = data.get("required", False)

        self.values: list[str] | None = data.get("values")
        self.placeholder: str | None = data.get("placeholder")

        self.choices: list[str] | None = data.get("choices")
        self.choice_index: int | None = None

        self.response: str | bool | None = None

        response: str | int | bool | None = data.get("response")
        if (
            self.field_type is JoinRequestFormFieldType.MULTIPLE_CHOICE
            and isinstance(response, int)
            and self.choices is not None
            and 0 <= response < len(self.choices)
        ):
            self.choice_index = response
            self.response = self.choices[self.choice_index]
