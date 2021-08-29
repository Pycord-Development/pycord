import logging
import typing
import uuid

import discord

from ..context import ComponentContext
from ..error import IncorrectFormat, IncorrectType
from ..model import ButtonStyle, ComponentType

logger = logging.getLogger("discord_slash")


def create_actionrow(*components: dict) -> dict:
    """
    Creates an ActionRow for message components.

    :param components: Components to go within the ActionRow.
    :return: dict
    """
    if not components or len(components) > 5:
        raise IncorrectFormat("Number of components in one row should be between 1 and 5.")
    if (
        ComponentType.select in [component["type"] for component in components]
        and len(components) > 1
    ):
        raise IncorrectFormat("Action row must have only one select component and nothing else")

    return {"type": ComponentType.actionrow, "components": components}


def spread_to_rows(*components, max_in_row=5) -> typing.List[dict]:
    """
    A helper function that spreads your components into ``actionrows`` of a set size

    :param components: Components dicts (buttons or selects or existing actionrows) to spread. Use `None` to explicitly start a new row.
    :type components: dict
    :param max_in_row: Maximum number of elements in each row.
    :type max_in_row: int
    :return: list

    .. note:: An action_row can only have a maximum of 5 items in it
    """
    if not components or len(components) > 25:
        raise IncorrectFormat("Number of components should be between 1 and 25.")

    if max_in_row < 1 or max_in_row > 5:
        raise IncorrectFormat("max_in_row should be between 1 and 5.")

    rows = []
    button_row = []
    for component in list(components) + [None]:
        if component is not None and component["type"] == ComponentType.button:
            button_row.append(component)

            if len(button_row) == max_in_row:
                rows.append(create_actionrow(*button_row))
                button_row = []

            continue

        if button_row:
            rows.append(create_actionrow(*button_row))
            button_row = []

        if component is None:
            pass
        elif component["type"] == ComponentType.actionrow:
            rows.append(component)
        elif component["type"] == ComponentType.select:
            rows.append(create_actionrow(component))

    if len(rows) > 5:
        raise IncorrectFormat("Number of rows exceeds 5.")

    return rows


def emoji_to_dict(emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str]) -> dict:
    """
    Converts a default or custom emoji into a partial emoji dict.

    :param emoji: The emoji to convert.
    :type emoji: Union[discord.Emoji, discord.PartialEmoji, str]
    """
    if isinstance(emoji, discord.Emoji):
        emoji = {"name": emoji.name, "id": emoji.id, "animated": emoji.animated}
    elif isinstance(emoji, discord.PartialEmoji):
        emoji = emoji.to_dict()
    elif isinstance(emoji, str):
        emoji = {"name": emoji, "id": None}
    return emoji if emoji else {}


def create_button(
    style: typing.Union[ButtonStyle, int],
    label: str = None,
    emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str] = None,
    custom_id: str = None,
    url: str = None,
    disabled: bool = False,
) -> dict:
    """
    Creates a button component for use with the ``components`` field. Must be used within an ``actionRow`` to be used (see :meth:`create_actionrow`).

    .. note::
        At least a label or emoji is required for a button. You can have both, but not neither of them.

    :param style: Style of the button. Refer to :class:`ButtonStyle`.
    :type style: Union[ButtonStyle, int]
    :param label: The label of the button.
    :type label: Optional[str]
    :param emoji: The emoji of the button.
    :type emoji: Union[discord.Emoji, discord.PartialEmoji, dict]
    :param custom_id: The custom_id of the button. Needed for non-link buttons.
    :type custom_id: Optional[str]
    :param url: The URL of the button. Needed for link buttons.
    :type url: Optional[str]
    :param disabled: Whether the button is disabled or not. Defaults to `False`.
    :type disabled: bool
    :returns: :class:`dict`
    """
    if style == ButtonStyle.URL:
        if custom_id:
            raise IncorrectFormat("A link button cannot have a `custom_id`!")
        if not url:
            raise IncorrectFormat("A link button must have a `url`!")
    elif url:
        raise IncorrectFormat("You can't have a URL on a non-link button!")

    if not label and not emoji:
        raise IncorrectFormat("You must have at least a label or emoji on a button.")

    if custom_id is not None and not isinstance(custom_id, str):
        custom_id = str(custom_id)
        logger.warning(
            "Custom_id has been automatically converted to a string. Please use strings in future\n"
            "Note: Discord will always return custom_id as a string"
        )

    emoji = emoji_to_dict(emoji)

    data = {
        "type": ComponentType.button,
        "style": style,
    }

    if label:
        data["label"] = label
    if emoji:
        data["emoji"] = emoji
    if disabled:
        data["disabled"] = disabled

    if style == ButtonStyle.URL:
        data["url"] = url
    else:
        data["custom_id"] = custom_id or str(uuid.uuid4())

    return data


