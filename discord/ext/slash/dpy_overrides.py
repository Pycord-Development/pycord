import typing

import discord
from discord import AllowedMentions, File, InvalidArgument, abc, http, utils
from discord.ext import commands
from discord.http import Route


class ComponentMessage(discord.Message):
    __slots__ = tuple(list(discord.Message.__slots__) + ["components"])

    def __init__(self, *, state, channel, data):
        super().__init__(state=state, channel=channel, data=data)
        self.components = data["components"]

    def get_component(self, custom_id: int) -> typing.Optional[dict]:
        """
        Returns first component with matching custom_id

        :param custom_id: custom_id of component to get from message components
        :return: Optional[dict]

        """
        for row in self.components:
            for component in row["components"]:
                if "custom_id" in component and component["custom_id"] == custom_id:
                    return component


def new_override(cls, *args, **kwargs):
    if isinstance(cls, discord.Message):
        return object.__new__(ComponentMessage)
    else:
        return object.__new__(cls)


discord.message.Message.__new__ = new_override


def send_files(
    self,
    channel_id,
    *,
    files,
    content=None,
    tts=False,
    embed=None,
    components=None,
    nonce=None,
    allowed_mentions=None,
    message_reference=None
):
    r = Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id)
    form = []

    payload = {"tts": tts}
    if content:
        payload["content"] = content
    if embed:
        payload["embed"] = embed
    if components:
        payload["components"] = components
    if nonce:
        payload["nonce"] = nonce
    if allowed_mentions:
        payload["allowed_mentions"] = allowed_mentions
    if message_reference:
        payload["message_reference"] = message_reference

    form.append({"name": "payload_json", "value": utils.to_json(payload)})
    if len(files) == 1:
        file = files[0]
        form.append(
            {
                "name": "file",
                "value": file.fp,
                "filename": file.filename,
                "content_type": "application/octet-stream",
            }
        )
    else:
        for index, file in enumerate(files):
            form.append(
                {
                    "name": "file%s" % index,
                    "value": file.fp,
                    "filename": file.filename,
                    "content_type": "application/octet-stream",
                }
            )

    return self.request(r, form=form, files=files)


def send_message(
    self,
    channel_id,
    content,
    *,
    tts=False,
    embed=None,
    components=None,
    nonce=None,
    allowed_mentions=None,
    message_reference=None
):
    r = Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id)
    payload = {}

    if content:
        payload["content"] = content

    if tts:
        payload["tts"] = True

    if embed:
        payload["embed"] = embed

    if components:
        payload["components"] = components

    if nonce:
        payload["nonce"] = nonce

    if allowed_mentions:
        payload["allowed_mentions"] = allowed_mentions

    if message_reference:
        payload["message_reference"] = message_reference

    return self.request(r, json=payload)


http.HTTPClient.send_files = send_files
http.HTTPClient.send_message = send_message


