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

from typing import ClassVar

import pytest

import discord
from discord.types.components import (
    OverflowMenuComponent as OverflowMenuComponentPayload,
)
from discord.ui import (
    ActionRow,
    DesignerView,
    MenuActionItem,
    OverflowMenu,
    OverflowMenuGroup,
    Section,
    TextDisplay,
    action_item,
)


def make_item(i: int = 0, **kwargs) -> MenuActionItem:
    kwargs.setdefault("label", f"Item {i}")
    if "url" not in kwargs:
        kwargs.setdefault("custom_id", f"item_{i}")
    return MenuActionItem(**kwargs)


def make_group(n: int = 1, label: str | None = None, start: int = 0) -> OverflowMenuGroup:
    return OverflowMenuGroup(*(make_item(start + i) for i in range(n)), label=label)


class TestMenuActionItem:
    def test_basic_construction(self):
        item = MenuActionItem(label="Hello", custom_id="hello")
        assert item.label == "Hello"
        assert item.custom_id == "hello"
        assert item.url is None
        assert item.style is discord.MenuActionItemStyle.default

    def test_danger_style(self):
        item = MenuActionItem(
            label="Danger", custom_id="d", style=discord.MenuActionItemStyle.danger
        )
        assert item.style == discord.MenuActionItemStyle.danger

    def test_url_item(self):
        item = MenuActionItem(label="GitHub", url="https://github.com")
        assert item.url == "https://github.com"
        assert item.custom_id is None
        assert item.style is discord.MenuActionItemStyle.link

    def test_url_and_custom_id_conflict(self):
        with pytest.raises(TypeError):
            MenuActionItem(url="https://github.com", custom_id="x")

    @pytest.mark.parametrize(
        "emoji",
        [
            "🐙",
            discord.PartialEmoji(name="octopus"),
            "<:emoji:1179511942310797433>",
        ],
    )
    def test_valid_emoji(self, emoji):
        item = MenuActionItem(emoji=emoji)
        assert isinstance(item.emoji, discord.PartialEmoji)

    def test_invalid_emoji_type(self):
        with pytest.raises(TypeError, match="emoji"):
            MenuActionItem(emoji=123)  # type: ignore

    def test_disabled_flag(self):
        item = MenuActionItem(disabled=True)
        assert item.disabled is True
        item.disabled = False
        assert item.disabled is False

    def test_to_dict(self):
        item = MenuActionItem(
            label="Hi", custom_id="hi", style=discord.MenuActionItemStyle.danger, id=0, disabled=False, 
        )
        payload = item.to_component_dict()
        assert payload["label"] == "Hi"
        assert payload["custom_id"] == "hi"
        assert payload["style"] == discord.MenuActionItemStyle.danger.value
        assert payload["id"] == 0
        assert payload["disabled"] is False
        assert "url" not in payload
        assert payload["type"] == discord.ComponentType.menu_action_item.value

    def test_to_dict_url_item(self):
        payload = MenuActionItem(url="https://github.com").to_component_dict()
        assert payload["url"] == "https://github.com"
        assert payload["style"] == discord.MenuActionItemStyle.link.value
        assert "custom_id" not in payload

    async def test_callback_is_invoked(self):
        calls = []

        class Custom(MenuActionItem):
            async def callback(self, interaction):
                calls.append(interaction)

        item = Custom(label="x", custom_id="x")
        sentinel = object()
        await item.callback(sentinel)
        assert calls == [sentinel]


# --------------------------------------------------------------------------- #
# OverflowMenuGroup
# --------------------------------------------------------------------------- #


