.. _discord_ui_kit:

Bot UI Kit
==========

The library has helpers to help create component-based UIs.


Shortcut decorators
-------------------

.. autofunction:: discord.ui.button
    :decorator:

.. autofunction:: discord.ui.select
    :decorator:

.. autofunction:: discord.ui.string_select
    :decorator:

.. autofunction:: discord.ui.user_select
    :decorator:

.. autofunction:: discord.ui.role_select
    :decorator:

.. autofunction:: discord.ui.mentionable_select
    :decorator:

.. autofunction:: discord.ui.channel_select
    :decorator:

Objects
-------

.. attributetable:: discord.ui.BaseView

.. autoclass:: discord.ui.BaseView
    :members:

.. attributetable:: discord.ui.View

.. autoclass:: discord.ui.View
    :members:

.. attributetable:: discord.ui.DesignerView

.. autoclass:: discord.ui.DesignerView
    :members:

.. attributetable:: discord.ui.Item

.. autoclass:: discord.ui.Item
    :members:

.. attributetable:: discord.ui.ActionRow

.. autoclass:: discord.ui.ActionRow
    :members:
    :inherited-members:

.. attributetable:: discord.ui.Button

.. autoclass:: discord.ui.Button
    :members:
    :inherited-members:

.. attributetable:: discord.ui.Select

.. autoclass:: discord.ui.Select
    :members:
    :inherited-members:


.. class:: discord.ui.StringSelect

    An alias for :class:`Select` with ``select_type`` as :attr:`discord.ComponentType.string_select`.

.. class:: discord.ui.UserSelect

    An alias for :class:`Select` with ``select_type`` as :attr:`discord.ComponentType.user_select`.

.. class:: discord.ui.RoleSelect

    An alias for :class:`Select` with ``select_type`` as :attr:`discord.ComponentType.role_select`.

.. class:: discord.ui.MentionableSelect

    An alias for :class:`Select` with ``select_type`` as :attr:`discord.ComponentType.mentionable_select`.

.. class:: discord.ui.ChannelSelect

    An alias for :class:`Select` with ``select_type`` as :attr:`discord.ComponentType.channel_select`.

.. attributetable:: discord.ui.Section

.. autoclass:: discord.ui.Section
    :members:
    :inherited-members:

.. attributetable:: discord.ui.TextDisplay

.. autoclass:: discord.ui.TextDisplay
    :members:
    :inherited-members:

.. attributetable:: discord.ui.Thumbnail

.. autoclass:: discord.ui.Thumbnail
    :members:
    :inherited-members:

.. attributetable:: discord.ui.MediaGallery

.. autoclass:: discord.ui.MediaGallery
    :members:
    :inherited-members:

.. attributetable:: discord.ui.File

.. autoclass:: discord.ui.File
    :members:
    :inherited-members:

.. attributetable:: discord.ui.Separator

.. autoclass:: discord.ui.Separator
    :members:
    :inherited-members:

.. attributetable:: discord.ui.Container

.. autoclass:: discord.ui.Container
    :members:
    :inherited-members:

.. attributetable:: discord.ui.BaseModal

.. autoclass:: discord.ui.BaseModal
    :members:
    :inherited-members:

.. attributetable:: discord.ui.Modal

.. autoclass:: discord.ui.Modal
    :members:
    :inherited-members:

.. attributetable:: discord.ui.DesignerModal

.. autoclass:: discord.ui.DesignerModal
    :members:
    :inherited-members:

.. attributetable:: discord.ui.Label

.. autoclass:: discord.ui.Label
    :members:
    :inherited-members:

.. attributetable:: discord.ui.InputText

.. autoclass:: discord.ui.InputText
    :members:
    :inherited-members:
