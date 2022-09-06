# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project does not adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.2] - 2022-09-06
### Fixed
- Fix subcommands having MISSING cog attribute. ([#1594](https://github.com/Pycord-Development/pycord/pull/1594) &
  [#1605](https://github.com/Pycord-Development/pycord/pull/1605))

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
- Fix required parameters validation error. ([#1589](https://github.com/Pycord-Development/pycord/pull/1589))

### Security
- Improved fix for application-based bots without the bot scope
  ([#1584](https://github.com/Pycord-Development/pycord/pull/1584))

## [2.0.1] - 2022-08-16
### Security
- Fix for application-based bots without the bot scope ([#1568](https://github.com/Pycord-Development/pycord/pull/1568))

## [2.0.0] - 2022-07-08
### Added
- New `news` property on `TextChannel`. ([#1370](https://github.com/Pycord-Development/pycord/pull/1370))
- New `invisible` kwarg to `defer()` method. ([#1379](https://github.com/Pycord-Development/pycord/pull/1379))
- Support for audit log event type 121 `APPLICATION_COMMAND_PERMISSION_UPDATE`.
  ([#1424](https://github.com/Pycord-Development/pycord/pull/1424))
- New `ForumChannelConverter`. ([#1440](https://github.com/Pycord-Development/pycord/pull/1440))
- A shortcut `jump_url` property to users. ([#1444](https://github.com/Pycord-Development/pycord/pull/1444))
- Ability for webhooks to create forum posts. ([#1405](https://github.com/Pycord-Development/pycord/pull/1405))
- New `message` property to `View` ([#1446](https://github.com/Pycord-Development/pycord/pull/1446))
- Support for `error`, `before_invoke`, and `after_invoke` handlers on `BridgeCommand`.
  ([#1411](https://github.com/Pycord-Development/pycord/pull/1411))
- New `thread` property to `Message`. ([#1447](https://github.com/Pycord-Development/pycord/pull/1447))
- A `starting_message` property to `Thread`. ([#1447](https://github.com/Pycord-Development/pycord/pull/1447))
- An `app_permissions` property to `Interaction` and `ApplicationContext`.
  ([#1460](https://github.com/Pycord-Development/pycord/pull/1460))
- Support for loading folders in `load_extension`, and a new helper function `load_extensions`.
  ([#1423](https://github.com/Pycord-Development/pycord/pull/1423))
- Support for AutoMod ([#1316](https://github.com/Pycord-Development/pycord/pull/1316))
- Support for `min_length` and `max_length` kwargs in `Option`. ([#1463](https://github.com/Pycord-Development/pycord/pull/1463))
- Native timeout support for `Modal`. ([#1434](https://github.com/Pycord-Development/pycord/pull/1434))

### Changed
- Updated to new sticker limit for premium guilds. ([#1420](https://github.com/Pycord-Development/pycord/pull/1420))
- Replace deprecated endpoint in `HTTPClient.change_my_nickname`.
  ([#1426](https://github.com/Pycord-Development/pycord/pull/1426))
- Updated deprecated IDENTIFY packet connection properties.
  ([#1430](https://github.com/Pycord-Development/pycord/pull/1430))

### Removed
- `Guild.region` attribute (Deprecated on API, VoiceChannel.rtc_region should be used instead).
  ([#1429](https://github.com/Pycord-Development/pycord/pull/1429))

### Fixed
- Change `guild_only` to `dm_permission` in application command `to_dict` method.
  ([#1368](https://github.com/Pycord-Development/pycord/pull/1368))
- Fix `repr(ScheduledEventLocation)` raising TypeError.
  ([#1369](https://github.com/Pycord-Development/pycord/pull/1369))
- Fix `repr(TextChannel)` raising AttributeError. ([#1370](https://github.com/Pycord-Development/pycord/pull/1370))
- Fix application command validation. ([#1372](https://github.com/Pycord-Development/pycord/pull/1372))
- Fix scheduled event `cover` property raising AttributeError.
  ([#1381](https://github.com/Pycord-Development/pycord/pull/1381))
- Fix `SlashCommandGroup` treating optional arguments as required.
  ([#1386](https://github.com/Pycord-Development/pycord/pull/1386))
- Fix `remove_application_command` not always removing commands.
  ([#1391](https://github.com/Pycord-Development/pycord/pull/1391))
- Fix busy-loop in `DecodeManager` when decode queue is empty, causing 100% CPU consumption.
  ([#1395](https://github.com/Pycord-Development/pycord/pull/1395))
- Fix incorrect activities and permissions on `Interaction` and `Option` objects.
  ([#1365](https://github.com/Pycord-Development/pycord/pull/1365))
- Converted PartialMember `deaf` and `mute` from str annotation (incorrect) to bool annotation.
  ([#1424](https://github.com/Pycord-Development/pycord/pull/1424))
- Use `PUT` instead of `POST` in `HTTPClient.join_thread`.
  ([#1426](https://github.com/Pycord-Development/pycord/pull/1426))
- Fix enum options not setting `input_type` to a SlashCommandOptionType.
  ([#1428](https://github.com/Pycord-Development/pycord/pull/1428))
- Fixed TypeError when using thread options. ([#1427](https://github.com/Pycord-Development/pycord/pull/1427))
- Allow voice channels in PartialMessage. ([#1441](https://github.com/Pycord-Development/pycord/pull/1441))
- Fixed `AuditLogAction.target_type` for application command permission updates.
  ([#1445](https://github.com/Pycord-Development/pycord/pull/1445))
- Fix bridge commands to ignore the ephemeral kwarg. ([#1453](https://github.com/Pycord-Development/pycord/pull/1453))
- Update `thread.members` on `thread.fetch_members`. ([#1464](https://github.com/Pycord-Development/pycord/pull/1464))
- Fix error when discord doesn't send the `app_permissions` data in `Interaction`.
  ([#1467](https://github.com/Pycord-Development/pycord/pull/1467))
- Fix AttributeError when voice client `play()` function isn't completed yet.
  ([#1360](https://github.com/Pycord-Development/pycord/pull/1360))

[Unreleased]: https://github.com/Pycord-Development/pycord/compare/v2.1.1...HEAD
[2.1.2]: https://github.com/Pycord-Development/pycord/compare/v2.1.1...v2.1.2
[2.1.1]: https://github.com/Pycord-Development/pycord/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/Pycord-Development/pycord/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/Pycord-Development/pycord/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/Pycord-Development/pycord/compare/v2.0.0-rc.1...v2.0.0
[2.0.0-rc.1]: https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.7...v2.0.0-rc.1
[2.0.0-beta.7]: https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.6...v2.0.0-beta.7
[2.0.0-beta.6]: https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.5...v2.0.0-beta.6
[2.0.0-beta.5]: https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.4...v2.0.0-beta.5
[2.0.0-beta.4]: https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.3...v2.0.0-beta.4
[2.0.0-beta.3]: https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.2...v2.0.0-beta.3
[2.0.0-beta.2]: https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.1...v2.0.0-beta.2
[2.0.0-beta.1]: https://github.com/Pycord-Development/pycord/compare/v1.7.3...v2.0.0-beta.1