class TestOverflowMenuGroup:
    def test_empty_group(self):
        group = OverflowMenuGroup()
        assert len(group.components) == 0

    def test_group_with_items_and_label(self):
        group = make_group(3, label="Actions")
        assert group.label == "Actions"
        assert len(group.components) == 3

    def test_group_rejects_wrong_type(self):
        with pytest.raises(TypeError, match="MenuActionItem"):
            OverflowMenuGroup(discord.ui.Button(label="no"))  # type: ignore

    def test_group_max_8_items(self):
        group = make_group(8)
        assert len(group.components) == 8
        with pytest.raises(ValueError, match="8"):
            group.add_item(make_item(99))

    def test_group_constructor_over_limit(self):
        with pytest.raises(ValueError, match="8"):
            make_group(9)

    def test_add_and_remove_item(self):
        group = OverflowMenuGroup()
        item = make_item(1)
        group.add_item(item)
        assert item in group.components
        group.remove_item(item)
        assert item not in group.components

    def test_get_item_by_custom_id(self):
        group = make_group(3)
        assert group.get_item("item_1") is not None
        assert group.get_item("does_not_exist") is None

    def test_to_dict(self):
        payload = make_group(2, label="Menu").to_component_dict()
        assert payload["label"] == "Menu"
        assert len(payload["components"]) == 2

    def test_to_dict_without_label(self):
        payload = make_group(1).to_component_dict()
        assert "label" not in payload

    def test_decorated_items_are_collected(self):
        class MyGroup(OverflowMenuGroup):
            @action_item(label="One", custom_id="one")
            async def one(self, item, interaction): ...

            @action_item(label="Two", custom_id="two")
            async def two(self, item, interaction): ...

        group = MyGroup()
        ids = [c.custom_id for c in group.components]
        assert ids == ["one", "two"]

    def test_decorated_and_constructor_items_combine(self):
        class MyGroup(OverflowMenuGroup):
            def __init__(self):
                super().__init__(MenuActionItem(label="GH", url="https://github.com"))

            @action_item(label="Deco", custom_id="deco")
            async def deco(self, item, interaction): ...

        group = MyGroup()
        assert len(group.components) == 2

    async def test_decorated_item_callback_receives_args(self):
        received = {}

        class MyGroup(OverflowMenuGroup):
            @action_item(label="x", custom_id="x")
            async def handler(self, item, interaction):
                received["item"] = item
                received["interaction"] = interaction

        group = MyGroup()
        item = group.get_item("x")
        sentinel = object()
        await item.callback(sentinel)  # type: ignore
        assert received["interaction"] is sentinel
        assert received["item"] is item

    def test_instances_do_not_share_items(self):
        class MyGroup(OverflowMenuGroup):
            @action_item(label="x", custom_id="x")
            async def handler(self, item, interaction): ...

        a, b = MyGroup(), MyGroup()
        a.handler.custom_id = "changed"
        assert b.handler.custom_id == "x"

    def test_disable_all_items(self):
        group = make_group(3)
        assert not any(i.disabled for i in group.components)

        group.disable_all_items()
        assert all(i.disabled for i in group.components)

        group.enable_all_items()
        assert not any(i.disabled for i in group.components)

    def test_disable_all_items_with_exclusions(self):
        group = make_group(3)
        item = group.get_item("item_1")
        assert item is not None
        assert not any(i.disabled for i in group.components)

        group.disable_all_items(exclusions=[item])
        assert all(((not i.disabled) if i.custom_id == "item_1" else i.disabled) for i in group.components)
        assert not item.disabled

        item.disabled = True
        assert all(i.disabled for i in group.components)
        group.enable_all_items(exclusions=[item])
        assert not any(((not i.disabled) if i.custom_id == "item_1" else i.disabled) for i in group.components)




class TestOverflowMenu:
    def test_construction(self):
        menu = OverflowMenu(make_group(1), make_group(1, start=10))
        assert len(menu.groups) == 2

    def test_type(self):
        assert OverflowMenu(make_group(1)).type == discord.ComponentType.overflow_menu

    def test_rejects_wrong_type(self):
        with pytest.raises(TypeError, match="OverflowMenuGroup"):
            OverflowMenu(make_item(1))  # type: ignore

    def test_max_8_groups(self):
        menu = OverflowMenu(*(make_group(1, start=i) for i in range(8)))
        with pytest.raises(ValueError, match="8"):
            menu.add_item(make_group(1, start=100))

    async def test_constructor_over_limit(self):
        with pytest.raises(ValueError, match="8"):
            OverflowMenu(*(make_group(1, start=i) for i in range(9)))

    async def test_add_and_remove_item(self):
        menu = OverflowMenu()
        group = make_group(1)
        menu.add_item(group)
        assert group in menu.groups
        menu.remove_item(group)
        assert group not in menu.groups

    def test_add_group(self):
        menu = OverflowMenu()
        items =[make_item(i) for i in range(3)]
        menu.add_group(*items, label="Hi")
        assert len(menu.groups) == 1
        assert len(menu.groups[0].components) == 3
        assert menu.groups[0].label == "Hi"

    async def test_get_item_searches_all_groups(self):
        menu = OverflowMenu(make_group(2, start=0), make_group(2, start=10))
        assert menu.get_item("item_11") is not None
        assert menu.get_item("nope") is None

    async def test_disable_all_items(self):
        menu = OverflowMenu(make_group(2, start=0), make_group(2, start=10))
        assert not any(i.disabled for i in menu.walk_items())
        menu.disable_all_items()
        assert all(i.disabled for i in menu.walk_items())
        menu.enable_all_items()
        assert not any(i.disabled for i in menu.walk_items())


    def test_disable_all_items_with_exclusions(self):
        menu = OverflowMenu(make_group(2, start=0), make_group(2, start=10))
        item = menu.get_item("item_1")
        assert item is not None
        assert not any(i.disabled for i in menu.walk_items())

        menu.disable_all_items(exclusions=[item])
        assert all(((not i.disabled) if i.custom_id == "item_1" else i.disabled) for i in menu.walk_items())
        assert not item.disabled

        item.disabled = True
        assert all(i.disabled for i in menu.walk_items())
        menu.enable_all_items(exclusions=[item])
        assert not any(((not i.disabled) if i.custom_id == "item_1" else i.disabled) for i in menu.walk_items())

    async def test_to_dict(self):
        payload = OverflowMenu(make_group(2, label="A"), make_group(1, start=5)).to_component_dict()
        assert payload["type"] == discord.ComponentType.overflow_menu.value
        assert len(payload["groups"]) == 2
        assert payload["groups"][0]["label"] == "A"

    async def test_subclass_pattern(self):
        class BasicOverflow(OverflowMenu):
            def __init__(self, index: int):
                super().__init__(make_group(2, start=index * 10))

        assert len(BasicOverflow(1).groups) == 1


