"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
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
from typing import TYPE_CHECKING, Any, Mapping, TypeVar

from . import utils
from .colour import Colour

__all__ = (
    "Embed",
    "EmbedField",
    "EmbedAuthor",
    "EmbedFooter",
    "EmbedMedia",
    "EmbedProvider",
)


E = TypeVar("E", bound="Embed")

if TYPE_CHECKING:
    from discord.types.embed import Embed as EmbedData
    from discord.types.embed import EmbedType


class EmbedAuthor:
    """Represents the author on the :class:`Embed` object.

    .. versionadded:: 2.5

    Attributes
    ----------
    name: :class:`str`
        The name of the author.
    url: :class:`str`
        The URL of the hyperlink created in the author's name.
    icon_url: :class:`str`
        The URL of the author icon image.
    proxy_icon_url: :class:`str`
        The proxied URL of the author icon image. This can't be set directly, it is set by Discord.
    """

    def __init__(
        self,
        name: str,
        url: str | None = None,
        icon_url: str | None = None,
    ) -> None:
        self.name: str = name
        self.url: str | None = url
        self.icon_url: str | None = icon_url
        self.proxy_icon_url: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> EmbedAuthor:
        self = cls.__new__(cls)
        name = data.get("name")
        if not name:
            raise ValueError("name field is required")
        self.name = name
        self.url = data.get("url")
        self.icon_url = data.get("icon_url")
        self.proxy_icon_url = data.get("proxy_icon_url")
        return self

    def to_dict(self) -> dict[str, str]:
        d = {"name": str(self.name)}
        if self.url:
            d["url"] = str(self.url)
        if self.icon_url:
            d["icon_url"] = str(self.icon_url)
        return d

    def __len__(self) -> int:
        """Returns the total number of characters in the author name."""
        return len(self.name)

    def __repr__(self) -> str:
        return f"<EmbedAuthor name={self.name!r} url={self.url!r} icon_url={self.icon_url!r}>"


class EmbedFooter:
    """Represents the footer on the :class:`Embed` object.

    .. versionadded:: 2.5

    Attributes
    ----------
    text: :class:`str`
       The text inside the footer.
    icon_url: :class:`str`
        The URL of the footer icon image.
    proxy_icon_url: :class:`str`
        The proxied URL of the footer icon image. This can't be set directly, it is set by Discord.
    """

    def __init__(
        self,
        text: str,
        icon_url: str | None = None,
    ) -> None:
        self.text: str = text
        self.icon_url: str | None = icon_url
        self.proxy_icon_url: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> EmbedFooter:
        self = cls.__new__(cls)
        text = data.get("text")
        if not text:
            raise ValueError("text field is required")
        self.text = text
        self.icon_url = data.get("icon_url")
        self.proxy_icon_url = data.get("proxy_icon_url")
        return self

    def to_dict(self) -> dict[str, Any]:
        d = {"text": str(self.text)}
        if self.icon_url:
            d["icon_url"] = str(self.icon_url)
        return d

    def __len__(self) -> int:
        """Returns the total number of characters in the footer text."""
        return len(self.text)

    def __repr__(self) -> str:
        return f"<EmbedFooter text={self.text!r} icon_url={self.icon_url!r}>"


class EmbedMedia:  # Thumbnail, Image, Video
    """Represents a media on the :class:`Embed` object.
    This includes thumbnails, images, and videos.

    .. versionadded:: 2.5

    Attributes
    ----------
    url: :class:`str`
        The source URL of the media.
    proxy_url: :class:`str`
        The proxied URL of the media.
    height: :class:`int`
        The height of the media.
    width: :class:`int`
        The width of the media.
    """

    url: str
    proxy_url: str | None
    height: int | None
    width: int | None

    def __init__(self, url: str):
        self.url = url
        self.proxy_url = None
        self.height = None
        self.width = None

    @classmethod
    def from_dict(cls, data: dict[str, str | int]) -> EmbedMedia:
        self = cls.__new__(cls)
        self.url = str(data.get("url"))
        self.proxy_url = (
            str(proxy_url) if (proxy_url := data.get("proxy_url")) else None
        )
        self.height = int(height) if (height := data.get("height")) else None
        self.width = int(width) if (width := data.get("width")) else None
        return self

    def __repr__(self) -> str:
        return f"<EmbedMedia url={self.url!r} proxy_url={self.proxy_url!r}> height={self.height!r} width={self.width!r}>"


