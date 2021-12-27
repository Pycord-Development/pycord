# Guide
The Official Guide For Pycord

# Quick Tip
Pycord comes with automatic generation of files using your command prompt.

Example some commands you can use:

## ``python -m py-cord newbot (args)``

#### Args:

- name
  - Your Project Name
- --sharded
   - If your bot should be sharded or not
- --prefix
   - Your Bot Prefix

## ``python -m py-cord newcog (args)``

#### Args:

- name
   - The name of your Cog

- directory 
   - Cogs Directory

- --full
   - Get Full Features Of Cogs

- --class-name
   - Name of Your Cog Class 

## Before you begin...
Pycord has a lot of features which would be too advanced for a person just starting out with python,
We would suggest you get the basic knowledge of Python before starting there is a lot of tutorials to follow and we would suggest you start off with small projects then get bigger as you progress.

### How much python do i need to know?

- The difference between instances and class attributes.
    - e.g. `guild.name` vs `discord.Guild.name` or any variation of these.
- How to use data structures in the language.
    - `dict`/`tuple`/`list`/`str`/`...`
- How to solve `NameError` or `SyntaxError` exceptions.
- How to read and understand tracebacks.

This list **doesn't** fully cover everything you should know before using Pycord, We would suggest you at least know these before attempting to make a bot in Pycord.

## Guide List

```{eval-rst}
:doc:`starting-out/installing`

:doc:`starting-out/making-a-bot`

:doc:`starting-out/initial-files`

The Pycord :ref:`slash commands <interactions/slash_commands>` Guide.

The Pycord :ref:`Context Menus <interactions/context_menus>` Guide.

The Pycord :ref:`Button Menus <interactions/button_views>` Guide.

The Pycord :ref:`Select Menus <interactions/select_views>` Guide.

A thing you might wanna look at is :ref:`how to use ``ext.commands`` <ext/commands/index>`

A primer to :ref:`gateway intents <misc/intents>`

You may wanna try :doc:`misc/logging` in Pycord.
```
<!--:doc:`misc/webhooks` Guide, Finishing this isn't too important, if anyone wants they can finish it.-->
