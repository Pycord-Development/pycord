# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project does not adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.1] - 2022-08-25
### Fixed
- Bridge command detection in cogs. ([#1592](https://github.com/Pycord-Development/pycord/pull/1592))

## [2.1.0] - 2022-08-25
### Added
- Support for add, sub, union, intersect, and inverse operations on classes inheriting from `BaseFlags`.
  ([#1486](https://github.com/Pycord-Development/pycord/pull/1486))
- A `disable_on_timeout` kwarg in the `View` constructor.
  ([#1492](https://github.com/Pycord-Development/pycord/pull/1492))
- New `mention` property for `SlashCommand` objects, allowing a shortcut for the new command markdown syntax.
  ([#1523](https://github.com/Pycord-Development/pycord/pull/1523))
- An `app_commands_badge` value on `ApplicationFlags`. ([#1535](https://github.com/Pycord-Development/pycord/pull/1535)
  and [#1553](https://github.com/Pycord-Development/pycord/pull/1553))
- A new `fetch_application` method in the `Client` object.
  ([#1536](https://github.com/Pycord-Development/pycord/pull/1536))
- New `on_check_failure` event method for the `View` class.
  ([#799](https://github.com/Pycord-Development/pycord/pull/799))
- A `set_mfa_required` method to `Guild`. ([#1552](https://github.com/Pycord-Development/pycord/pull/1552))
- Support for command groups with bridge commands. ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- Support for `Attachment` type options for bridge commands.
  ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- `is_app` property for `BridgeContext` to better differentiate context types.
  ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- Support for localization on bridge commands. ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- A `filter_params` helper function in `discord.utils`.
  ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- Support for `InteractionMessage` via the `message` property of `View`.
  ([#1492](https://github.com/Pycord-Development/pycord/pull/1492))

### Changed
- Use `slash_variant` and `ext_variant` attributes instead of `get_application_command()` and `get_ext_command()`
  methods on `BridgeCommand`. ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- Set `store` kwarg default to `False` in load_extension(s) method.
  ([#1520](https://github.com/Pycord-Development/pycord/pull/1520))
- `commands.has_permissions()` check now returns `True` in DM channels.
  ([#1577](https://github.com/Pycord-Development/pycord/pull/1577))

### Fixed
- Fix `VoiceChannel`/`CategoryChannel` data being invalidated on `Option._invoke`.
  ([#1490](https://github.com/Pycord-Development/pycord/pull/1490))
- Fix type issues in options.py ([#1473](https://github.com/Pycord-Development/pycord/pull/1473))
- Fix KeyError on AutoModActionExecution when the bot lacks the Message Content Intent.
  ([#1521](https://github.com/Pycord-Development/pycord/pull/1521))
- Large code/documentation cleanup & minor bug fixes. ([#1476](https://github.com/Pycord-Development/pycord/pull/1476))
- Fix `Option` with type `str` raising AttributeError when `min_length` or `max_length` kwargs are passed.
  ([#1527](https://github.com/Pycord-Development/pycord/pull/1527))
- Fix `load_extensions` parameters not being passed through correctly.
  ([#1537](https://github.com/Pycord-Development/pycord/pull/1537))
- Fix `SlashCommandGroup` descriptions to use the correct default string.
  ([#1539](https://github.com/Pycord-Development/pycord/pull/1539) and
  [#1586](https://github.com/Pycord-Development/pycord/pull/1586))
- Fix Enum type options breaking due to `from_datatype()` method & Fix minor typing import.
  ([#1541](https://github.com/Pycord-Development/pycord/pull/1541))
- Adjust category and guild `_channels` attributes to work with NoneType positions.
  ([#1530](https://github.com/Pycord-Development/pycord/pull/1530))
- Make `SelectOption.emoji` a property. ([#1550](https://github.com/Pycord-Development/pycord/pull/1550))
- Improve sticker creation by checking for minimum and maximum length on `name` and `description`.
  ([#1546](https://github.com/Pycord-Development/pycord/pull/1546))
- Fix threads created with a base message being set to the wrong `message_reference`.
  ([#1551](https://github.com/Pycord-Development/pycord/pull/1551))
- Avoid unnecessary call to `sync_commands` during runtime.
  ([#1563](https://github.com/Pycord-Development/pycord/pull/1563))
- Fix bug in `Modal.on_timeout()` by using `custom_id` to create timeout task.
  ([#1562](https://github.com/Pycord-Development/pycord/pull/1562))
- Respect limit argument in `Guild.bans()`. ([#1573](https://github.com/Pycord-Development/pycord/pull/1573))
- Fix `before` argument in `on_scheduled_event_update` event always set to `None` by converting ID to `int`.
  ([#1580](https://github.com/Pycord-Development/pycord/pull/1580))
- Fix `__eq__` method `ApplicationCommand` accidentally comparing to self.
  ([#1585](https://github.com/Pycord-Development/pycord/pull/1585))
- Apply `cog_check` method to `ApplicationCommand` invocations.
  ([#1575](https://github.com/Pycord-Development/pycord/pull/1575))
- Fix `Interaction.edit_original_message()` using `ConnectionState` instead of `InteractionMessageState`.
  ([#1565](https://github.com/Pycord-Development/pycord/pull/1565))
- Fix required parameters validation error ([#1589](https://github.com/Pycord-Development/pycord/pull/1589))

### Security
- Fix for application-based bots without the bot scope ([#1568](https://github.com/Pycord-Development/pycord/pull/1568)
  and [#1584](https://github.com/Pycord-Development/pycord/pull/1584))


[Unreleased]: https://github.com/Pycord-Development/pycord/compare/v2.1.1...HEAD
[2.1.1]: https://github.com/Pycord-Development/pycord/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/Pycord-Development/pycord/compare/v2.0.1...v2.1.0