def create_select_option(
    label: str, value: str, emoji=None, description: str = None, default: bool = False
):
    """
    Creates an option for select components.

    :param label: The user-facing name of the option that will be displayed in discord client.
    :param value: The value that the bot will receive when this option is selected.
    :param emoji: The emoji of the option.
    :param description: An additional description of the option.
    :param default: Whether or not this is the default option.
    """
    emoji = emoji_to_dict(emoji)

    if not len(label) or len(label) > 100:
        raise IncorrectFormat("Label length should be between 1 and 100.")
    if not isinstance(value, str):
        value = str(value)
        logger.warning(
            "Value has been automatically converted to a string. Please use strings in future\n"
            "Note: Discord will always return value as a string"
        )
    if not len(value) or len(value) > 100:
        raise IncorrectFormat("Value length should be between 1 and 100.")
    if description is not None and len(description) > 100:
        raise IncorrectFormat("Description length must be 100 or lower.")

    return {
        "label": label,
        "value": value,
        "description": description,
        "default": default,
        "emoji": emoji,
    }


def create_select(
    options: typing.List[dict],
    custom_id: str = None,
    placeholder: typing.Optional[str] = None,
    min_values: typing.Optional[int] = None,
    max_values: typing.Optional[int] = None,
    disabled: bool = False,
):
    """
    Creates a select (dropdown) component for use with the ``components`` field. Must be inside an ActionRow to be used (see :meth:`create_actionrow`).

    :param options: The choices the user can pick from
    :param custom_id: A custom identifier, like buttons
    :param placeholder: Custom placeholder text if nothing is selected
    :param min_values: The minimum number of items that **must** be chosen
    :param max_values: The maximum number of items that **can** be chosen
    :param disabled: Disables this component. Defaults to ``False``.
    """
    if not len(options) or len(options) > 25:
        raise IncorrectFormat("Options length should be between 1 and 25.")

    return {
        "type": ComponentType.select,
        "options": options,
        "custom_id": custom_id or str(uuid.uuid4()),
        "placeholder": placeholder or "",
        "min_values": min_values,
        "max_values": max_values,
        "disabled": disabled,
    }


def get_components_ids(component: typing.Union[str, dict, list]) -> typing.Iterator[str]:
    """
    Returns generator with the ``custom_id`` of a component or list of components.

    :param component: Custom ID or component dict (actionrow or button) or list of the two.
    :returns: typing.Iterator[str]
    """

    if isinstance(component, str):
        yield component
    elif isinstance(component, dict):
        if component["type"] == ComponentType.actionrow:
            yield from (
                comp["custom_id"] for comp in component["components"] if "custom_id" in comp
            )
        elif "custom_id" in component:
            yield component["custom_id"]
    elif isinstance(component, list):
        # Either list of components (actionrows or buttons) or list of ids
        yield from (comp_id for comp in component for comp_id in get_components_ids(comp))
    else:
        raise IncorrectType(
            f"Unknown component type of {component} ({type(component)}). "
            f"Expected str, dict or list"
        )


def get_messages_ids(message: typing.Union[int, discord.Message, list]) -> typing.Iterator[int]:
    """
    Returns generator with the ``id`` of message or list messages.

    :param message: message ID or message object or list of previous two.
    :returns: typing.Iterator[int]
    """
    if isinstance(message, int):
        yield message
    elif isinstance(message, discord.Message):
        yield message.id
    elif isinstance(message, list):
        yield from (msg_id for msg in message for msg_id in get_messages_ids(msg))
    else:
        raise IncorrectType(
            f"Unknown component type of {message} ({type(message)}). "
            f"Expected discord.Message, int or list"
        )


async def wait_for_component(
    client: discord.Client,
    messages: typing.Union[discord.Message, int, list] = None,
    components: typing.Union[str, dict, list] = None,
    check=None,
    timeout=None,
) -> ComponentContext:
    """
    Helper function - wrapper around 'client.wait_for("component", ...)'

    Waits for a component interaction. Only accepts interactions based on the custom ID of the component or/and message ID, and optionally a check function.

    :param client: The client/bot object.
    :type client: :class:`discord.Client`
    :param messages: The message object to check for, or the message ID or list of previous two.
    :type messages: Union[discord.Message, int, list]
    :param components: Custom ID to check for, or component dict (actionrow or button) or list of previous two.
    :type components: Union[str, dict, list]
    :param check: Optional check function. Must take a `ComponentContext` as the first parameter.
    :param timeout: The number of seconds to wait before timing out and raising :exc:`asyncio.TimeoutError`.
    :raises: :exc:`asyncio.TimeoutError`
    """

    if not (messages or components):
        raise IncorrectFormat("You must specify messages or components (or both)")

    message_ids = list(get_messages_ids(messages)) if messages else None
    custom_ids = list(get_components_ids(components)) if components else None

    # automatically convert improper custom_ids
    if custom_ids and not all(isinstance(x, str) for x in custom_ids):
        custom_ids = [str(i) for i in custom_ids]
        logger.warning(
            "Custom_ids have been automatically converted to a list of strings. Please use lists of strings in future.\n"
            "Note: Discord will always return custom_ids as strings"
        )

    def _check(ctx: ComponentContext):
        if check and not check(ctx):
            return False
        # if custom_ids is empty or there is a match
        wanted_message = not message_ids or ctx.origin_message_id in message_ids
        wanted_component = not custom_ids or ctx.custom_id in custom_ids
        return wanted_message and wanted_component

    return await client.wait_for("component", check=_check, timeout=timeout)
