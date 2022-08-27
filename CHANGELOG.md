# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project does not adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.1] - 2022-08-25
### Fixed
- Fix bridge command detection in cogs by [@BobDotCom](https://github.com/BobDotCom) in [#1592](https://github.com/Pycord-Development/pycord/pull/1592)

## [2.1.0] - 2022-08-25
### Added
- feat: add additional operations to `BaseFlags` by [@celsiusnarhwal](https://github.com/celsiusnarhwal) in [#1486](https://github.com/Pycord-Development/pycord/pull/1486)
- Add interaction support for View.message and add disable_on_timeout to Views by [@ConchDev](https://github.com/ConchDev) in [#1492](https://github.com/Pycord-Development/pycord/pull/1492)
- feat: Slash Command Mentions by [@JustaSqu1d](https://github.com/JustaSqu1d) in [#1523](https://github.com/Pycord-Development/pycord/pull/1523)
- Implement app_commands_badge in flags.py by [@lol219](https://github.com/lol219) in [#1535](https://github.com/Pycord-Development/pycord/pull/1535)
- Adding RPC endpoint support (Client.fetch_application) by [@lol219](https://github.com/lol219) in [#1536](https://github.com/Pycord-Development/pycord/pull/1536)
- Adding `on_check_failure` to `View` class by [@Kile](https://github.com/Kile) in [#799](https://github.com/Pycord-Development/pycord/pull/799)
- Add set_mfa_required method by [@Middledot](https://github.com/Middledot) in [#1552](https://github.com/Pycord-Development/pycord/pull/1552)
- Implement `resume_gateway_url` by [@Dorukyum](https://github.com/Dorukyum) in [#1559](https://github.com/Pycord-Development/pycord/pull/1559)
- ext.bridge improvements by [@Middledot](https://github.com/Middledot) in [#1496](https://github.com/Pycord-Development/pycord/pull/1496)

### Changed
- Set store=False as default in load_extension(s) by [@NeloBlivion](https://github.com/NeloBlivion) in [#1520](https://github.com/Pycord-Development/pycord/pull/1520)
- commands.has_permissions() return True in DM channels (fix #1576) by [@yoggys](https://github.com/yoggys) in [#1577](https://github.com/Pycord-Development/pycord/pull/1577)

### Fixed
- Fix `VoiceChannel`/`CategoryChannel` data being invalidated on `Option._invoke` by [@baronkobama](https://github.com/baronkobama) in [#1490](https://github.com/Pycord-Development/pycord/pull/1490)
- Fix type issues in options.py by [@Dorukyum](https://github.com/Dorukyum) in [#1473](https://github.com/Pycord-Development/pycord/pull/1473)
- Update content retrieval from AutoModActionExecution by [@NeloBlivion](https://github.com/NeloBlivion) in [#1521](https://github.com/Pycord-Development/pycord/pull/1521)
- Large code/documentation cleanup by [@baronkobama](https://github.com/baronkobama) in [#1476](https://github.com/Pycord-Development/pycord/pull/1476)
- Fix `Option` raising AttributeError for `str` and `min_length or max_length` (issue #1526) by [@yoggys](https://github.com/yoggys) in [#1527](https://github.com/Pycord-Development/pycord/pull/1527)
- Fix load_extensions parameters not being passed through by [@UP929312](https://github.com/UP929312) in [#1537](https://github.com/Pycord-Development/pycord/pull/1537)
- Fix SlashCommandGroup descriptions pretending to be optional by [@Middledot](https://github.com/Middledot) in [#1539](https://github.com/Pycord-Development/pycord/pull/1539)
- Fix Enum options breaking again & wrong typing import by [@Middledot](https://github.com/Middledot) in [#1541](https://github.com/Pycord-Development/pycord/pull/1541)
- Adjust category and guild _channels attributes to work with NoneType positions by [@NeloBlivion](https://github.com/NeloBlivion) in [#1530](https://github.com/Pycord-Development/pycord/pull/1530)
- Make `SelectOption.emoji` a property by [@Middledot](https://github.com/Middledot) in [#1550](https://github.com/Pycord-Development/pycord/pull/1550)
- Improve sticker creation checks by [@Middledot](https://github.com/Middledot) in [#1546](https://github.com/Pycord-Development/pycord/pull/1546)
- Fix threads made from messages breaking by [@Middledot](https://github.com/Middledot) in [#1551](https://github.com/Pycord-Development/pycord/pull/1551)
- Correct location of app_commands_badge flag by [@Middledot](https://github.com/Middledot) in [#1553](https://github.com/Pycord-Development/pycord/pull/1553)
- Avoid unnecessary call to `sync_commands` by [@BobDotCom](https://github.com/BobDotCom) in [#1563](https://github.com/Pycord-Development/pycord/pull/1563)
- use custom_id to create timeout task by [@LuisWollenschneider](https://github.com/LuisWollenschneider) in [#1562](https://github.com/Pycord-Development/pycord/pull/1562)
- Respect limit argument in Guild.bans() by [@NeloBlivion](https://github.com/NeloBlivion) in [#1573](https://github.com/Pycord-Development/pycord/pull/1573)
- Fix on_scheduled_event_update event by [@NeloBlivion](https://github.com/NeloBlivion) in [#1580](https://github.com/Pycord-Development/pycord/pull/1580)
- Fixed small bug in `ApplicationCommand` by [@chrisdewa](https://github.com/chrisdewa) in [#1585](https://github.com/Pycord-Development/pycord/pull/1585)
- Fix SlashCommandGroup description not being truly optional by [@NeloBlivion](https://github.com/NeloBlivion) in [#1586](https://github.com/Pycord-Development/pycord/pull/1586)
- Apply cog_check method to ApplicationCommand invocations by [@NeloBlivion](https://github.com/NeloBlivion) in [#1575](https://github.com/Pycord-Development/pycord/pull/1575)
- Fix `Interaction.edit_original_message()` InteractionMessage state by [@camelwater](https://github.com/camelwater) in [#1565](https://github.com/Pycord-Development/pycord/pull/1565)
- Fix required parameters validation error by [@Middledot](https://github.com/Middledot) in [#1589](https://github.com/Pycord-Development/pycord/pull/1589)

### Security
- Fix for application-based bots without the bot scope by [@NeloBlivion](https://github.com/NeloBlivion) in [#1568](https://github.com/Pycord-Development/pycord/pull/1568)
- Rework vulnerability handling by [@Lulalaby](https://github.com/Lulalaby) in [#1584](https://github.com/Pycord-Development/pycord/pull/1584)


[Unreleased]: https://github.com/Pycord-Development/pycord/compare/v2.1.1...HEAD
[2.1.1]: https://github.com/Pycord-Development/pycord/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/Pycord-Development/pycord/compare/v2.0.1...v2.1.0
