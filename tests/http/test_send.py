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

from typing import TYPE_CHECKING

import pytest

from discord import Route, utils
from discord.types import components, embed, message, sticker

from ..core import client
from .core import allowed_mentions, channel_id, components, content
from .core import embed as embed_
from .core import (
    embeds,
    message_id,
    message_ids,
    nonce,
    powerset,
    random_allowed_mentions,
    random_amount,
    random_dict,
    random_embed,
    random_file,
    random_message_reference,
    random_sticker,
    reason,
    stickers,
    user_id,
)

if TYPE_CHECKING:
    from discord.file import File


@pytest.fixture(params=(True, False))
def tts(request) -> bool:
    return request.param


@pytest.fixture(params=(None, random_message_reference()))
def message_reference(request) -> message.MessageReference | None:
    return request.param


@pytest.fixture(params=(None,))  # TODO: Add flags to send tests
def flags(request) -> int | None:
    return request.param


@pytest.fixture
def files() -> list[File]:
    return random_amount(random_file)


def attachment_helper(payload, **kwargs):
    form = []
    attachments = []
    form.append({"name": "payload_json"})
    for index, file in enumerate(kwargs["files"]):
        attachments.append(
            {"id": index, "filename": file.filename, "description": file.description}
        )
        form.append(
            {
                "name": f"files[{index}]",
                "value": file.fp,
                "filename": file.filename,
                "content_type": "application/octet-stream",
            }
        )
    if "attachments" not in payload:
        payload["attachments"] = attachments
    else:
        payload["attachments"].extend(attachments)
    form[0]["value"] = utils._to_json(payload)
    return {
        "form": form,
        "files": kwargs["files"],
    }


def payload_helper(**kwargs):
    payload = {}
    if kwargs.get("tts") or kwargs.get("files"):
        payload["tts"] = kwargs.get("tts", False)
    if kwargs.get("content"):
        payload["content"] = kwargs["content"]
    if kwargs.get("embed"):
        payload["embeds"] = [kwargs["embed"]]
    if kwargs.get("embeds"):
        payload["embeds"] = kwargs["embeds"]
    if kwargs.get("nonce"):
        payload["nonce"] = kwargs["nonce"]
    if kwargs.get("allowed_mentions"):
        payload["allowed_mentions"] = kwargs["allowed_mentions"]
    if kwargs.get("message_reference"):
        payload["message_reference"] = kwargs["message_reference"]
    if kwargs.get("stickers"):
        payload["sticker_ids"] = kwargs["stickers"]
    if kwargs.get("components"):
        payload["components"] = kwargs["components"]
    if kwargs.get("flags"):
        payload["flags"] = kwargs["flags"]

    if kwargs.get("files"):
        return attachment_helper(payload, **kwargs)
    return {
        "json": payload,
    }


def edit_file_payload_helper(**kwargs):
    payload = {}
    if "attachments" in kwargs:
        payload["attachments"] = kwargs["attachments"]
    if "flags" in kwargs:
        payload["flags"] = kwargs["flags"]
    if "content" in kwargs:
        payload["content"] = kwargs["content"]
    if "embeds" in kwargs:
        payload["embeds"] = kwargs["embeds"]
    if "allowed_mentions" in kwargs:
        payload["allowed_mentions"] = kwargs["allowed_mentions"]
    if "components" in kwargs:
        payload["components"] = kwargs["components"]
    if "files" in kwargs:
        return attachment_helper(payload, **kwargs)
    return {
        "json": payload,
    }


async def test_send_message(
    client,
    channel_id,
    content,
    tts,
    embed,
    embeds,
    nonce,
    allowed_mentions,
    message_reference,
    stickers,
    components,
    flags,
):
    """Test sending a message."""

    with client.makes_request(
        Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id),
        **payload_helper(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            nonce=nonce,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            stickers=stickers,
            components=components,
            flags=flags,
        ),
    ):
        await client.http.send_message(
            channel_id,
            content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            nonce=nonce,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            stickers=stickers,
            components=components,
            flags=flags,
        )


async def test_send_typing(client, channel_id):
    """Test sending typing."""
    with client.makes_request(
        Route("POST", "/channels/{channel_id}/typing", channel_id=channel_id),
    ):
        await client.http.send_typing(channel_id)


async def test_send_files(
    client,
    channel_id,
    content,
    tts,
    embed,
    embeds,
    nonce,
    allowed_mentions,
    message_reference,
    stickers,
    components,
    flags,
    files,
):
    """Test sending files."""
    with client.makes_request(
        Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id),
        **payload_helper(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            nonce=nonce,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            stickers=stickers,
            components=components,
            flags=flags,
            files=files,
        ),
    ):
        await client.http.send_files(
            channel_id,
            files=files,
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            nonce=nonce,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            stickers=stickers,
            components=components,
            flags=flags,
        )


@pytest.mark.parametrize(
    "exclude",
    powerset(
        [
            "content",
            "embeds",
            "allowed_mentions",
            "components",
            "flags",
        ]
    ),
)
async def test_edit_files(  # TODO: Add attachments
    client,
    channel_id,
    message_id,
    content,
    # embed,  # TODO: Evaluate: Should edit_files support embed shortcut kwarg?
    embeds,
    allowed_mentions,
    components,
    flags,
    files,
    exclude,
):
    """Test editing files."""
    kwargs = {
        "content": content,
        # "embed": embed,
        "embeds": embeds,
        "allowed_mentions": allowed_mentions,
        "components": components,
        "flags": flags,
    }
    for key in exclude:
        del kwargs[key]
    with client.makes_request(
        Route(
            "PATCH",
            f"/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        ),
        **edit_file_payload_helper(files=files, **kwargs),
    ):
        await client.http.edit_files(channel_id, message_id, files=files, **kwargs)


async def test_delete_message(
    client,
    channel_id,
    message_id,
    reason,
):
    """Test deleting a message."""
    with client.makes_request(
        Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        ),
        reason=reason,
    ):
        await client.http.delete_message(channel_id, message_id, reason=reason)


async def test_delete_messages(
    client,
    channel_id,
    message_ids,
    reason,
):
    """Test deleting multiple messages."""
    with client.makes_request(
        Route(
            "POST",
            "/channels/{channel_id}/messages/bulk-delete",
            channel_id=channel_id,
        ),
        json={"messages": message_ids},
        reason=reason,
    ):
        await client.http.delete_messages(channel_id, message_ids, reason=reason)


@pytest.mark.parametrize("fields", [random_dict()])
async def test_edit_message(
    client,
    channel_id,
    message_id,
    fields,
):
    """Test editing a message."""
    with client.makes_request(
        Route(
            "PATCH",
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        ),
        json=fields,
    ):
        await client.http.edit_message(channel_id, message_id, **fields)