class EmbedProvider:
    """Represents a provider on the :class:`Embed` object.

    .. versionadded:: 2.5

    Attributes
    ----------
    name: :class:`str`
        The name of the provider.
    url: :class:`str`
        The URL of the provider.
    """

    name: str | None
    url: str | None

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> EmbedProvider:
        self = cls.__new__(cls)
        self.name = data.get("name")
        self.url = data.get("url")
        return self

    def __repr__(self) -> str:
        return f"<EmbedProvider name={self.name!r} url={self.url!r}>"


class EmbedField:
    """Represents a field on the :class:`Embed` object.

    .. versionadded:: 2.0

    Attributes
    ----------
    name: :class:`str`
        The name of the field.
    value: :class:`str`
        The value of the field.
    inline: :class:`bool`
        Whether the field should be displayed inline.
    """

    def __init__(self, name: str, value: str, inline: bool | None = False):
        self.name = name
        self.value = value
        self.inline = inline

    @classmethod
    def from_dict(cls, data: dict[str, str | bool]) -> EmbedField:
        """Converts a :class:`dict` to a :class:`EmbedField` provided it is in the
        format that Discord expects it to be in.

        You can find out about this format in the `official Discord documentation`__.

        .. _DiscordDocsEF: https://discord.com/developers/docs/resources/channel#embed-object-embed-field-structure

        __ DiscordDocsEF_

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into an EmbedField object.
        """
        self = cls.__new__(cls)

        self.name = data["name"]
        self.value = data["value"]
        self.inline = data.get("inline", False)

        return self

    def to_dict(self) -> dict[str, str | bool | None]:
        """Converts this EmbedField object into a dict.

        Returns
        -------
        Dict[:class:`str`, Union[:class:`str`, :class:`bool`]]
            A dictionary of :class:`str` embed field keys bound to the respective value.
        """
        return {
            "name": self.name,
            "value": self.value,
            "inline": self.inline,
        }

    def __repr__(self) -> str:
        return f"<EmbedField name={self.name!r} value={self.value!r} inline={self.inline!r}>"


