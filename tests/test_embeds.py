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

import copy
import datetime

import pytest

import discord

TITLE = "Embed test"
DESCRIPTION = "Description with **markdown** and an emoji 🐉"
URL = "https://example.com/embed-test"
AUTHOR_NAME = "Author name"
AUTHOR_URL = "https://example.com/author"
AUTHOR_ICON = "https://cdn.discordapp.com/embed/avatars/2.png"
FOOTER_TEXT = "Footer text"
FOOTER_ICON = "https://cdn.discordapp.com/embed/avatars/3.png"
IMAGE_URL = "https://cdn.discordapp.com/embed/avatars/0.png"
THUMBNAIL_URL = "https://cdn.discordapp.com/embed/avatars/1.png"
COLOUR = 0x8A2BE2
TIMESTAMP = datetime.datetime(2026, 1, 2, 3, 4, 5, 678000, tzinfo=datetime.timezone.utc)
FIELDS = [
    ("Inline 1", "a", True),
    ("Inline 2", "b", True),
    ("Block", "c\nmultiline", False),
    ("Unicode ✨", "Ünïcödé 🐉", True),
]

# Shaped like an embed as returned by the Discord API, including server-added keys.
API_PAYLOAD = {
    "type": "rich",
    "title": TITLE,
    "description": DESCRIPTION,
    "url": URL,
    "color": COLOUR,
    "timestamp": "2026-01-02T03:04:05.678000+00:00",
    "author": {
        "name": AUTHOR_NAME,
        "url": AUTHOR_URL,
        "icon_url": AUTHOR_ICON,
        "proxy_icon_url": "https://images-ext-1.discordapp.net/external/a/author.png",
    },
    "footer": {
        "text": FOOTER_TEXT,
        "icon_url": FOOTER_ICON,
        "proxy_icon_url": "https://images-ext-1.discordapp.net/external/b/footer.png",
    },
    "image": {
        "url": IMAGE_URL,
        "proxy_url": "https://images-ext-1.discordapp.net/external/c/image.png",
        "width": 256,
        "height": 256,
    },
    "thumbnail": {
        "url": THUMBNAIL_URL,
        "proxy_url": "https://images-ext-1.discordapp.net/external/d/thumb.png",
        "width": 128,
        "height": 128,
    },
    "fields": [{"name": n, "value": v, "inline": i} for n, v, i in FIELDS],
}

VIDEO_PAYLOAD = {
    "type": "video",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "title": "Some video",
    "provider": {"name": "YouTube", "url": "https://www.youtube.com"},
    "video": {
        "url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "width": 1280,
        "height": 720,
    },
    "thumbnail": {
        "url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "proxy_url": "https://images-ext-1.discordapp.net/external/e/thumb.jpg",
        "width": 1280,
        "height": 720,
    },
}


def _full_embed() -> discord.Embed:
    embed = discord.Embed(
        title=TITLE,
        description=DESCRIPTION,
        url=URL,
        colour=COLOUR,
        timestamp=TIMESTAMP,
    )
    embed.set_author(name=AUTHOR_NAME, url=AUTHOR_URL, icon_url=AUTHOR_ICON)
    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
    embed.set_image(url=IMAGE_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    for name, value, inline in FIELDS:
        embed.add_field(name=name, value=value, inline=inline)
    return embed


def _fields(embed: discord.Embed) -> list[tuple]:
    return [(f.name, f.value, f.inline) for f in embed.fields]


def _unset(obj, attr: str) -> bool:
    return obj is None or getattr(obj, attr, None) is None


# --- construction and scalar attributes ------------------------------------------------


def test_constructor_scalars():
    embed = discord.Embed(
        title="T", description="D", url=URL, colour=COLOUR, timestamp=TIMESTAMP
    )
    assert embed.title == "T"
    assert embed.description == "D"
    assert embed.url == URL
    assert isinstance(embed.colour, discord.Colour)
    assert embed.colour.value == COLOUR
    assert embed.color == embed.colour
    assert embed.timestamp == TIMESTAMP
    assert embed.type == "rich"
    assert embed


def test_constructor_color_alias():
    assert discord.Embed(color=0x123456).colour.value == 0x123456


def test_constructor_object_kwargs():
    embed = discord.Embed(
        fields=[discord.EmbedField(name="a", value="1", inline=False)],
        author=discord.EmbedAuthor(name="A", url=AUTHOR_URL, icon_url=AUTHOR_ICON),
        footer=discord.EmbedFooter(text="F", icon_url=FOOTER_ICON),
        image=IMAGE_URL,
        thumbnail=THUMBNAIL_URL,
    )
    assert _fields(embed) == [("a", "1", False)]
    assert (embed.author.name, embed.author.url, embed.author.icon_url) == (
        "A",
        AUTHOR_URL,
        AUTHOR_ICON,
    )
    assert (embed.footer.text, embed.footer.icon_url) == ("F", FOOTER_ICON)
    assert embed.image.url == IMAGE_URL
    assert embed.thumbnail.url == THUMBNAIL_URL


def test_empty_embed():
    embed = discord.Embed()
    assert not embed
    assert len(embed) == 0
    assert embed.title is None
    assert embed.description is None
    assert embed.url is None
    assert embed.colour is None
    assert embed.timestamp is None
    assert list(embed.fields) == []
    assert _unset(embed.author, "name")
    assert _unset(embed.footer, "text")
    assert _unset(embed.image, "url")
    assert _unset(embed.thumbnail, "url")
    data = embed.to_dict()
    assert all(not v for k, v in data.items() if k != "type"), data


def test_scalar_setters():
    embed = discord.Embed()
    embed.title, embed.description, embed.url = "T", "D", URL
    assert (embed.title, embed.description, embed.url) == ("T", "D", URL)
    embed.title = None
    assert embed.title is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (discord.Colour.blurple(), discord.Colour.blurple().value),
        (0x123456, 0x123456),
        (0, 0),
    ],
    ids=["Colour", "int", "zero"],
)
def test_colour_setter(value: discord.Colour | int, expected: int):
    embed = discord.Embed()
    embed.colour = value
    assert embed.colour.value == expected
    assert embed.color == embed.colour


