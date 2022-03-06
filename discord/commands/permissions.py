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

from typing import Callable, Dict, Union

__all__ = (
    "CommandPermission",
    "has_role",
    "has_any_role",
    "is_user",
    "is_owner",
    "permission",
)


class CommandPermission:
    """The class used in the application command decorators
    to hash permission data into a dictionary using the
    :meth:`to_dict` method to be sent to the discord API later on.

    .. versionadded:: 2.0

    Attributes
    -----------
    id: Union[:class:`int`, :class:`str`]
        A string or integer that represents or helps get
        the id of the user or role that the permission is tied to.
    type: :class:`int`
        An integer representing the type of the permission.
    permission: :class:`bool`
        A boolean representing the permission's value.
    guild_id: :class:`int`
        The integer which represents the id of the guild that the
        permission may be tied to.
    """

    def __init__(
        self,
        id: Union[int, str],
        type: int,
        permission: bool = True,
        guild_id: int = None,
    ):
        self.id = id
        self.type = type
        self.permission = permission
        self.guild_id = guild_id

    def to_dict(self) -> Dict[str, Union[int, bool]]:
        return {"id": self.id, "type": self.type, "permission": self.permission}


def permission(
    role_id: int = None,
    user_id: int = None,
    permission: bool = True,
    guild_id: int = None,
):
    """The method used to specify application command permissions
    for specific users or roles using their id.

    This method is meant to be used as a decorator.

    .. versionadded:: 2.0

    Parameters
    -----------
    role_id: :class:`int`
        An integer which represents the id of the role that the
        permission may be tied to.
    user_id: :class:`int`
        An integer which represents the id of the user that the
        permission may be tied to.
    permission: :class:`bool`
        A boolean representing the permission's value.
    guild_id: :class:`int`
        The integer which represents the id of the guild that the
        permission may be tied to.
    """

    def decorator(func: Callable):
        if not role_id is None:
            app_cmd_perm = CommandPermission(role_id, 1, permission, guild_id)
        elif not user_id is None:
            app_cmd_perm = CommandPermission(user_id, 2, permission, guild_id)
        else:
            raise ValueError("role_id or user_id must be specified!")

        # Create __app_cmd_perms__
        if not hasattr(func, "__app_cmd_perms__"):
            func.__app_cmd_perms__ = []

        # Append
        func.__app_cmd_perms__.append(app_cmd_perm)

        return func

    return decorator


def has_role(item: Union[int, str], guild_id: int = None):
    """The method used to specify application command role restrictions.

    This method is meant to be used as a decorator.

    .. versionadded:: 2.0

    Parameters
    -----------
    item: Union[:class:`int`, :class:`str`]
        An integer or string that represent the id or name of the role
        that the permission is tied to.
    guild_id: :class:`int`
        The integer which represents the id of the guild that the
        permission may be tied to.
    """

    def decorator(func: Callable):
        # Create __app_cmd_perms__
        if not hasattr(func, "__app_cmd_perms__"):
            func.__app_cmd_perms__ = []

        # Permissions (Will Convert ID later in register_commands if needed)
        app_cmd_perm = CommandPermission(item, 1, True, guild_id)  # {"id": item, "type": 1, "permission": True}

        # Append
        func.__app_cmd_perms__.append(app_cmd_perm)

        return func

    return decorator


def has_any_role(*items: Union[int, str], guild_id: int = None):
    """The method used to specify multiple application command role restrictions,
    The application command runs if the invoker has **any** of the specified roles.

    This method is meant to be used as a decorator.

    .. versionadded:: 2.0

    Parameters
    -----------
    *items: Union[:class:`int`, :class:`str`]
        The integers or strings that represent the ids or names of the roles
        that the permission is tied to.
    guild_id: :class:`int`
        The integer which represents the id of the guild that the
        permission may be tied to.
    """

    def decorator(func: Callable):
        # Create __app_cmd_perms__
        if not hasattr(func, "__app_cmd_perms__"):
            func.__app_cmd_perms__ = []

        # Permissions (Will Convert ID later in register_commands if needed)
        for item in items:
            app_cmd_perm = CommandPermission(item, 1, True, guild_id)  # {"id": item, "type": 1, "permission": True}

            # Append
            func.__app_cmd_perms__.append(app_cmd_perm)

        return func

    return decorator


def is_user(user: int, guild_id: int = None):
    """The method used to specify application command user restrictions.

    This method is meant to be used as a decorator.

    .. versionadded:: 2.0

    Parameters
    -----------
    user: :class:`int`
        An integer that represent the id of the user that the permission is tied to.
    guild_id: :class:`int`
        The integer which represents the id of the guild that the
        permission may be tied to.
    """

    def decorator(func: Callable):
        # Create __app_cmd_perms__
        if not hasattr(func, "__app_cmd_perms__"):
            func.__app_cmd_perms__ = []

        # Permissions (Will Convert ID later in register_commands if needed)
        app_cmd_perm = CommandPermission(user, 2, True, guild_id)  # {"id": user, "type": 2, "permission": True}

        # Append
        func.__app_cmd_perms__.append(app_cmd_perm)

        return func

    return decorator


def is_owner(guild_id: int = None):
    """The method used to limit application commands exclusively
    to the owner of the bot.

    This method is meant to be used as a decorator.

    .. versionadded:: 2.0

    Parameters
    -----------
    guild_id: :class:`int`
        The integer which represents the id of the guild that the
        permission may be tied to.
    """

    def decorator(func: Callable):
        # Create __app_cmd_perms__
        if not hasattr(func, "__app_cmd_perms__"):
            func.__app_cmd_perms__ = []

        # Permissions (Will Convert ID later in register_commands if needed)
        app_cmd_perm = CommandPermission("owner", 2, True, guild_id)  # {"id": "owner", "type": 2, "permission": True}

        # Append
        func.__app_cmd_perms__.append(app_cmd_perm)

        return func

    return decorator
