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

from typing import Union, Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types.interactions import (
        ApplicationCommandPermissions,
        ApplicationCommandPermissionType
    )
    from ..types.snowflake import Snowflake

__all__ = (
    "Permission",
    "has_role",
    "has_any_role",
    "is_user",
    "is_owner",
    "permission",
)


class Permission:
    def __init__(self, perm_id: Snowflake, perm_type: int, perm: bool = True, guild_id: Optional[int] = None):
        self.id: Snowflake = perm_id
        self.type: ApplicationCommandPermissionType = perm_type
        self.permission: bool = perm
        self.guild_id: Optional[int] = guild_id

    def to_dict(self) -> ApplicationCommandPermissions:
        return {"id": self.id, "type": self.type, "permission": self.permission}


def permission(role_id: int = None, user_id: int = None, perm: bool = True, guild_id: int = None):
    def decorator(func: Callable):
        if role_id is not None:
            app_cmd_perm = Permission(role_id, 1, perm, guild_id)
        elif not user_id is None:
            app_cmd_perm = Permission(user_id, 2, perm, guild_id)
        else:
            raise ValueError("role_id or user_id must be specified!")

        # Create __app_cmd_perms__
        if not hasattr(func, '__app_cmd_perms__'):
            func.__app_cmd_perms__ = []

        # Append
        func.__app_cmd_perms__.append(app_cmd_perm)

        return func

    return decorator


def has_role(item: Union[int, str], guild_id: int = None):
    def decorator(func: Callable):
        # Create __app_cmd_perms__
        if not hasattr(func, '__app_cmd_perms__'):
            func.__app_cmd_perms__ = []

        # Permissions (Will Convert ID later in register_commands if needed)
        app_cmd_perm = Permission(item, 1, True, guild_id)  # {"id": item, "type": 1, "permission": True}

        # Append
        func.__app_cmd_perms__.append(app_cmd_perm)

        return func

    return decorator


def has_any_role(*items: Union[int, str], guild_id: int = None):
    def decorator(func: Callable):
        # Create __app_cmd_perms__
        if not hasattr(func, '__app_cmd_perms__'):
            func.__app_cmd_perms__ = []

        # Permissions (Will Convert ID later in register_commands if needed)
        for item in items:
            app_cmd_perm = Permission(item, 1, True, guild_id)  # {"id": item, "type": 1, "permission": True}

            # Append
            func.__app_cmd_perms__.append(app_cmd_perm)

        return func

    return decorator


def is_user(user: int, guild_id: int = None):
    def decorator(func: Callable):
        # Create __app_cmd_perms__
        if not hasattr(func, '__app_cmd_perms__'):
            func.__app_cmd_perms__ = []

        # Permissions (Will Convert ID later in register_commands if needed)
        app_cmd_perm = Permission(user, 2, True, guild_id)  # {"id": user, "type": 2, "permission": True}

        # Append
        func.__app_cmd_perms__.append(app_cmd_perm)

        return func

    return decorator


def is_owner(guild_id: int = None):
    def decorator(func: Callable):
        # Create __app_cmd_perms__
        if not hasattr(func, '__app_cmd_perms__'):
            func.__app_cmd_perms__ = []

        # Permissions (Will Convert ID later in register_commands if needed)
        app_cmd_perm = Permission("owner", 2, True, guild_id)  # {"id": "owner", "type": 2, "permission": True}

        # Append
        func.__app_cmd_perms__.append(app_cmd_perm)

        return func

    return decorator
