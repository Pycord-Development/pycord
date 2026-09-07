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

from typing import Literal, NotRequired, TypedDict

from .snowflake import Snowflake
from .user import User

ApplicationStatus = Literal[
    "STARTED",  # started, but not yet submitted
    "SUBMITTED",  # submitted, but not yet reviewed
    "APPROVED",
    "REJECTED",
]
FormFieldType = Literal[
    "TERMS",
    "TEXT_INPUT",
    "PARAGRAPH",
    "MULTIPLE_CHOICE",
]


class JoinRequest(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    application_status: ApplicationStatus | None
    created_at: str  # iso
    reviewed_at: str | None  # iso
    reviewed_by_user: NotRequired[User]
    rejection_reason: str | None
    user_id: Snowflake
    user: NotRequired[User]
    form_responses: NotRequired[list[FormResponse]]
    actioned_by_user: NotRequired[User]


class _BaseFormResponse(TypedDict):
    field_type: FormFieldType


class TermsFormResponse(_BaseFormResponse):
    field_type: Literal["TERMS"]
    values: list[str]
    response: NotRequired[bool]


class TextInputFormResponse(_BaseFormResponse):
    field_type: Literal["TEXT_INPUT"]
    placeholder: NotRequired[str]
    response: NotRequired[str]


class ParagraphFormResponse(TextInputFormResponse): ...


class MultipleChoiceFormResponse(_BaseFormResponse):
    field_type: Literal["MULTIPLE_CHOICE"]
    choices: list[str]
    response: NotRequired[int]


FormResponse = (
    TermsFormResponse
    | TextInputFormResponse
    | ParagraphFormResponse
    | MultipleChoiceFormResponse
)


class _BaseListJoinRequests(TypedDict):
    total: NotRequired[int]  # only when status is "SUBMITTED" or omitted


# only returned with the kick_member permission
class ListJoinRequestsWithPermissions(_BaseListJoinRequests):
    guild_join_requests: list[JoinRequest]


ListJoinRequests = ListJoinRequestsWithPermissions | _BaseListJoinRequests


class JoinRequestCreate(TypedDict):
    guild_id: Snowflake
    status: ApplicationStatus
    request: JoinRequest


class JoinRequestUpdate(TypedDict):
    guild_id: Snowflake
    status: ApplicationStatus
    request: JoinRequest


class JoinRequestDelete(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    user_id: Snowflake