class TestDesignerViewIntegration:
    async def test_in_action_row(self):
        view = DesignerView(timeout=None)
        view.add_item(ActionRow(OverflowMenu(make_group(1))))
        assert view.is_components_v2()
        assert view.is_dispatchable()
        assert view.is_persistent()

    async def test_as_section_accessory(self):
        view = DesignerView(timeout=None)
        view.add_item(Section(TextDisplay("Test"), accessory=OverflowMenu(make_group(1))))
        assert view.is_components_v2()
        assert view.is_dispatchable()
        assert view.is_persistent()

    async def test_inside_container(self):
        view = DesignerView(timeout=None)
        view.add_item(
            discord.ui.Container(
                ActionRow(OverflowMenu(make_group(1))),
                Section(TextDisplay("x"), accessory=OverflowMenu(make_group(1, start=5))),
            )
        )
        assert view.is_components_v2()
        assert view.is_dispatchable()
        assert view.is_persistent()

    async def test_not_persistent_with_timeout(self):
        view = DesignerView(timeout=180)
        view.add_item(ActionRow(OverflowMenu(make_group(1))))
        assert not view.is_persistent()

    async def test_get_item_finds_nested_menu_item(self):
        view = DesignerView(timeout=None)
        view.add_item(ActionRow(OverflowMenu(make_group(2))))
        assert view.get_item("item_1") is not None

    async def test_get_item_inside_container_and_section(self):
        view = DesignerView(timeout=None)
        view.add_item(
            discord.ui.Container(
                Section(TextDisplay("x"), accessory=OverflowMenu(make_group(1, start=7)))
            )
        )
        assert view.get_item("item_7") is not None

    async def test_remove_item_by_custom_id(self):
        view = DesignerView(timeout=None)
        view.add_item(ActionRow(OverflowMenu(make_group(2))))
        view.remove_item("item_0")
        assert view.get_item("item_0") is None
        assert view.get_item("item_1") is not None

    async def test_to_components(self):
        view = DesignerView(timeout=None)
        view.add_item(ActionRow(OverflowMenu(make_group(1, label="L"))))
        payload = view.to_components()
        assert len(payload) == 1
        menu = payload[0]["components"][0]
        assert menu["type"] == discord.ComponentType.overflow_menu.value
        assert menu["groups"][0]["label"] == "L"



class TestComponentModels:
    PAYLOAD: ClassVar[OverflowMenuComponentPayload] = {
        "type": discord.ComponentType.overflow_menu.value,
        "id": 3,
        "groups": [
            {
                "label": "Group",
                "components": [
                    {"type": discord.ComponentType.menu_action_item.value, "label": "A", "custom_id": "a", "style": discord.MenuActionItemStyle.default.value, "disabled": False},
                    {"type": discord.ComponentType.menu_action_item.value, "label": "GH", "url": "https://github.com", "style": discord.MenuActionItemStyle.link.value, "disabled": False},
                ],
            },
            {
                "components": [
                    {"type": discord.ComponentType.menu_action_item.value, "label": "B", "custom_id": "b", "style": discord.MenuActionItemStyle.danger.value, "disabled": True},
                    {"type": discord.ComponentType.menu_action_item.value, "label": "GH", "url": "https://github.com", "style": discord.MenuActionItemStyle.link.value, "disabled": True},
                ],
            }
        ],
    }

    async def test_component_from_payload(self):
        from discord.components import OverflowMenu as OverflowMenuComponent

        component = OverflowMenuComponent(self.PAYLOAD)
        assert component.type == discord.ComponentType.overflow_menu
        assert component.id == 3
        assert len(component.groups) == 2
        assert component.groups[0].label == "Group"
        assert len(component.groups[0].components) == 2
        # A
        component_a = component.groups[0].components[0]
        assert component_a.type == discord.ComponentType.menu_action_item
        assert component_a.label == "A"
        assert component_a.custom_id == "a"
        assert component_a.style == discord.MenuActionItemStyle.default
        assert component_a.url is None
        assert not component_a.disabled
        # GH
        component_gh = component.groups[0].components[1]
        assert component_gh.type == discord.ComponentType.menu_action_item
        assert component_gh.label == "GH"
        assert component_gh.custom_id is None
        assert component_gh.style == discord.MenuActionItemStyle.link
        assert component_gh.url == "https://github.com"
        assert not component_gh.disabled

        assert component.groups[1].label is None
        assert len(component.groups[1].components) == 2
        # B
        component_b = component.groups[1].components[0]
        assert component_b.type == discord.ComponentType.menu_action_item
        assert component_b.label == "B"
        assert component_b.custom_id == "b"
        assert component_b.style == discord.MenuActionItemStyle.danger
        assert component_b.url is None
        assert component_b.disabled

    async def test_component_to_dict_roundtrip(self):
        from discord.components import OverflowMenu as OverflowMenuComponent

        out = OverflowMenuComponent(self.PAYLOAD).to_dict()
        assert out == self.PAYLOAD