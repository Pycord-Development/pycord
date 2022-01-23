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
The guide on how you can try :doc:`starting-out/installing>`

If you don't know how to make a bot in discord -> :doc:`starting-out/making-a-bot`

And if you don't know which files or what files to chose when starting we suggest you look at :doc:`starting-out/initial-files`

The Pycord :doc:`interactions/slash_commands` Guide.

The Pycord :doc:`interactions/context_menus` Guide.

The Pycord :doc:`interactions/button_views` Guide.

The Pycord :doc:`interactions/select_views` Guide.

A thing you might wanna look at is :doc:`ext/commands/index`.

:doc:`misc/intents`

You may wanna try :doc:`misc/logging` in Pycord.
```
<!--:doc:`misc/webhooks` Guide, Finishing this isn't too important, if anyone wants they can finish it.-->
