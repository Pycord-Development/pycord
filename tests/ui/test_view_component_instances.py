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

import pytest

import discord
from discord.components import ActionRow as ActionRowComponent
from discord.components import Container as ContainerComponent


@pytest.mark.asyncio
async def test_view_component_instances_roundtrip():
    view = discord.ui.View(timeout=90.0)
    view.add_item(discord.ui.Button(label="Primary", custom_id="primary"))
    view.add_item(discord.ui.Button(label="Secondary", custom_id="secondary", row=1))

    components = view.to_component_instances()

    assert all(isinstance(component, ActionRowComponent) for component in components)

    restored = discord.ui.View.from_components(components, timeout=30.0)

    assert restored.timeout == 30.0
    assert restored.to_components() == view.to_components()


@pytest.mark.asyncio
async def test_designerview_component_instances_roundtrip():
    view = discord.ui.DesignerView(timeout=120.0)
    view.add_item(discord.ui.TextDisplay("Top level text"))
    view.add_item(
        discord.ui.ActionRow(
            discord.ui.Button(label="Inside row", custom_id="inside-row"),
        )
    )
    view.add_item(discord.ui.Container(discord.ui.TextDisplay("Nested text")))

    components = view.to_component_instances()

    assert any(isinstance(component, ContainerComponent) for component in components)

    restored = discord.ui.DesignerView.from_components(components, timeout=None)

    assert restored.timeout is None
    assert restored.to_components() == view.to_components()


@pytest.mark.asyncio
async def test_existing_dict_roundtrip_unchanged():
    view = discord.ui.View(timeout=45.0)
    view.add_item(discord.ui.Button(label="Dict path", custom_id="dict-path"))

    payload = view.to_components()
    restored = discord.ui.View.from_dict(payload, timeout=None)

    assert restored.timeout is None
    assert restored.to_components() == payload