def test_colour_setter_none_and_invalid():
    embed = discord.Embed(colour=COLOUR)
    embed.colour = None
    assert embed.colour is None
    with pytest.raises(TypeError):
        embed.colour = "red"  # type: ignore[assignment]


def test_timestamp_setter():
    embed = discord.Embed()
    embed.timestamp = TIMESTAMP
    assert embed.timestamp == TIMESTAMP

    embed.timestamp = datetime.datetime(2026, 1, 2, 3, 4, 5)
    assert embed.timestamp.tzinfo is not None

    embed.timestamp = None
    assert embed.timestamp is None

    with pytest.raises(TypeError):
        embed.timestamp = "2026-01-01"  # type: ignore[assignment]


# --- author / footer / media -----------------------------------------------------------


def test_author():
    embed = discord.Embed()
    assert embed.set_author(name="A", url=AUTHOR_URL, icon_url=AUTHOR_ICON) is embed
    assert (embed.author.name, embed.author.url, embed.author.icon_url) == (
        "A",
        AUTHOR_URL,
        AUTHOR_ICON,
    )

    embed.set_author(name="Only name")
    assert embed.author.name == "Only name"
    assert embed.author.url is None
    assert embed.author.icon_url is None

    assert embed.remove_author() is embed
    assert _unset(embed.author, "name")
    embed.remove_author()  # idempotent


def test_footer():
    embed = discord.Embed()
    assert embed.set_footer(text="F", icon_url=FOOTER_ICON) is embed
    assert (embed.footer.text, embed.footer.icon_url) == ("F", FOOTER_ICON)

    embed.set_footer(text="Only text")
    assert embed.footer.text == "Only text"
    assert embed.footer.icon_url is None

    assert embed.remove_footer() is embed
    assert _unset(embed.footer, "text")
    embed.remove_footer()  # idempotent


@pytest.mark.parametrize(
    ("kind", "url"),
    [("image", IMAGE_URL), ("thumbnail", THUMBNAIL_URL)],
    ids=["image", "thumbnail"],
)
def test_media(kind: str, url: str):
    embed = discord.Embed()
    assert getattr(embed, f"set_{kind}")(url=url) is embed
    media = getattr(embed, kind)
    assert media.url == url
    assert _unset(media, "proxy_url")

    assert getattr(embed, f"remove_{kind}")() is embed
    assert _unset(getattr(embed, kind), "url")
    getattr(embed, f"remove_{kind}")()  # idempotent


def test_rich_embed_has_no_video_or_provider():
    embed = _full_embed()
    assert _unset(embed.video, "url")
    assert _unset(embed.provider, "name")


# --- fields ----------------------------------------------------------------------------


def test_field_operations():
    embed = discord.Embed()
    assert embed.add_field(name="f1", value="v1") is embed
    embed.add_field(name="f2", value="v2", inline=False)
    embed.insert_field_at(0, name="f0", value="v0")
    assert _fields(embed) == [
        ("f0", "v0", True),
        ("f1", "v1", True),
        ("f2", "v2", False),
    ]
    assert all(isinstance(f, discord.EmbedField) for f in embed.fields)

    embed.set_field_at(1, name="F1", value="V1", inline=False)
    assert _fields(embed)[1] == ("F1", "V1", False)

    embed.remove_field(0)
    assert [f.name for f in embed.fields] == ["F1", "f2"]

    embed.insert_field_at(99, name="end", value="e")
    assert embed.fields[-1].name == "end"

    embed.clear_fields()
    assert list(embed.fields) == []


def test_set_field_at_out_of_range():
    embed = discord.Embed().add_field(name="a", value="b")
    with pytest.raises(IndexError):
        embed.set_field_at(5, name="x", value="y")


