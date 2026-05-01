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

from typing import TYPE_CHECKING, Iterable, Union

from .colour import Colour
from .enums import SharedClientThemeBaseType, try_enum

__all__ = ("SharedClientTheme",)


if TYPE_CHECKING:
    from .types.shared_client_theme import SharedClientTheme as SharedClientThemePayload

    ColourLike = Union[Colour, str, int]


def _coerce_colour(value: ColourLike) -> str:
    if isinstance(value, Colour):
        return f"{value.value:0>6x}"
    if isinstance(value, int):
        return f"{value:0>6x}"
    if isinstance(value, str):
        stripped = value.lstrip("#")
        if len(stripped) != 6 or any(
            c not in "0123456789abcdefABCDEF" for c in stripped
        ):
            raise ValueError(
                f"{value!r} is not a valid hexadecimal color (expected format: 'rrggbb')"
            )
        return stripped.lower()
    raise TypeError(f"colors must be Colour, str, or int, not {type(value).__name__}")


class SharedClientTheme:
    """Represents a shared client theme that can be sent in a message.

    A shared client theme lets users transmit a customized Discord client
    appearance (colors, gradient, and base mode) through a message.

    .. versionadded:: 2.9

    Attributes
    ----------
    colors: List[:class:`str`]
        The hexadecimal-encoded colors of the theme. A maximum of 5 colors.
    gradient_angle: :class:`int`
        The direction of the theme's colors, in degrees. Must be between ``0`` and ``360``.
    base_mix: :class:`int`
        The intensity of the theme's colors. Must be between ``0`` and ``100``.
    base_theme: Optional[:class:`SharedClientThemeBaseType`]
        The mode of the theme. Defaults to :attr:`SharedClientThemeBaseType.unset`,
        which Discord treats as :attr:`SharedClientThemeBaseType.dark`.
    """

    __slots__ = ("colors", "gradient_angle", "base_mix", "base_theme")

    def __init__(
        self,
        colors: Iterable[ColourLike],
        gradient_angle: int,
        base_mix: int,
        *,
        base_theme: SharedClientThemeBaseType | None = None,
    ):
        normalized = [_coerce_colour(c) for c in colors]
        if not normalized:
            raise ValueError("colors must contain at least one color")
        if len(normalized) > 5:
            raise ValueError("colors must contain at most 5 colors")

        if not isinstance(gradient_angle, int) or isinstance(gradient_angle, bool):
            raise TypeError("gradient_angle must be an int")
        if not 0 <= gradient_angle <= 360:
            raise ValueError("gradient_angle must be between 0 and 360")

        if not isinstance(base_mix, int) or isinstance(base_mix, bool):
            raise TypeError("base_mix must be an int")
        if not 0 <= base_mix <= 100:
            raise ValueError("base_mix must be between 0 and 100")

        if base_theme is not None and not isinstance(
            base_theme, SharedClientThemeBaseType
        ):
            raise TypeError("base_theme must be a SharedClientThemeBaseType or None")

        self.colors: list[str] = normalized
        self.gradient_angle: int = gradient_angle
        self.base_mix: int = base_mix
        self.base_theme: SharedClientThemeBaseType | None = base_theme

    def __repr__(self) -> str:
        return (
            f"<SharedClientTheme colors={self.colors!r} "
            f"gradient_angle={self.gradient_angle} base_mix={self.base_mix} "
            f"base_theme={self.base_theme!r}>"
        )

    def to_dict(self) -> SharedClientThemePayload:
        payload: SharedClientThemePayload = {
            "colors": list(self.colors),
            "gradient_angle": self.gradient_angle,
            "base_mix": self.base_mix,
        }
        if self.base_theme is not None:
            payload["base_theme"] = self.base_theme.value
        return payload

    @classmethod
    def from_dict(cls, data: SharedClientThemePayload) -> SharedClientTheme:
        base_theme_value = data.get("base_theme")
        return cls(
            colors=data.get("colors", []),
            gradient_angle=data["gradient_angle"],
            base_mix=data["base_mix"],
            base_theme=(
                try_enum(SharedClientThemeBaseType, base_theme_value)
                if base_theme_value is not None
                else None
            ),
        )
