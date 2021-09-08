from typing import TypedDict, Optional, List, Union


class OptionChoice(TypedDict, total=False):
    name: str
    value: Union[str, int, float]


class Option(TypedDict, total=False):
    name: str
    description: str
    type: int
    required: bool
    choices: List[OptionChoice]


class SlashCommand(TypedDict, total=False):
    name: str
    description: str
    options: Option
    type: Optional[int]


class SlashCommandGroup(SlashCommand):
    pass


class ContextMenuCommand(TypedDict, total=False):
    name: str
    description: str
    type: int

