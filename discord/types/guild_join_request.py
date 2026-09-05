from __future__ import annotations

from typing import Literal, NotRequired, TypedDict
from .snowflake import Snowflake
from .user import User

ApplicationStatus = Literal[
    "STARTED",  # started, but not yet submitted
    "SUBMITTED",  # submitted, but not yet reviewed
    "APPROVED",
    "DENIED",
]
FormFieldType = Literal[
    "TERMS",
    "TEXT_INPUT",
    "PARAGRAPH",
    "MULTIPLE_CHOICE",
]


class JoinRequest(TypedDict):
    id: Snowflake
    created_at: str  # iso
    reviewed_at: str | None  # iso
    application_status: ApplicationStatus | None
    rejection_status: str | None
    guild_id: Snowflake
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



class _BaseListGuildJoinRequests(TypedDict):
    total: NotRequired[int]  # only when status is "SUBMITTED" or omitted


# only returned with the kick_member permission
class ListGuildJoinRequestsWithPermissions(_BaseListGuildJoinRequests):
    guild_join_requests: list[JoinRequest]


ListGuildJoinRequests = (
    ListGuildJoinRequestsWithPermissions | _BaseListGuildJoinRequests
)


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
