# A Test Which Imports Everything
# Mostly to help reduce issues with untested code that will not even parse/run on python3 or future versions
# EX: Code Might Run On Python 3.8/9 But Not On 3.10+


def test_import():
    import discord


def test_import_ext_bridge():
    import discord.ext.bridge


def test_import_ext_commands():
    import discord.ext.commands


def test_import_ext_pages():
    import discord.ext.pages


def test_import_ext_tasks():
    import discord.ext.tasks
