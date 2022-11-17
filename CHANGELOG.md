# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) when
possible (see our [Version Guarantees] for more info).

## [Unreleased]

These changes are available on the `master` branch, but have not yet been released.

### Added

- New brief Attribute to BridgeSlashCommand.
  ([#1676](https://github.com/Pycord-Development/pycord/pull/1676))
- Python 3.11 support. ([#1680](https://github.com/Pycord-Development/pycord/pull/1680))
- New select types `user`, `role`, `mentionable`, and `channel` - Along with their
  respective types and shortcut decorators.
  ([#1702](https://github.com/Pycord-Development/pycord/pull/1702))
- Added support for age-restricted (NSFW) commands.
  ([#1775](https://github.com/Pycord-Development/pycord/pull/1775))
- New flags: `PublicUserFlags.active_developer` & `ApplicationFlags.active`.
  ([#1776](https://github.com/Pycord-Development/pycord/pull/1776))
- Support for new forum features including tags, default slowmode, and default sort
  order. ([#1636](https://github.com/Pycord-Development/pycord/pull/1636))
- Support for new thread attributes `total_message_sent` and `is_pinned`.
  ([#1636](https://github.com/Pycord-Development/pycord/pull/1636))

### Fixed

- Fix bridge.has_permissions.
  ([#1695](https://github.com/Pycord-Development/pycord/pull/1695))
- Fix audit log overwrite type always resulting in `None`.
  ([#1716](https://github.com/Pycord-Development/pycord/pull/1716))
- Fixed error when using `suppress` kwarg in `send()`.
  ([#1719](https://github.com/Pycord-Development/pycord/pull/1719) &
  [#1723](https://github.com/Pycord-Development/pycord/pull/1723))

### Changed

- `get_application_command()` type kwarg now defaults to `ApplicationCommand`, so all
  command types can be retrieved by default.
  ([#1678](https://github.com/Pycord-Development/pycord/pull/1678))
- `get_application_command()` now supports retrieving subcommands and subcommand groups.
  ([#1678](https://github.com/Pycord-Development/pycord/pull/1678))

## [2.2.2] - 2022-10-05

### Fixed

- Fixed `parent` attribute of second level subcommands being set to the base level
  command instead of the direct parent.
  ([#1673](https://github.com/Pycord-Development/pycord/pull/1673))

## [2.2.1] - 2022-10-05

### Added

- New `SlashCommand.qualified_id` attribute.
  ([#1672](https://github.com/Pycord-Development/pycord/pull/1672))

### Fixed

- Fixed a `TypeError` in `ban()` methods related to the new `delete_message_seconds`
  parameter. ([#1666](https://github.com/Pycord-Development/pycord/pull/1666))
- Fixed broken `cog` and `parent` attributes on commands in cogs.
  ([#1662](https://github.com/Pycord-Development/pycord/pull/1662))
- Fixed `SlashCommand.mention` for subcommands.
  ([#1672](https://github.com/Pycord-Development/pycord/pull/1672))

## [2.2.0] - 2022-10-02

### Added

- New Guild Feature `INVITES_DISABLED`.
  ([#1613](https://github.com/Pycord-Development/pycord/pull/1613))
- `suppress` kwarg to `Messageable.send()`.
  ([#1587](https://github.com/Pycord-Development/pycord/pull/1587))
- `proxy` and `proxy_auth` params to many Webhook related methods.
  ([#1655](https://github.com/Pycord-Development/pycord/pull/1655))
- `delete_message_seconds` parameter in ban methods.
  ([#1557](https://github.com/Pycord-Development/pycord/pull/1557))
- New `View.get_item()` method.
  ([#1659](https://github.com/Pycord-Development/pycord/pull/1659))
- Permissions support for bridge commands.
  ([#1642](https://github.com/Pycord-Development/pycord/pull/1642))
- New `BridgeCommand.invoke()` method.
  ([#1642](https://github.com/Pycord-Development/pycord/pull/1642))
- New `raw_mentions`, `raw_role_mentions` and `raw_channel_mentions` functions in
  `discord.utils`. ([#1658](https://github.com/Pycord-Development/pycord/pull/1658))
- New methods `original_response`, `edit_original_response` & `delete_original_response`
  for `Interaction` objects.
  ([#1609](https://github.com/Pycord-Development/pycord/pull/1609))

### Deprecated

- The `delete_message_days` parameter in ban methods is now deprecated. Please use
  `delete_message_seconds` instead.
  ([#1557](https://github.com/Pycord-Development/pycord/pull/1557))
- The `original_message`, `edit_original_message` & `delete_original_message` methods
  for `Interaction` are now deprecated. Please use the respective `original_response`,
  `edit_original_response` & `delete_original_response` methods instead.
  ([#1609](https://github.com/Pycord-Development/pycord/pull/1609))

### Fixed

- Various fixes to ext.bridge groups.
  ([#1633](https://github.com/Pycord-Development/pycord/pull/1633) &
  [#1631](https://github.com/Pycord-Development/pycord/pull/1631))
- Fix `VOICE_SERVER_UPDATE` error.
  ([#1624](https://github.com/Pycord-Development/pycord/pull/1624))
- Removed unnecessary instance check in autocomplete.
  ([#1643](https://github.com/Pycord-Development/pycord/pull/1643))
- Interaction responses are now passed the respective `proxy` and `proxy_auth` params as
  defined in `Client`. ([#1655](https://github.com/Pycord-Development/pycord/pull/1655))

## [2.1.3] - 2022-09-06

### Fixed

- Fix TypeError in `process_application_commands`.
  ([#1622](https://github.com/Pycord-Development/pycord/pull/1622))

## [2.1.2] - 2022-09-06

### Fixed

- Fix subcommands having MISSING cog attribute.
  ([#1594](https://github.com/Pycord-Development/pycord/pull/1594) &
  [#1605](https://github.com/Pycord-Development/pycord/pull/1605))

## [2.1.1] - 2022-08-25

### Fixed

- Bridge command detection in cogs.
  ([#1592](https://github.com/Pycord-Development/pycord/pull/1592))

## [2.1.0] - 2022-08-25

### Added

- Support for add, sub, union, intersect, and inverse operations on classes inheriting
  from `BaseFlags`. ([#1486](https://github.com/Pycord-Development/pycord/pull/1486))
- A `disable_on_timeout` kwarg in the `View` constructor.
  ([#1492](https://github.com/Pycord-Development/pycord/pull/1492))
- New `mention` property for `SlashCommand` objects, allowing a shortcut for the new
  command markdown syntax.
  ([#1523](https://github.com/Pycord-Development/pycord/pull/1523))
- An `app_commands_badge` value on `ApplicationFlags`.
  ([#1535](https://github.com/Pycord-Development/pycord/pull/1535) and
  [#1553](https://github.com/Pycord-Development/pycord/pull/1553))
- A new `fetch_application` method in the `Client` object.
  ([#1536](https://github.com/Pycord-Development/pycord/pull/1536))
- New `on_check_failure` event method for the `View` class.
  ([#799](https://github.com/Pycord-Development/pycord/pull/799))
- A `set_mfa_required` method to `Guild`.
  ([#1552](https://github.com/Pycord-Development/pycord/pull/1552))
- Support for command groups with bridge commands.
  ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- Support for `Attachment` type options for bridge commands.
  ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- `is_app` property for `BridgeContext` to better differentiate context types.
  ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- Support for localization on bridge commands.
  ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- A `filter_params` helper function in `discord.utils`.
  ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- Support for `InteractionMessage` via the `message` property of `View`.
  ([#1492](https://github.com/Pycord-Development/pycord/pull/1492))

### Changed

- Use `slash_variant` and `ext_variant` attributes instead of
  `get_application_command()` and `get_ext_command()` methods on `BridgeCommand`.
  ([#1496](https://github.com/Pycord-Development/pycord/pull/1496))
- Set `store` kwarg default to `False` in load_extension(s) method.
  ([#1520](https://github.com/Pycord-Development/pycord/pull/1520))
- `commands.has_permissions()` check now returns `True` in DM channels.
  ([#1577](https://github.com/Pycord-Development/pycord/pull/1577))

### Fixed

- Fix `VoiceChannel`/`CategoryChannel` data being invalidated on `Option._invoke`.
  ([#1490](https://github.com/Pycord-Development/pycord/pull/1490))
- Fix type issues in options.py
  ([#1473](https://github.com/Pycord-Development/pycord/pull/1473))
- Fix KeyError on AutoModActionExecution when the bot lacks the Message Content Intent.
  ([#1521](https://github.com/Pycord-Development/pycord/pull/1521))
- Large code/documentation cleanup & minor bug fixes.
  ([#1476](https://github.com/Pycord-Development/pycord/pull/1476))
- Fix `Option` with type `str` raising AttributeError when `min_length` or `max_length`
  kwargs are passed. ([#1527](https://github.com/Pycord-Development/pycord/pull/1527))
- Fix `load_extensions` parameters not being passed through correctly.
  ([#1537](https://github.com/Pycord-Development/pycord/pull/1537))
- Fix `SlashCommandGroup` descriptions to use the correct default string.
  ([#1539](https://github.com/Pycord-Development/pycord/pull/1539) and
  [#1586](https://github.com/Pycord-Development/pycord/pull/1586))
- Fix Enum type options breaking due to `from_datatype()` method & Fix minor typing
  import. ([#1541](https://github.com/Pycord-Development/pycord/pull/1541))
- Adjust category and guild `_channels` attributes to work with NoneType positions.
  ([#1530](https://github.com/Pycord-Development/pycord/pull/1530))
- Make `SelectOption.emoji` a property.
  ([#1550](https://github.com/Pycord-Development/pycord/pull/1550))
- Improve sticker creation by checking for minimum and maximum length on `name` and
  `description`. ([#1546](https://github.com/Pycord-Development/pycord/pull/1546))
- Fix threads created with a base message being set to the wrong `message_reference`.
  ([#1551](https://github.com/Pycord-Development/pycord/pull/1551))
- Avoid unnecessary call to `sync_commands` during runtime.
  ([#1563](https://github.com/Pycord-Development/pycord/pull/1563))
- Fix bug in `Modal.on_timeout()` by using `custom_id` to create timeout task.
  ([#1562](https://github.com/Pycord-Development/pycord/pull/1562))
- Respect limit argument in `Guild.bans()`.
  ([#1573](https://github.com/Pycord-Development/pycord/pull/1573))
- Fix `before` argument in `on_scheduled_event_update` event always set to `None` by
  converting ID to `int`.
  ([#1580](https://github.com/Pycord-Development/pycord/pull/1580))
- Fix `__eq__` method `ApplicationCommand` accidentally comparing to self.
  ([#1585](https://github.com/Pycord-Development/pycord/pull/1585))
- Apply `cog_check` method to `ApplicationCommand` invocations.
  ([#1575](https://github.com/Pycord-Development/pycord/pull/1575))
- Fix `Interaction.edit_original_message()` using `ConnectionState` instead of
  `InteractionMessageState`.
  ([#1565](https://github.com/Pycord-Development/pycord/pull/1565))
- Fix required parameters validation error.
  ([#1589](https://github.com/Pycord-Development/pycord/pull/1589))

### Security

- Improved fix for application-based bots without the bot scope
  ([#1584](https://github.com/Pycord-Development/pycord/pull/1584))

## [2.0.1] - 2022-08-16

### Security

- Fix for application-based bots without the bot scope
  ([#1568](https://github.com/Pycord-Development/pycord/pull/1568))

## [2.0.0] - 2022-07-08

### Added

- New `news` property on `TextChannel`.
  ([#1370](https://github.com/Pycord-Development/pycord/pull/1370))
- New `invisible` kwarg to `defer()` method.
  ([#1379](https://github.com/Pycord-Development/pycord/pull/1379))
- Support for audit log event type 121 `APPLICATION_COMMAND_PERMISSION_UPDATE`.
  ([#1424](https://github.com/Pycord-Development/pycord/pull/1424))
- New `ForumChannelConverter`.
  ([#1440](https://github.com/Pycord-Development/pycord/pull/1440))
- A shortcut `jump_url` property to users.
  ([#1444](https://github.com/Pycord-Development/pycord/pull/1444))
- Ability for webhooks to create forum posts.
  ([#1405](https://github.com/Pycord-Development/pycord/pull/1405))
- New `message` property to `View`
  ([#1446](https://github.com/Pycord-Development/pycord/pull/1446))
- Support for `error`, `before_invoke`, and `after_invoke` handlers on `BridgeCommand`.
  ([#1411](https://github.com/Pycord-Development/pycord/pull/1411))
- New `thread` property to `Message`.
  ([#1447](https://github.com/Pycord-Development/pycord/pull/1447))
- A `starting_message` property to `Thread`.
  ([#1447](https://github.com/Pycord-Development/pycord/pull/1447))
- An `app_permissions` property to `Interaction` and `ApplicationContext`.
  ([#1460](https://github.com/Pycord-Development/pycord/pull/1460))
- Support for loading folders in `load_extension`, and a new helper function
  `load_extensions`. ([#1423](https://github.com/Pycord-Development/pycord/pull/1423))
- Support for AutoMod ([#1316](https://github.com/Pycord-Development/pycord/pull/1316))
- Support for `min_length` and `max_length` kwargs in `Option`.
  ([#1463](https://github.com/Pycord-Development/pycord/pull/1463))
- Native timeout support for `Modal`.
  ([#1434](https://github.com/Pycord-Development/pycord/pull/1434))

### Changed

- Updated to new sticker limit for premium guilds.
  ([#1420](https://github.com/Pycord-Development/pycord/pull/1420))
- Replace deprecated endpoint in `HTTPClient.change_my_nickname`.
  ([#1426](https://github.com/Pycord-Development/pycord/pull/1426))
- Updated deprecated IDENTIFY packet connection properties.
  ([#1430](https://github.com/Pycord-Development/pycord/pull/1430))

### Removed

- `Guild.region` attribute (Deprecated on API, VoiceChannel.rtc_region should be used
  instead). ([#1429](https://github.com/Pycord-Development/pycord/pull/1429))

### Fixed

- Change `guild_only` to `dm_permission` in application command `to_dict` method.
  ([#1368](https://github.com/Pycord-Development/pycord/pull/1368))
- Fix `repr(ScheduledEventLocation)` raising TypeError.
  ([#1369](https://github.com/Pycord-Development/pycord/pull/1369))
- Fix `repr(TextChannel)` raising AttributeError.
  ([#1370](https://github.com/Pycord-Development/pycord/pull/1370))
- Fix application command validation.
  ([#1372](https://github.com/Pycord-Development/pycord/pull/1372))
- Fix scheduled event `cover` property raising AttributeError.
  ([#1381](https://github.com/Pycord-Development/pycord/pull/1381))
- Fix `SlashCommandGroup` treating optional arguments as required.
  ([#1386](https://github.com/Pycord-Development/pycord/pull/1386))
- Fix `remove_application_command` not always removing commands.
  ([#1391](https://github.com/Pycord-Development/pycord/pull/1391))
- Fix busy-loop in `DecodeManager` when decode queue is empty, causing 100% CPU
  consumption. ([#1395](https://github.com/Pycord-Development/pycord/pull/1395))
- Fix incorrect activities and permissions on `Interaction` and `Option` objects.
  ([#1365](https://github.com/Pycord-Development/pycord/pull/1365))
- Converted PartialMember `deaf` and `mute` from str annotation (incorrect) to bool
  annotation. ([#1424](https://github.com/Pycord-Development/pycord/pull/1424))
- Use `PUT` instead of `POST` in `HTTPClient.join_thread`.
  ([#1426](https://github.com/Pycord-Development/pycord/pull/1426))
- Fix enum options not setting `input_type` to a SlashCommandOptionType.
  ([#1428](https://github.com/Pycord-Development/pycord/pull/1428))
- Fixed TypeError when using thread options.
  ([#1427](https://github.com/Pycord-Development/pycord/pull/1427))
- Allow voice channels in PartialMessage.
  ([#1441](https://github.com/Pycord-Development/pycord/pull/1441))
- Fixed `AuditLogAction.target_type` for application command permission updates.
  ([#1445](https://github.com/Pycord-Development/pycord/pull/1445))
- Fix bridge commands to ignore the ephemeral kwarg.
  ([#1453](https://github.com/Pycord-Development/pycord/pull/1453))
- Update `thread.members` on `thread.fetch_members`.
  ([#1464](https://github.com/Pycord-Development/pycord/pull/1464))
- Fix error when discord doesn't send the `app_permissions` data in `Interaction`.
  ([#1467](https://github.com/Pycord-Development/pycord/pull/1467))
- Fix AttributeError when voice client `play()` function isn't completed yet.
  ([#1360](https://github.com/Pycord-Development/pycord/pull/1360))

## [2.0.0-rc.1] - 2022-05-17

### Added

- A `delete_after` kwarg to `Paginator.send`.
  ([#1245](https://github.com/Pycord-Development/pycord/pull/1245))
- New `reason` kwarg to `Thread.delete_messages`.
  ([#1253](https://github.com/Pycord-Development/pycord/pull/1253))
- A new `jump_url` property to channel and thread objects.
  ([#1254](https://github.com/Pycord-Development/pycord/pull/1254) &
  [#1259](https://github.com/Pycord-Development/pycord/pull/1259))
- New `Paginator.edit()` method.
  ([#1258](https://github.com/Pycord-Development/pycord/pull/1258))
- An `EmbedField` object.
  ([#1181](https://github.com/Pycord-Development/pycord/pull/1181))
- Option names and descriptions are now validated locally.
  ([#1271](https://github.com/Pycord-Development/pycord/pull/1271))
- Component field limits are now enforced at library-level
  ([#1065](https://github.com/Pycord-Development/pycord/pull/1065) &
  [#1289](https://github.com/Pycord-Development/pycord/pull/1289))
- Support providing option channel types as list.
  ([#1000](https://github.com/Pycord-Development/pycord/pull/1000))
- New `Guild.jump_url` property.
  ([#1282](https://github.com/Pycord-Development/pycord/pull/1282))
- ext.pages now supports ext.bridge.
  ([#1288](https://github.com/Pycord-Development/pycord/pull/1288))
- Implement `None` check for check_guilds.
  ([#1291](https://github.com/Pycord-Development/pycord/pull/1291))
- A debug warning to catch deprecated perms v1 usage until v2 perms are implemented.
  ([#1301](https://github.com/Pycord-Development/pycord/pull/1301))
- A new `files` parameter to `Page` object.
  ([#1300](https://github.com/Pycord-Development/pycord/pull/1300))
- A `disable_all_items` and `enable_all_items` methods to `View` object.
  ([#1199](https://github.com/Pycord-Development/pycord/pull/1199) &
  [#1319](https://github.com/Pycord-Development/pycord/pull/1319))
- New `is_nsfw` attribute to voice channels.
  ([#1317](https://github.com/Pycord-Development/pycord/pull/1317))
- Support for Permissions v2.
  ([#1328](https://github.com/Pycord-Development/pycord/pull/1328))
- Allow using Enum to specify option choices.
  ([#1292](https://github.com/Pycord-Development/pycord/pull/1292))
- The `file` and `files` parameters to `InteractionResponse.edit_message()`.
  ([#1340](https://github.com/Pycord-Development/pycord/pull/1340))
- A `BridgeExtContext.delete()` method.
  ([#1348](https://github.com/Pycord-Development/pycord/pull/1348))
- Forum channels support.
  ([#1249](https://github.com/Pycord-Development/pycord/pull/1249))
- Implemented `Interaction.to_dict`.
  ([#1274](https://github.com/Pycord-Development/pycord/pull/1274))
- Support event covers for audit logs.
  ([#1355](https://github.com/Pycord-Development/pycord/pull/1355))

### Changed

- Removed implicit defer call in `View`.
  ([#1260](https://github.com/Pycord-Development/pycord/pull/1260))
- `Option` class and usage was rewritten.
  ([#1251](https://github.com/Pycord-Development/pycord/pull/1251))
- `description` argument of `PageGroup` is now optional.
  ([#1330](https://github.com/Pycord-Development/pycord/pull/1330))
- Allow `Modal.children` to be set on initialization.
  ([#1311](https://github.com/Pycord-Development/pycord/pull/1311))
- Renamed `delete_exiting` to `delete_existing` (typo).
  ([#1336](https://github.com/Pycord-Development/pycord/pull/1336))

### Fixed

- Fix `PartialMessage.edit()` setting `view` as `None` when `view` kwarg is not passed.
  ([#1256](https://github.com/Pycord-Development/pycord/pull/1256))
- Fix channel parsing in slash command invocations.
  ([#1257](https://github.com/Pycord-Development/pycord/pull/1257))
- Make channel `position` attribute optional.
  ([#1257](https://github.com/Pycord-Development/pycord/pull/1257))
- Fix `PaginatorMenu` to use interaction routes for updates.
  ([#1267](https://github.com/Pycord-Development/pycord/pull/1267))
- Fix `PartialMessage.edit()` behavior when `content` is `None`.
  ([#1268](https://github.com/Pycord-Development/pycord/pull/1268))
- Fix `Paginator.add_menu()` and `Paginator.add_default_buttons()` passing `custom_id`
  to `PaginatorMenu`. ([#1270](https://github.com/Pycord-Development/pycord/pull/1270))
- Fix `process_application_commands` command not found fallback.
  ([#1262](https://github.com/Pycord-Development/pycord/pull/1262))
- Fix interaction response race condition.
  ([#1039](https://github.com/Pycord-Development/pycord/pull/1039))
- Remove voice client when bot disconnects.
  ([#1273](https://github.com/Pycord-Development/pycord/pull/1273))
- Fix conversion exception in ext.bridge.
  ([#1250](https://github.com/Pycord-Development/pycord/pull/1250))
- Context.me return ClientUser when guilds intent is absent.
  ([#1286](https://github.com/Pycord-Development/pycord/pull/1286))
- Updated `Message.edit` type hinting overload and removed resulting redundant
  overloads. ([#1299](https://github.com/Pycord-Development/pycord/pull/1299))
- Improved validation regex for command names & options.
  ([#1309](https://github.com/Pycord-Development/pycord/pull/1309))
- Correct `Guild.fetch_members()` type hints.
  ([#1323](https://github.com/Pycord-Development/pycord/pull/1323))
- Multiple fixes and enhancements for `PageGroup` handling.
  ([#1350](https://github.com/Pycord-Development/pycord/pull/1350))
- Make `TextChannel._get_channel` async.
  ([#1358](https://github.com/Pycord-Development/pycord/pull/1358))

## [2.0.0-beta.7] - 2022-04-09

### Fixed

- Fix py3.10 UnionType checks issue.
  ([#1240](https://github.com/Pycord-Development/pycord/pull/1240))

[unreleased]: https://github.com/Pycord-Development/pycord/compare/v2.2.2...HEAD
[2.2.2]: https://github.com/Pycord-Development/pycord/compare/v2.2.1...v2.2.2
[2.2.1]: https://github.com/Pycord-Development/pycord/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/Pycord-Development/pycord/compare/v2.1.3...v2.2.0
[2.1.3]: https://github.com/Pycord-Development/pycord/compare/v2.1.2...v2.1.3
[2.1.2]: https://github.com/Pycord-Development/pycord/compare/v2.1.1...v2.1.2
[2.1.1]: https://github.com/Pycord-Development/pycord/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/Pycord-Development/pycord/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/Pycord-Development/pycord/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/Pycord-Development/pycord/compare/v2.0.0-rc.1...v2.0.0
[2.0.0-rc.1]:
  https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.7...v2.0.0-rc.1
[2.0.0-beta.7]:
  https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.6...v2.0.0-beta.7
[2.0.0-beta.6]:
  https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.5...v2.0.0-beta.6
[2.0.0-beta.5]:
  https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.4...v2.0.0-beta.5
[2.0.0-beta.4]:
  https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.3...v2.0.0-beta.4
[2.0.0-beta.3]:
  https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.2...v2.0.0-beta.3
[2.0.0-beta.2]:
  https://github.com/Pycord-Development/pycord/compare/v2.0.0-beta.1...v2.0.0-beta.2
[2.0.0-beta.1]:
  https://github.com/Pycord-Development/pycord/compare/v1.7.3...v2.0.0-beta.1
[version guarantees]: https://docs.pycord.dev/en/stable/version_guarantees.html