def test_remove_field_out_of_range_is_silent():
    embed = discord.Embed().add_field(name="a", value="b")
    embed.remove_field(5)
    assert len(embed.fields) == 1


def test_add_field_coerces_to_str():
    embed = discord.Embed().add_field(name=1, value=2)  # type: ignore[arg-type]
    assert (embed.fields[0].name, embed.fields[0].value) == ("1", "2")


def test_fields_setter_and_append_field():
    embed = discord.Embed()
    embed.fields = [
        discord.EmbedField(name="a", value="1"),
        discord.EmbedField(name="b", value="2", inline=True),
    ]
    assert [(f.name, f.value) for f in embed.fields] == [("a", "1"), ("b", "2")]

    embed.append_field(discord.EmbedField(name="c", value="3", inline=False))
    assert _fields(embed)[-1] == ("c", "3", False)
    assert embed.to_dict()["fields"][-1] == {"name": "c", "value": "3", "inline": False}


# --- len / serialisation ---------------------------------------------------------------


def test_len():
    expected = (
        len(TITLE)
        + len(DESCRIPTION)
        + len(AUTHOR_NAME)
        + len(FOOTER_TEXT)
        + sum(len(n) + len(v) for n, v, _ in FIELDS)
    )
    assert len(_full_embed()) == expected


def test_to_dict():
    data = _full_embed().to_dict()
    assert data["type"] == "rich"
    assert data["title"] == TITLE
    assert data["description"] == DESCRIPTION
    assert data["url"] == URL
    assert data["color"] == COLOUR
    assert datetime.datetime.fromisoformat(data["timestamp"]) == TIMESTAMP
    assert data["author"] == {
        "name": AUTHOR_NAME,
        "url": AUTHOR_URL,
        "icon_url": AUTHOR_ICON,
    }
    assert data["footer"] == {"text": FOOTER_TEXT, "icon_url": FOOTER_ICON}
    assert data["image"] == {"url": IMAGE_URL}
    assert data["thumbnail"] == {"url": THUMBNAIL_URL}
    assert data["fields"] == [
        {"name": n, "value": v, "inline": i} for n, v, i in FIELDS
    ]


def test_to_dict_from_dict_roundtrip():
    data = _full_embed().to_dict()
    snapshot = copy.deepcopy(data)
    embed = discord.Embed.from_dict(data)

    assert embed.to_dict() == data
    assert data == snapshot  # input not mutated

    embed.add_field(name="x", value="y")
    embed.set_author(name="changed")
    assert data == snapshot  # result doesn't share state with input


def test_from_api_payload():
    payload = copy.deepcopy(API_PAYLOAD)
    embed = discord.Embed.from_dict(payload)

    assert embed.type == "rich"
    assert (embed.title, embed.description, embed.url) == (TITLE, DESCRIPTION, URL)
    assert embed.colour.value == COLOUR
    assert embed.timestamp == TIMESTAMP
    assert embed.author.name == AUTHOR_NAME
    assert embed.author.proxy_icon_url == API_PAYLOAD["author"]["proxy_icon_url"]
    assert embed.footer.text == FOOTER_TEXT
    assert embed.footer.proxy_icon_url == API_PAYLOAD["footer"]["proxy_icon_url"]
    for kind in ("image", "thumbnail"):
        media = getattr(embed, kind)
        expected = API_PAYLOAD[kind]
        assert (media.url, media.proxy_url, media.width, media.height) == (
            expected["url"],
            expected["proxy_url"],
            expected["width"],
            expected["height"],
        )
    assert _fields(embed) == FIELDS
    assert payload == API_PAYLOAD  # input not mutated


def test_api_payload_roundtrip_is_stable():
    embed = discord.Embed.from_dict(copy.deepcopy(API_PAYLOAD))
    data = embed.to_dict()
    assert discord.Embed.from_dict(data).to_dict() == data
    assert embed.copy().to_dict() == data


def test_from_video_payload():
    embed = discord.Embed.from_dict(copy.deepcopy(VIDEO_PAYLOAD))
    assert embed.type == "video"
    assert embed.provider.name == "YouTube"
    assert embed.provider.url == "https://www.youtube.com"
    assert embed.video.url == VIDEO_PAYLOAD["video"]["url"]
    assert (embed.video.width, embed.video.height) == (1280, 720)
    assert embed.thumbnail.proxy_url == VIDEO_PAYLOAD["thumbnail"]["proxy_url"]


def test_copy_is_independent():
    original = _full_embed()
    clone = original.copy()
    assert clone.to_dict() == original.to_dict()

    clone.add_field(name="extra", value="x")
    clone.fields[0].name = "mutated"
    clone.set_author(name="changed")
    clone.set_footer(text="changed")
    clone.colour = 0x000001
    clone.timestamp = None

    assert _fields(original) == FIELDS
    assert original.author.name == AUTHOR_NAME
    assert original.footer.text == FOOTER_TEXT
    assert original.colour.value == COLOUR
    assert original.timestamp == TIMESTAMP