class Embed:
    """Represents a Discord embed.

    .. container:: operations

        .. describe:: len(x)

            Returns the total size of the embed.
            Useful for checking if it's within the 6000 character limit.

        .. describe:: bool(b)

            Returns whether the embed has any data set.

            .. versionadded:: 2.0

    For ease of use, all parameters that expect a :class:`str` are implicitly
    cast to :class:`str` for you.

    Attributes
    ----------
    title: :class:`str`
        The title of the embed.
        This can be set during initialisation.
        Must be 256 characters or fewer.
    type: :class:`str`
        The type of embed. Usually "rich".
        This can be set during initialisation.
        Possible strings for embed types can be found on discord's
        `api docs <https://discord.com/developers/docs/resources/channel#embed-object-embed-types>`_
    description: :class:`str`
        The description of the embed.
        This can be set during initialisation.
        Must be 4096 characters or fewer.
    url: :class:`str`
        The URL of the embed.
        This can be set during initialisation.
    timestamp: :class:`datetime.datetime`
        The timestamp of the embed content. This is an aware datetime.
        If a naive datetime is passed, it is converted to an aware
        datetime with the local timezone.
    colour: Union[:class:`Colour`, :class:`int`]
        The colour code of the embed. Aliased to ``color`` as well.
        This can be set during initialisation.
    """

    __slots__ = (
        "title",
        "url",
        "type",
        "_timestamp",
        "_colour",
        "_footer",
        "_image",
        "_thumbnail",
        "_video",
        "_provider",
        "_author",
        "_fields",
        "description",
    )

    def __init__(
        self,
        *,
        colour: int | Colour | None = None,
        color: int | Colour | None = None,
        title: Any | None = None,
        type: EmbedType = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime.datetime | None = None,
        fields: list[EmbedField] | None = None,
        author: EmbedAuthor | None = None,
        footer: EmbedFooter | None = None,
        image: str | EmbedMedia | None = None,
        thumbnail: str | EmbedMedia | None = None,
    ):
        self.colour = colour if colour else color
        self.title = title
        self.type = type
        self.url = url
        self.description = description

        if self.title:
            self.title = str(self.title)

        if self.description:
            self.description = str(self.description)

        if self.url:
            self.url = str(self.url)

        if timestamp:
            self.timestamp = timestamp

        self._fields: list[EmbedField] = fields if fields is not None else []

        self.author = author
        self.footer = footer
        self.image = image
        self.thumbnail = thumbnail

    @classmethod
    def from_dict(cls: type[E], data: Mapping[str, Any]) -> E:
        """Converts a :class:`dict` to a :class:`Embed` provided it is in the
        format that Discord expects it to be in.

        You can find out about this format in the `official Discord documentation`__.

        .. _DiscordDocs: https://discord.com/developers/docs/resources/channel#embed-object

        __ DiscordDocs_

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into an embed.

        Returns
        -------
        :class:`Embed`
            The converted embed object.
        """
        # we are bypassing __init__ here since it doesn't apply here
        self: E = cls.__new__(cls)

        # fill in the basic fields

        self.title = data.get("title", None)
        self.type = data.get("type", None)
        self.description = data.get("description", None)
        self.url = data.get("url", None)

        if self.title:
            self.title = str(self.title)

        if self.description:
            self.description = str(self.description)

        if self.url:
            self.url = str(self.url)

        # try to fill in the more rich fields

        try:
            self._colour = Colour(value=data["color"])
        except KeyError:
            pass

        try:
            self._timestamp = utils.parse_time(data["timestamp"])
        except KeyError:
            pass

        for attr in (
            "thumbnail",
            "video",
            "provider",
            "author",
            "fields",
            "image",
            "footer",
        ):
            if attr == "fields":
                value = data.get(attr, [])
                self._fields = [EmbedField.from_dict(d) for d in value] if value else []
            else:
                try:
                    value = data[attr]
                except KeyError:
                    continue
                else:
                    setattr(self, f"_{attr}", value)

        return self

    def copy(self: E) -> E:
        """Creates a shallow copy of the :class:`Embed` object.

        Returns
        -------
        :class:`Embed`
            The copied embed object.
        """
        return self.__class__.from_dict(self.to_dict())

    def __len__(self) -> int:
        total = 0
        if self.title:
            total += len(self.title)
        if self.description:
            total += len(self.description)
        for field in getattr(self, "_fields", []):
            total += len(field.name) + len(field.value)

        try:
            footer_text = self._footer["text"]
        except (AttributeError, KeyError):
            pass
        else:
            total += len(footer_text)

        try:
            author = self._author
        except AttributeError:
            pass
        else:
            total += len(author["name"])

        return total

    def __bool__(self) -> bool:
        return any(
            (
                self.title,
                self.url,
                self.description,
                self.colour,
                self.fields,
                self.timestamp,
                self.author,
                self.thumbnail,
                self.footer,
                self.image,
                self.provider,
                self.video,
            )
        )

    @property
    def colour(self) -> Colour | None:
        return getattr(self, "_colour", None)

    @colour.setter
    def colour(self, value: int | Colour | None):  # type: ignore
        if value is None or isinstance(value, Colour):
            self._colour = value
        elif isinstance(value, int):
            self._colour = Colour(value=value)
        else:
            raise TypeError(
                "Expected discord.Colour, int, or None but received"
                f" {value.__class__.__name__} instead."
            )

    color = colour

    @property
    def timestamp(self) -> datetime.datetime | None:
        return getattr(self, "_timestamp", None)

    @timestamp.setter
    def timestamp(self, value: datetime.datetime | None):
        if isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                value = value.astimezone()
            self._timestamp = value
        elif value is None:
            self._timestamp = value
        else:
            raise TypeError(
                "Expected datetime.datetime or None. Received"
                f" {value.__class__.__name__} instead"
            )

    @property
    def footer(self) -> EmbedFooter | None:
        """Returns an :class:`EmbedFooter` denoting the footer contents.

        See :meth:`set_footer` for possible values you can access.

        If the footer is not set then `None` is returned.
        """
        foot = getattr(self, "_footer", None)
        if not foot:
            return None
        return EmbedFooter.from_dict(foot)

    @footer.setter
    def footer(self, value: EmbedFooter | None):
        if value is None:
            self.remove_footer()
        elif isinstance(value, EmbedFooter):
            self._footer = value.to_dict()
        else:
            raise TypeError(
                "Expected EmbedFooter or None. Received"
                f" {value.__class__.__name__} instead"
            )

    def set_footer(
        self: E,
        *,
        text: Any | None = None,
        icon_url: Any | None = None,
    ) -> E:
        """Sets the footer for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        ----------
        text: :class:`str`
            The footer text.
            Must be 2048 characters or fewer.
        icon_url: :class:`str`
            The URL of the footer icon. Only HTTP(S) is supported.
        """

        self._footer = {}
        if text:
            self._footer["text"] = str(text)

        if icon_url:
            self._footer["icon_url"] = str(icon_url)

        return self

    def remove_footer(self: E) -> E:
        """Clears embed's footer information.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionadded:: 2.0
        """
        try:
            del self._footer
        except AttributeError:
            pass

        return self

    @property
    def image(self) -> EmbedMedia | None:
        """Returns an :class:`EmbedMedia` denoting the image contents.

        Attributes you can access are:

        - ``url``
        - ``proxy_url``
        - ``width``
        - ``height``

        If the image is not set then `None` is returned.
        """
        img = getattr(self, "_image", None)
        if not img:
            return None
        return EmbedMedia.from_dict(img)

    @image.setter
    def image(self, value: str | EmbedMedia | None):
        if value is None:
            self.remove_image()
        elif isinstance(value, str):
            self.set_image(url=value)
        elif isinstance(value, EmbedMedia):
            self.set_image(url=value.url)
        else:
            raise TypeError(
                "Expected discord.EmbedMedia, or None but received"
                f" {value.__class__.__name__} instead."
            )

    def set_image(self: E, *, url: Any | None) -> E:
        """Sets the image for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionchanged:: 1.4
            Passing `None` removes the image.

        Parameters
        ----------
        url: :class:`str`
            The source URL for the image. Only HTTP(S) is supported.
        """

        if url is None:
            try:
                del self._image
            except AttributeError:
                pass
        else:
            self._image = {
                "url": str(url),
            }

        return self

    def remove_image(self: E) -> E:
        """Removes the embed's image.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionadded:: 2.0
        """
        try:
            del self._image
        except AttributeError:
            pass

        return self

    @property
    def thumbnail(self) -> EmbedMedia | None:
        """Returns an :class:`EmbedMedia` denoting the thumbnail contents.

        Attributes you can access are:

        - ``url``
        - ``proxy_url``
        - ``width``
        - ``height``

        If the thumbnail is not set then `None` is returned.
        """
        thumb = getattr(self, "_thumbnail", None)
        if not thumb:
            return None
        return EmbedMedia.from_dict(thumb)

    @thumbnail.setter
    def thumbnail(self, value: str | EmbedMedia | None):
        if value is None:
            self.remove_thumbnail()
        elif isinstance(value, str):
            self.set_thumbnail(url=value)
        elif isinstance(value, EmbedMedia):
            self.set_thumbnail(url=value.url)
        else:
            raise TypeError(
                "Expected discord.EmbedMedia, or None but received"
                f" {value.__class__.__name__} instead."
            )

    def set_thumbnail(self: E, *, url: Any | None) -> E:
        """Sets the thumbnail for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionchanged:: 1.4
            Passing `None` removes the thumbnail.

        Parameters
        ----------
        url: :class:`str`
            The source URL for the thumbnail. Only HTTP(S) is supported.
        """

        if url is None:
            try:
                del self._thumbnail
            except AttributeError:
                pass
        else:
            self._thumbnail = {
                "url": str(url),
            }

        return self

    def remove_thumbnail(self: E) -> E:
        """Removes the embed's thumbnail.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionadded:: 2.0
        """
        try:
            del self._thumbnail
        except AttributeError:
            pass

        return self

    @property
    def video(self) -> EmbedMedia | None:
        """Returns an :class:`EmbedMedia` denoting the video contents.

        Attributes include:

        - ``url`` for the video URL.
        - ``height`` for the video height.
        - ``width`` for the video width.

        If the video is not set then `None` is returned.
        """
        vid = getattr(self, "_video", None)
        if not vid:
            return None
        return EmbedMedia.from_dict(vid)

    @property
    def provider(self) -> EmbedProvider | None:
        """Returns an :class:`EmbedProvider` denoting the provider contents.

        The only attributes that might be accessed are ``name`` and ``url``.

        If the provider is not set then `None` is returned.
        """
        prov = getattr(self, "_provider", None)
        if not prov:
            return None
        return EmbedProvider.from_dict(prov)

    @property
    def author(self) -> EmbedAuthor | None:
        """Returns an :class:`EmbedAuthor` denoting the author contents.

        See :meth:`set_author` for possible values you can access.

        If the author is not set then `None` is returned.
        """
        auth = getattr(self, "_author", None)
        if not auth:
            return None
        return EmbedAuthor.from_dict(auth)

    @author.setter
    def author(self, value: EmbedAuthor | None):
        if value is None:
            self.remove_author()
        elif isinstance(value, EmbedAuthor):
            self._author = value.to_dict()
        else:
            raise TypeError(
                "Expected discord.EmbedAuthor, or None but received"
                f" {value.__class__.__name__} instead."
            )

    def set_author(
        self: E,
        *,
        name: Any,
        url: Any | None = None,
        icon_url: Any | None = None,
    ) -> E:
        """Sets the author for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        ----------
        name: :class:`str`
            The name of the author.
            Must be 256 characters or fewer.
        url: :class:`str`
            The URL for the author.
        icon_url: :class:`str`
            The URL of the author icon. Only HTTP(S) is supported.
        """

        self._author = {
            "name": str(name),
        }

        if url:
            self._author["url"] = str(url)

        if icon_url:
            self._author["icon_url"] = str(icon_url)

        return self

    def remove_author(self: E) -> E:
        """Clears embed's author information.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionadded:: 1.4
        """
        try:
            del self._author
        except AttributeError:
            pass

        return self

    @property
    def fields(self) -> list[EmbedField]:
        """Returns a :class:`list` of :class:`EmbedField` objects denoting the field contents.

        See :meth:`add_field` for possible values you can access.

        If the attribute has no value then ``None`` is returned.
        """
        return self._fields

    @fields.setter
    def fields(self, value: list[EmbedField]) -> None:
        """Sets the fields for the embed. This overwrites any existing fields.

        Parameters
        ----------
        value: List[:class:`EmbedField`]
            The list of :class:`EmbedField` objects to include in the embed.
        """
        if not all(isinstance(x, EmbedField) for x in value):
            raise TypeError("Expected a list of EmbedField objects.")

        self._fields = value

    def append_field(self, field: EmbedField) -> None:
        """Appends an :class:`EmbedField` object to the embed.

        .. versionadded:: 2.0

        Parameters
        ----------
        field: :class:`EmbedField`
            The field to add.
        """
        if not isinstance(field, EmbedField):
            raise TypeError("Expected an EmbedField object.")

        self._fields.append(field)

    def add_field(self: E, *, name: str, value: str, inline: bool = True) -> E:
        """Adds a field to the embed object.

        This function returns the class instance to allow for fluent-style
        chaining. There must be 25 fields or fewer.

        Parameters
        ----------
        name: :class:`str`
            The name of the field.
            Must be 256 characters or fewer.
        value: :class:`str`
            The value of the field.
            Must be 1024 characters or fewer.
        inline: :class:`bool`
            Whether the field should be displayed inline.
        """
        self._fields.append(EmbedField(name=str(name), value=str(value), inline=inline))

        return self

    def insert_field_at(
        self: E, index: int, *, name: Any, value: Any, inline: bool = True
    ) -> E:
        """Inserts a field before a specified index to the embed.

        This function returns the class instance to allow for fluent-style
        chaining. There must be 25 fields or fewer.

        .. versionadded:: 1.2

        Parameters
        ----------
        index: :class:`int`
            The index of where to insert the field.
        name: :class:`str`
            The name of the field.
            Must be 256 characters or fewer.
        value: :class:`str`
            The value of the field.
            Must be 1024 characters or fewer.
        inline: :class:`bool`
            Whether the field should be displayed inline.
        """

        field = EmbedField(name=str(name), value=str(value), inline=inline)

        self._fields.insert(index, field)

        return self

    def clear_fields(self) -> None:
        """Removes all fields from this embed."""
        self._fields.clear()

    def remove_field(self, index: int) -> None:
        """Removes a field at a specified index.

        If the index is invalid or out of bounds then the error is
        silently swallowed.

        .. note::

            When deleting a field by index, the index of the other fields
            shift to fill the gap just like a regular list.

        Parameters
        ----------
        index: :class:`int`
            The index of the field to remove.
        """
        try:
            del self._fields[index]
        except IndexError:
            pass

    def set_field_at(
        self: E, index: int, *, name: Any, value: Any, inline: bool = True
    ) -> E:
        """Modifies a field to the embed object.

        The index must point to a valid pre-existing field. There must be 25 fields or fewer.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        ----------
        index: :class:`int`
            The index of the field to modify.
        name: :class:`str`
            The name of the field.
            Must be 256 characters or fewer.
        value: :class:`str`
            The value of the field.
            Must be 1024 characters or fewer.
        inline: :class:`bool`
            Whether the field should be displayed inline.

        Raises
        ------
        IndexError
            An invalid index was provided.
        """

        try:
            field = self._fields[index]
        except (TypeError, IndexError):
            raise IndexError("field index out of range")

        field.name = str(name)
        field.value = str(value)
        field.inline = inline
        return self

    def to_dict(self) -> EmbedData:
        """Converts this embed object into a dict.

        Returns
        -------
        Dict[:class:`str`, Union[:class:`str`, :class:`int`, :class:`bool`]]
            A dictionary of :class:`str` embed keys bound to the respective value.
        """

        # add in the raw data into the dict
        result = {
            key[1:]: getattr(self, key)
            for key in self.__slots__
            if key != "_fields" and key[0] == "_" and hasattr(self, key)
        }

        # add in the fields
        result["fields"] = [field.to_dict() for field in self._fields]

        # deal with basic convenience wrappers

        try:
            colour = result.pop("colour")
        except KeyError:
            pass
        else:
            if colour:
                result["color"] = colour.value

        try:
            timestamp = result.pop("timestamp")
        except KeyError:
            pass
        else:
            if timestamp:
                if timestamp.tzinfo:
                    result["timestamp"] = timestamp.astimezone(
                        tz=datetime.timezone.utc
                    ).isoformat()
                else:
                    result["timestamp"] = timestamp.replace(
                        tzinfo=datetime.timezone.utc
                    ).isoformat()

        # add in the non-raw attribute ones
        if self.type:
            result["type"] = self.type

        if self.description:
            result["description"] = self.description

        if self.url:
            result["url"] = self.url

        if self.title:
            result["title"] = self.title

        return result  # type: ignore