async def send(
    self,
    content=None,
    *,
    tts=False,
    embed=None,
    file=None,
    components=None,
    files=None,
    delete_after=None,
    nonce=None,
    allowed_mentions=None,
    reference=None,
    mention_author=None
):
    """|coro|

    Sends a message to the destination with the content given.

    The content must be a type that can convert to a string through ``str(content)``.
    If the content is set to ``None`` (the default), then the ``embed`` parameter must
    be provided.

    To upload a single file, the ``file`` parameter should be used with a
    single :class:`~discord.File` object. To upload multiple files, the ``files``
    parameter should be used with a :class:`list` of :class:`~discord.File` objects.
    **Specifying both parameters will lead to an exception**.

    If the ``embed`` parameter is provided, it must be of type :class:`~discord.Embed` and
    it must be a rich embed type.

    Parameters
    ------------
    content: :class:`str`
        The content of the message to send.
    tts: :class:`bool`
        Indicates if the message should be sent using text-to-speech.
    embed: :class:`~discord.Embed`
        The rich embed for the content.
    file: :class:`~discord.File`
        The file to upload.
    files: List[:class:`~discord.File`]
        A list of files to upload. Must be a maximum of 10.
    nonce: :class:`int`
        The nonce to use for sending this message. If the message was successfully sent,
        then the message will have a nonce with this value.
    delete_after: :class:`float`
        If provided, the number of seconds to wait in the background
        before deleting the message we just sent. If the deletion fails,
        then it is silently ignored.
    allowed_mentions: :class:`~discord.AllowedMentions`
        Controls the mentions being processed in this message. If this is
        passed, then the object is merged with :attr:`~discord.Client.allowed_mentions`.
        The merging behaviour only overrides attributes that have been explicitly passed
        to the object, otherwise it uses the attributes set in :attr:`~discord.Client.allowed_mentions`.
        If no object is passed at all then the defaults given by :attr:`~discord.Client.allowed_mentions`
        are used instead.

        .. versionadded:: 1.4

    reference: Union[:class:`~discord.Message`, :class:`~discord.MessageReference`]
        A reference to the :class:`~discord.Message` to which you are replying, this can be created using
        :meth:`~discord.Message.to_reference` or passed directly as a :class:`~discord.Message`. You can control
        whether this mentions the author of the referenced message using the :attr:`~discord.AllowedMentions.replied_user`
        attribute of ``allowed_mentions`` or by setting ``mention_author``.

        .. versionadded:: 1.6

    mention_author: Optional[:class:`bool`]
        If set, overrides the :attr:`~discord.AllowedMentions.replied_user` attribute of ``allowed_mentions``.

        .. versionadded:: 1.6

    Raises
    --------
    ~discord.HTTPException
        Sending the message failed.
    ~discord.Forbidden
        You do not have the proper permissions to send the message.
    ~discord.InvalidArgument
        The ``files`` list is not of the appropriate size,
        you specified both ``file`` and ``files``,
        or the ``reference`` object is not a :class:`~discord.Message`
        or :class:`~discord.MessageReference`.

    Returns
    ---------
    :class:`~discord.Message`
        The message that was sent.
    """

    channel = await self._get_channel()
    state = self._state
    content = str(content) if content is not None else None
    components = components or []
    if embed is not None:
        embed = embed.to_dict()

    if allowed_mentions is not None:
        if state.allowed_mentions is not None:
            allowed_mentions = state.allowed_mentions.merge(allowed_mentions).to_dict()
        else:
            allowed_mentions = allowed_mentions.to_dict()
    else:
        allowed_mentions = state.allowed_mentions and state.allowed_mentions.to_dict()

    if mention_author is not None:
        allowed_mentions = allowed_mentions or AllowedMentions().to_dict()
        allowed_mentions["replied_user"] = bool(mention_author)

    if reference is not None:
        try:
            reference = reference.to_message_reference_dict()
        except AttributeError:
            raise InvalidArgument(
                "reference parameter must be Message or MessageReference"
            ) from None

    if file is not None and files is not None:
        raise InvalidArgument("cannot pass both file and files parameter to send()")

    if file is not None:
        if not isinstance(file, File):
            raise InvalidArgument("file parameter must be File")

        try:
            data = await state.http.send_files(
                channel.id,
                files=[file],
                allowed_mentions=allowed_mentions,
                content=content,
                tts=tts,
                embed=embed,
                nonce=nonce,
                components=components,
                message_reference=reference,
            )
        finally:
            file.close()

    elif files is not None:
        if len(files) > 10:
            raise InvalidArgument("files parameter must be a list of up to 10 elements")
        elif not all(isinstance(file, File) for file in files):
            raise InvalidArgument("files parameter must be a list of File")

        try:
            data = await state.http.send_files(
                channel.id,
                files=files,
                content=content,
                tts=tts,
                embed=embed,
                nonce=nonce,
                allowed_mentions=allowed_mentions,
                components=components,
                message_reference=reference,
            )
        finally:
            for f in files:
                f.close()
    else:
        data = await state.http.send_message(
            channel.id,
            content,
            tts=tts,
            embed=embed,
            components=components,
            nonce=nonce,
            allowed_mentions=allowed_mentions,
            message_reference=reference,
        )

    ret = state.create_message(channel=channel, data=data)
    if delete_after is not None:
        await ret.delete(delay=delete_after)
    return ret


async def send_override(context_or_channel, *args, **kwargs):
    if isinstance(context_or_channel, commands.Context):
        channel = context_or_channel.channel
    else:
        channel = context_or_channel

    return await send(channel, *args, **kwargs)


abc.Messageable.send = send_override
