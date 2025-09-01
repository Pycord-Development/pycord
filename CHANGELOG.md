# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) when
possible (see our [Version Guarantees] for more info).

## [Unreleased]

These changes are available on the `master` branch, but have not yet been released.

### Added

### Changed

### Fixed

- Manage silence for new SSRC with existing user_id.
  ([#2808](https://github.com/Pycord-Development/pycord/pull/2808))

### Removed

## [2.7.0rc1] - 2025-08-30

⚠️ **This version removes support for Python 3.8.** ⚠️

### Added

- Added `Guild.fetch_role` method.
  ([#2528](https://github.com/Pycord-Development/pycord/pull/2528))
- Added the following `AppInfo` attributes: `approximate_guild_count`,
  `approximate_user_install_count`, `custom_install_url`, `install_params`,
  `interactions_endpoint_url`, `redirect_uris`, `role_connections_verification_url`, and
  `tags`. ([#2520](https://github.com/Pycord-Development/pycord/pull/2520))
- Added `Member.guild_banner` and `Member.display_banner` properties.
  ([#2556](https://github.com/Pycord-Development/pycord/pull/2556))
- Added support for Application Emojis.
  ([#2501](https://github.com/Pycord-Development/pycord/pull/2501))
- Added `cache_app_emojis` parameter to `Client`.
  ([#2501](https://github.com/Pycord-Development/pycord/pull/2501))
- Added `elapsed` method to `VoiceClient`.
  ([#2587](https://github.com/Pycord-Development/pycord/pull/2587/))
- Added optional `filter` parameter to `utils.basic_autocomplete()`.
  ([#2590](https://github.com/Pycord-Development/pycord/pull/2590))
- Added role tags: `subscription_listing_id`, `guild_connections`, and
  `available_for_purchase`.
  ([#2606](https://github.com/Pycord-Development/pycord/pull/2606))
- Added missing `with_counts` parameter to `fetch_guilds` method.
  ([#2615](https://github.com/Pycord-Development/pycord/pull/2615))
- Added the following missing permissions: `Permissions.use_soundboard`,
  `Permissions.use_external_sounds`, and
  `Permissions.view_creator_monetization_analytics`.
  ([#2620](https://github.com/Pycord-Development/pycord/pull/2620))
- Added `MediaChannel` channel type.
  ([#2641](https://github.com/Pycord-Development/pycord/pull/2641))
- Added `Message._raw_data` attribute.
  ([#2670](https://github.com/Pycord-Development/pycord/pull/2670))
- Added helper methods to determine the authorizing party of an `Interaction`.
  ([#2659](https://github.com/Pycord-Development/pycord/pull/2659))
- Added `VoiceMessage` subclass of `File` to allow voice messages to be sent.
  ([#2579](https://github.com/Pycord-Development/pycord/pull/2579))
- Added the following soundboard-related features:
  - Manage guild soundboard sounds with `Guild.fetch_sounds()`, `Guild.create_sound()`,
    `SoundboardSound.edit()`, and `SoundboardSound.delete()`.
  - Access Discord default sounds with `Client.fetch_default_sounds()`.
  - Play sounds in voice channels with `VoiceChannel.send_soundboard_sound()`.
  - New `on_voice_channel_effect_send` event for sound and emoji effects.
  - Soundboard limits based on guild premium tier (8-48 slots) in
    `Guild.soundboard_limit`.
    ([#2623](https://github.com/Pycord-Development/pycord/pull/2623))
- Added new `Subscription` object and related methods/events.
  ([#2564](https://github.com/Pycord-Development/pycord/pull/2564))
- Added `Message.forward_to`, `Message.snapshots`, and other related attributes.
  ([#2598](https://github.com/Pycord-Development/pycord/pull/2598))
- Add missing `Guild` feature flags and `Guild.edit` parameters.
  ([#2672](https://github.com/Pycord-Development/pycord/pull/2672))
- Added the ability to change the API's base URL with `Route.API_BASE_URL`.
  ([#2714](https://github.com/Pycord-Development/pycord/pull/2714))
- Added the ability to pass a `datetime.time` object to `format_dt`.
  ([#2747](https://github.com/Pycord-Development/pycord/pull/2747))
- Added `RawMessageUpdateEvent.new_message` - message update events now contain full
  message objects ([#2780](https://github.com/Pycord-Development/pycord/pull/2780))
- Added various missing channel parameters and allow `default_reaction_emoji` to be
  `None`. ([#2772](https://github.com/Pycord-Development/pycord/pull/2772))
- Added support for type hinting slash command options with `typing.Annotated`.
  ([#2782](https://github.com/Pycord-Development/pycord/pull/2782))
- Added conversion to `Member` in `MentionableConverter`.
  ([#2775](https://github.com/Pycord-Development/pycord/pull/2775))
- Added `discord.Interaction.created_at`.
  ([#2801](https://github.com/Pycord-Development/pycord/pull/2801))
- Added `User.nameplate` property.
  ([#2817](https://github.com/Pycord-Development/pycord/pull/2817))
- Added role gradients support with `Role.colours` and the `RoleColours` class.
  ([#2818](https://github.com/Pycord-Development/pycord/pull/2818))
- Added `ThreadArchiveDuration` enum to improve clarity of thread archive durations.
  ([#2826](https://github.com/Pycord-Development/pycord/pull/2826))
- Added `Interaction.attachment_size_limit`.
  ([#2854](https://github.com/Pycord-Development/pycord/pull/2854))
- Added support for selects and text displays in modals.
  ([#2858](https://github.com/Pycord-Development/pycord/pull/2858))
- Added `AuditLogDiff.communication_disabled_until`.
  ([#2883](https://github.com/Pycord-Development/pycord/pull/2883))
- Added `discord.User.primary_guild` and the `PrimaryGuild` class.
  ([#2876](https://github.com/Pycord-Development/pycord/pull/2876))
- Added `get_component` to `Message`, `Section`, `Container` and `ActionRow`.
  ([#2849](https://github.com/Pycord-Development/pycord/pull/2849))

### Fixed

- Fixed `Enum` options not setting the correct type when only one choice is available.
  ([#2577](https://github.com/Pycord-Development/pycord/pull/2577))
- Fixed `codec` option for `FFmpegOpusAudio` class to make it in line with
  documentation. ([#2581](https://github.com/Pycord-Development/pycord/pull/2581))
- Fixed a possible bug where audio would play too fast at the beginning of audio files.
  ([#2584](https://github.com/Pycord-Development/pycord/pull/2584))
- Fixed paginator not responding when using `Paginator.edit()` with default parameters.
  ([#2594](https://github.com/Pycord-Development/pycord/pull/2594))
- Fixed the `is_owner()` `user` type hint: `User` -> `User | Member`.
  ([#2593](https://github.com/Pycord-Development/pycord/pull/2593))
- Fixed `Guild.create_test_entitlement()` and `User.create_test_entitlement()` using the
  guild/user ID instead of the application ID.
  ([#2595](https://github.com/Pycord-Development/pycord/pull/2595))
- Fixed `BucketType.category` cooldown commands not functioning correctly in private
  channels. ([#2603](https://github.com/Pycord-Development/pycord/pull/2603))
- Fixed `ctx` parameter of a `SlashCommand` not being `Union` type.
  ([#2611](https://github.com/Pycord-Development/pycord/pull/2611))
- Fixed `TypeError` when passing `skus` parameter in `Client.entitlements()`.
  ([#2627](https://github.com/Pycord-Development/pycord/issues/2627))
- Fixed `AttributeError` when sending polls with `PartialWebook`.
  ([#2624](https://github.com/Pycord-Development/pycord/pull/2624))
- Fixed editing `ForumChannel` flags not working.
  ([#2641](https://github.com/Pycord-Development/pycord/pull/2641))
- Fixed `AttributeError` when accessing `Member.guild_permissions` for user installed
  apps. ([#2650](https://github.com/Pycord-Development/pycord/pull/2650))
- Fixed type annotations of cached properties.
  ([#2635](https://github.com/Pycord-Development/pycord/issues/2635))
- Fixed malformed properties in `Interaction.channel`.
  ([#2658](https://github.com/Pycord-Development/pycord/pull/2658))
- Fixed an error when responding non-ephemerally with a `Paginator` to an ephemerally
  deferred interaction.
  ([#2661](https://github.com/Pycord-Development/pycord/pull/2661))
- Fixed attachment metadata being set incorrectly in interaction responses causing the
  metadata to be ignored by Discord.
  ([#2679](https://github.com/Pycord-Development/pycord/pull/2679))
- Fixed unexpected backoff behavior in the handling of task failures
  ([#2700](https://github.com/Pycord-Development/pycord/pull/2700)).
- Fixed `BridgeCommand` duplicate in default help command.
  ([#2656](https://github.com/Pycord-Development/pycord/pull/2656))
- Fixed `AttributeError` when trying to consume a consumable entitlement.
  ([#2564](https://github.com/Pycord-Development/pycord/pull/2564))
- Fixed `Subscription.renewal_sku_ids` not accepting `None` from the received payload.
  ([#2709](https://github.com/Pycord-Development/pycord/pull/2709))
- Fixed `ForumChannel.edit` allowing `default_reaction_emoji` to be `None`.
  ([#2739](https://github.com/Pycord-Development/pycord/pull/2739))
- Fixed missing `None` type hints in `Select.__init__`.
  ([#2746](https://github.com/Pycord-Development/pycord/pull/2746))
- Fixed `TypeError` when using `Flag` with Python 3.11+.
  ([#2759](https://github.com/Pycord-Development/pycord/pull/2759))
- Fixed `TypeError` when specifying `thread_name` in `Webhook.send`.
  ([#2761](https://github.com/Pycord-Development/pycord/pull/2761))
- Updated `valid_locales` to support `in` and `es-419`.
  ([#2767](https://github.com/Pycord-Development/pycord/pull/2767))
- Added support for emoji aliases like `:smile:` in PartialEmoji.from_str. Also applied
  the same logic in PartialEmojiConverter.
  ([#2815](https://github.com/Pycord-Development/pycord/pull/2815))
- Fixed `Webhook.edit` not working with `attachments=[]`.
  ([#2779](https://github.com/Pycord-Development/pycord/pull/2779))
- Fixed GIF-based `Sticker` returning the wrong `url`.
  ([#2781](https://github.com/Pycord-Development/pycord/pull/2781))
- Fixed `VoiceClient` crashing randomly while receiving audio
  ([#2800](https://github.com/Pycord-Development/pycord/pull/2800))
- Fixed `VoiceClient.connect` failing to do initial connection.
  ([#2812](https://github.com/Pycord-Development/pycord/pull/2812))
- Fixed `AttributeError` when printing a File component's `__repr__`.
  ([#2843](https://github.com/Pycord-Development/pycord/pull/2843))
- Fixed `TypeError` when using `@option` with certain annotations and along with
  `channel_types`. ([#2835](https://github.com/Pycord-Development/pycord/pull/2835))
- Fixed `TypeError` when using `Optional[...]` or `... | None` in command option type.
  ([#2852](https://github.com/Pycord-Development/pycord/pull/2852))
- Fixed type-hinting for `PermissionOverwrite.update`.
  ([#2878](https://github.com/Pycord-Development/pycord/pull/2878))
- Fixed `AttributeError` when accessing `AuditLogEntry.changes` more than once.
  ([#2882])(https://github.com/Pycord-Development/pycord/pull/2882))
- Fixed type hint for argument `start_time` and `end_time` of
  `Guild.create_scheduled_event`
  ([#2879](https://github.com/Pycord-Development/pycord/pull/2879))

### Changed

- Renamed `cover` property of `ScheduledEvent` and `cover` argument of
  `ScheduledEvent.edit` to `image`.
  ([#2496](https://github.com/Pycord-Development/pycord/pull/2496))
- ⚠️ **Removed support for Python 3.8.**
  ([#2521](https://github.com/Pycord-Development/pycord/pull/2521))
- `Emoji` has been renamed to `GuildEmoji`.
  ([#2501](https://github.com/Pycord-Development/pycord/pull/2501))
- Replaced audioop (deprecated module) implementation of `PCMVolumeTransformer.read`
  method with a pure Python equivalent.
  ([#2176](https://github.com/Pycord-Development/pycord/pull/2176))
- Updated `Guild.filesize_limit` to 10 MB instead of 25 MB following Discord's API
  changes. ([#2671](https://github.com/Pycord-Development/pycord/pull/2671))
- `Entitlement.ends_at` can now be `None`.
  ([#2564](https://github.com/Pycord-Development/pycord/pull/2564))
- Changed the default value of `ApplicationCommand.nsfw` to `False`.
  ([#2797](https://github.com/Pycord-Development/pycord/pull/2797))
- Upgraded voice websocket version to v8.
  ([#2812](https://github.com/Pycord-Development/pycord/pull/2812))
- `Messageable.pins()` now returns a `MessagePinIterator` and has new arguments.
  ([#2872](https://github.com/Pycord-Development/pycord/pull/2872))

### Deprecated

- Deprecated `AppInfo.summary` in favor of `AppInfo.description`.
  ([#2520](https://github.com/Pycord-Development/pycord/pull/2520))
- Deprecated `Emoji` in favor of `GuildEmoji`.
  ([#2501](https://github.com/Pycord-Development/pycord/pull/2501))
- Deprecated `Interaction.cached_channel` in favor of `Interaction.channel`.
  ([#2658](https://github.com/Pycord-Development/pycord/pull/2658))
- Deprecated `is_nsfw` for categories since it was never supported by the API.
  ([#2772](https://github.com/Pycord-Development/pycord/pull/2772))
- Deprecated `Messageable.pins()` returning a list of `Message`; it should be used as an
  iterator of `MessagePin` instead.
  ([#2872](https://github.com/Pycord-Development/pycord/pull/2872))

### Removed

- Removed deprecated support for `Option` in `BridgeCommand`, use `BridgeOption`
  instead. ([#2731](https://github.com/Pycord-Development/pycord/pull/2731))

## [2.6.1] - 2024-09-15

### Fixed

- Fixed premature garbage collection of tasks.
  ([#2510](https://github.com/Pycord-Development/pycord/pull/2510))
- Fixed `EntitlementIterator` type hints and behavior with `limit > 100`.
  ([#2555](https://github.com/Pycord-Development/pycord/pull/2555))
- Fixed missing `stacklevel` parameter in `warn_deprecated` function call inside
  `@utils.deprecated`. ([#2500](https://github.com/Pycord-Development/pycord/pull/2500))
- Fixed the type hint in `ConnectionState._polls` to reflect actual behavior, changing
  it from `Guild` to `Poll`.
  ([#2500](https://github.com/Pycord-Development/pycord/pull/2500))
- Fixed missing `__slots__` attributes in `RawReactionClearEmojiEvent` and
  `RawMessagePollVoteEvent`.
  ([#2500](https://github.com/Pycord-Development/pycord/pull/2500))
- Fixed the type of `ForumChannel.default_sort_order`, changing it from `int` to
  `SortOrder`. ([#2500](https://github.com/Pycord-Development/pycord/pull/2500))
- Fixed `PartialMessage` causing errors when created from `PartialMessageable`.
  ([#2568](https://github.com/Pycord-Development/pycord/pull/2500))
- Fixed the `guild` attribute of `Member`s received from a `UserCommand` being `None`.
  ([#2573](https://github.com/Pycord-Development/pycord/pull/2573))
- Fixed `Webhook.send`, which did not include attachment data.
  ([#2513](https://github.com/Pycord-Development/pycord/pull/2513))
- Fixed inverted type hints in `CheckAnyFailure`.
  ([#2502](https://github.com/Pycord-Development/pycord/pull/2502))

## [2.6.0] - 2024-07-09

### Added

- Added `banner` parameter to `ClientUser.edit`.
  ([#2396](https://github.com/Pycord-Development/pycord/pull/2396))
- Added `user` argument to `Paginator.edit`.
  ([#2390](https://github.com/Pycord-Development/pycord/pull/2390))
- Added `bridge_option` decorator. Required for `bridge.Bot` in 2.7.
  ([#2417](https://github.com/Pycord-Development/pycord/pull/2417))
- Added `Guild.search_members`.
  ([#2418](https://github.com/Pycord-Development/pycord/pull/2418))
- Added bulk banning up to 200 users through `Guild.bulk_ban`.
  ([#2421](https://github.com/Pycord-Development/pycord/pull/2421))
- Added `member` data to the `raw_reaction_remove` event.
  ([#2412](https://github.com/Pycord-Development/pycord/pull/2412))
- Added `Poll` and all related features.
  ([#2408](https://github.com/Pycord-Development/pycord/pull/2408))
- Added `stacklevel` param to `utils.warn_deprecated` and `utils.deprecated`.
  ([#2450](https://github.com/Pycord-Development/pycord/pull/2450))
- Added support for user-installable applications.
  ([#2409](https://github.com/Pycord-Development/pycord/pull/2409))
- Added support for one-time purchases for Discord monetization.
  ([#2438](https://github.com/Pycord-Development/pycord/pull/2438))
- Added `Attachment.title`.
  ([#2486](https://github.com/Pycord-Development/pycord/pull/2486))
- Added `MemberFlags`. ([#2489](https://github.com/Pycord-Development/pycord/pull/2489))
- Added `bypass_verification` parameter to `Member.edit`.
  ([#2489](https://github.com/Pycord-Development/pycord/pull/2489))
- Added `RoleFlags`. ([#2487](https://github.com/Pycord-Development/pycord/pull/2487))
- Added `MessageCall` information.
  ([#2488](https://github.com/Pycord-Development/pycord/pull/2488))

### Fixed

- Fixed the type-hinting of `Member.move_to` and `Member.edit` to reflect actual
  behavior. ([#2386](https://github.com/Pycord-Development/pycord/pull/2386))
- Fixed a deprecation warning from being displayed when running `python -m discord -v`
  by replacing the deprecated module.
  ([#2392](https://github.com/Pycord-Development/pycord/pull/2392))
- Fixed `Paginator.edit` to no longer set user to the bot.
  ([#2390](https://github.com/Pycord-Development/pycord/pull/2390))
- Fixed `NameError` in some instances of `Interaction`.
  ([#2402](https://github.com/Pycord-Development/pycord/pull/2402))
- Fixed interactions being ignored due to `PartialMessage.id` being of type `str`.
  ([#2406](https://github.com/Pycord-Development/pycord/pull/2406))
- Fixed the type-hinting of `ScheduledEvent.subscribers` to reflect actual behavior.
  ([#2400](https://github.com/Pycord-Development/pycord/pull/2400))
- Fixed `ScheduledEvent.subscribers` behavior with `limit=None`.
  ([#2407](https://github.com/Pycord-Development/pycord/pull/2407))
- Fixed invalid data being passed to `Interaction._guild` in certain cases.
  ([#2411](https://github.com/Pycord-Development/pycord/pull/2411))
- Fixed option type hints being ignored when using `parameter_name`.
  ([#2417](https://github.com/Pycord-Development/pycord/pull/2417))
- Fixed parameter `embed=None` causing `AttributeError` on `PartialMessage.edit`.
  ([#2446](https://github.com/Pycord-Development/pycord/pull/2446))
- Fixed paginator to revert state if a page update callback fails.
  ([#2448](https://github.com/Pycord-Development/pycord/pull/2448))
- Fixed missing `application_id` in `Entitlement.delete`.
  ([#2458](https://github.com/Pycord-Development/pycord/pull/2458))
- Fixed issues with enums as `Option` types with long descriptions or too many values.
  ([#2463](https://github.com/Pycord-Development/pycord/pull/2463))
- Fixed many inaccurate type hints throughout the library.
  ([#2457](https://github.com/Pycord-Development/pycord/pull/2457))
- Fixed `AttributeError` due to `discord.Option` being initialised with `input_type` set
  to `None`. ([#2464](https://github.com/Pycord-Development/pycord/pull/2464))
- Fixed `remove_application_command` causing issues while reloading extensions.
  ([#2480](https://github.com/Pycord-Development/pycord/pull/2480))
- Fixed outdated logic for filtering and sorting audit log entries.
  ([#2371](https://github.com/Pycord-Development/pycord/pull/2371))
- Further fixed logic when fetching audit logs.
  ([#2492](https://github.com/Pycord-Development/pycord/pull/2492))

### Changed

- Changed the type of `Guild.bitrate_limit` to `int`.
  ([#2387](https://github.com/Pycord-Development/pycord/pull/2387))
- HTTP requests that fail with a 503 status are now retried.
  ([#2395](https://github.com/Pycord-Development/pycord/pull/2395))
- `option` decorator now accepts `input_type`.
  ([#2417](https://github.com/Pycord-Development/pycord/pull/2417))
- `Option` may be used instead of `BridgeOption` until 2.7.
  ([#2417](https://github.com/Pycord-Development/pycord/pull/2417))
- `Guild.query_members` now accepts `limit=None` to retrieve all members.
  ([#2419](https://github.com/Pycord-Development/pycord/pull/2419))
- `ApplicationCommand.guild_only` is now deprecated in favor of
  `ApplicationCommand.contexts`.
  ([#2409](https://github.com/Pycord-Development/pycord/pull/2409))
- `Message.interaction` is now deprecated in favor of `Message.interaction_metadata`.
  ([#2409](https://github.com/Pycord-Development/pycord/pull/2409))
- Replaced `Client.fetch_entitlements` with `Client.entitlements`, which returns an
  `EntitlementIterator`.
  ([#2490](https://github.com/Pycord-Development/pycord/pull/2490))
- Changed the error message that appears when attempting to add a subcommand group to a
  subcommand group. ([#2275](https://github.com/Pycord-Development/pycord/pull/2275))

### Removed

- Removed the `delete_message_days` parameter from ban methods. Please use
  `delete_message_seconds` instead.
  ([#2421](https://github.com/Pycord-Development/pycord/pull/2421))
- Removed the `oldest_first` parameter from `Guild.audit_logs` in favor of the `before`
  and `after` parameters.
  ([#2371](https://github.com/Pycord-Development/pycord/pull/2371))
- Removed the `vanity_code` parameter from `Guild.edit`.
  ([#2491](https://github.com/Pycord-Development/pycord/pull/2491))

## [2.5.0] - 2024-03-02

### Added

- Added method to start bot via async context manager.
  ([#1801](https://github.com/Pycord-Development/pycord/pull/1801))
- Added parameters `author`, `footer`, `image` and `thumbnail` to `discord.Embed`
  initializer. ([#1996](https://github.com/Pycord-Development/pycord/pull/1996))
- Added events `on_bridge_command`, `on_bridge_command_completion`, and
  `on_bridge_command_error`.
  ([#1916](https://github.com/Pycord-Development/pycord/pull/1916))
- Added the `@client.once()` decorator, which serves as a one-time event listener.
  ([#1940](https://github.com/Pycord-Development/pycord/pull/1940))
- Added support for text-related features in `StageChannel`.
  ([#1936](https://github.com/Pycord-Development/pycord/pull/1936))
- Added support for one-time event listeners in `Client.listen`.
  ([#1957](https://github.com/Pycord-Development/pycord/pull/1957))
- Added `current_page` argument to `Paginator.update()`.
  ([#1983](https://github.com/Pycord-Development/pycord/pull/1983))
- Added application flag `application_auto_moderation_rule_create_badge`.
  ([#1992](https://github.com/Pycord-Development/pycord/pull/1992))
- Added support for recording silence via new `sync_start` argument in
  `VoiceClient.start_recording()`.
  ([#1984](https://github.com/Pycord-Development/pycord/pull/1984))
- Added `custom_message` to AutoModActionMetadata.
  ([#2029](https://github.com/Pycord-Development/pycord/pull/2029))
- Added support for
  [voice messages](https://github.com/discord/discord-api-docs/pull/6082).
  ([#2016](https://github.com/Pycord-Development/pycord/pull/2016))
- Added `data` attribute to all
  [Raw Event payloads](https://docs.pycord.dev/en/master/api/models.html#events).
  ([#2023](https://github.com/Pycord-Development/pycord/pull/2023))
- Added and documented missing `AuditLogAction` enums.
  ([#2030](https://github.com/Pycord-Development/pycord/pull/2030),
  [#2171](https://github.com/Pycord-Development/pycord/pull/2171))
- Added AutoMod-related models for `AuditLogDiff` enums.
  ([#2030](https://github.com/Pycord-Development/pycord/pull/2030))
- Added `Interaction.respond` and `Interaction.edit` as shortcut responses.
  ([#2026](https://github.com/Pycord-Development/pycord/pull/2026))
- Added `view.parent` which is set when the view is sent by
  `interaction.response.send_message`.
  ([#2036](https://github.com/Pycord-Development/pycord/pull/2036))
- Added methods `bridge.Bot.walk_bridge_commands` and
  `BridgeCommandGroup.walk_commands`.
  ([#1867](https://github.com/Pycord-Development/pycord/pull/1867))
- Added support for usernames and modified multiple methods accordingly.
  ([#2042](https://github.com/Pycord-Development/pycord/pull/2042))
- Added `icon` and `unicode_emoji` arguments to `Guild.create_role`.
  ([#2086](https://github.com/Pycord-Development/pycord/pull/2086))
- Added `cooldown` and `max_concurrency` attributes to `SlashCommandGroup`.
  ([#2091](https://github.com/Pycord-Development/pycord/pull/2091))
- Added embedded activities Gartic Phone and Jamspace.
  ([#2102](https://github.com/Pycord-Development/pycord/pull/2102))
- Added `bridge.Context` type as a `Union` of subclasses.
  ([#2106](https://github.com/Pycord-Development/pycord/pull/2106))
- Added support for type-hinting slash command options with `typing.Annotated`.
  ([#2124](https://github.com/Pycord-Development/pycord/pull/2124))
- Added `suppress` and `allowed_mentions` parameters to `Webhook` and
  `InteractionResponse` edit methods.
  ([#2138](https://github.com/Pycord-Development/pycord/pull/2138))
- Added `wait_finish` parameter to `VoiceClient.play` for awaiting the end of a play.
  ([#2194](https://github.com/Pycord-Development/pycord/pull/2194))
- Added support for custom bot status.
  ([#2206](https://github.com/Pycord-Development/pycord/pull/2206))
- Added function `Guild.delete_auto_moderation_rule`.
  ([#2153](https://github.com/Pycord-Development/pycord/pull/2153))
- Added `VoiceChannel.slowmode_delay`.
  ([#2112](https://github.com/Pycord-Development/pycord/pull/2112))
- Added `ForumChannel.default_reaction_emoji` attribute.
  ([#2178](https://github.com/Pycord-Development/pycord/pull/2178))
- Added `default_reaction_emoji` parameter to `Guild.create_forum_channel` and
  `ForumChannel.edit` methods.
  ([#2178](https://github.com/Pycord-Development/pycord/pull/2178))
- Added `applied_tags` parameter to `Webhook.send` method.
  ([#2322](https://github.com/Pycord-Development/pycord/pull/2322))
- Added `User.avatar_decoration`.
  ([#2131](https://github.com/Pycord-Development/pycord/pull/2131))
- Added support for guild onboarding related features.
  ([#2127](https://github.com/Pycord-Development/pycord/pull/2127))
- Added support for monetization related objects and events.
  ([#2273](https://github.com/Pycord-Development/pycord/pull/2273))
- Added `AttachmentFlags` and attachment attributes `expires_at`, `issued_at` and `hm`.
  ([#2342](https://github.com/Pycord-Development/pycord/pull/2342))
- Added `invitable` and `slowmode_delay` to `Thread` creation methods.
  ([#2350](https://github.com/Pycord-Development/pycord/pull/2350))
- Added support for voice channel statuses.
  ([#2368](https://github.com/Pycord-Development/pycord/pull/2368))
- Added `enforce_nonce` parameter for message sending.
  ([#2370](https://github.com/Pycord-Development/pycord/pull/2370))
- Added audit log support for voice channel status.
  ([#2373](https://github.com/Pycord-Development/pycord/pull/2373))

### Changed

- Changed default for all `name_localizations` and `description_localizations`
  attributes from being `None` to being `MISSING`.
  ([#1866](https://github.com/Pycord-Development/pycord/pull/1866))
- Changed `ffmpeg` output suppression when recording voice channels.
  ([#1993](https://github.com/Pycord-Development/pycord/pull/1993))
- Changed file-upload size limit from 8 MB to 25 MB accordingly.
  ([#2014](https://github.com/Pycord-Development/pycord/pull/2014))
- Changed the behavior of retrieving bans to accurately reflect the API.
  ([#1922](https://github.com/Pycord-Development/pycord/pull/1922))
- Changed `Interaction.channel` to be received from the gateway, allowing it to be
  `DMChannel` or `GroupChannel`.
  ([#2025](https://github.com/Pycord-Development/pycord/pull/2025))
- Changed `DMChannel.recipients` to potentially be `None`.
  ([#2025](https://github.com/Pycord-Development/pycord/pull/2025))
- Changed the behavior to store `view.message` when receiving a component interaction,
  while also changing `view.message` not to be set when sending view through
  `InteractionResponse.send_message`.
  ([#2036](https://github.com/Pycord-Development/pycord/pull/2036))
- Changed the fetching of attributes shared between text-based and Slash Commands in
  Bridge Commands to be dynamic.
  ([#1867](https://github.com/Pycord-Development/pycord/pull/1867))
- `discord.Embed` attributes (such as author, footer, etc.) now return instances of
  their respective classes when set and `None` otherwise.
  ([#2063](https://github.com/Pycord-Development/pycord/pull/2063))
- Changed `default_avatar` behavior to depend on the user's username migration status.
  ([#2087](https://github.com/Pycord-Development/pycord/pull/2087))
- Changed type hints of `command_prefix` and `help_command` arguments to be accurate.
  ([#2099](https://github.com/Pycord-Development/pycord/pull/2099))
- Replaced `orjson` features with `msgspec` in the codebase.
  ([#2170](https://github.com/Pycord-Development/pycord/pull/2170))
- `BridgeOption` must now be used for arguments in bridge commands.
  ([#2252](https://github.com/Pycord-Development/pycord/pull/2252))

### Removed

- Removed `Client.once` in favour of `once` argument in `Client.listen`.
  ([#1957](https://github.com/Pycord-Development/pycord/pull/1957))
- Removed `Embed.Empty` in favour of `None`, and `EmbedProxy` in favour of individual
  classes. ([#2063](https://github.com/Pycord-Development/pycord/pull/2063))

### Fixed

- Fixed `AttributeError` caused by
  [#1957](https://github.com/Pycord-Development/pycord/pull/1957) when using listeners
  in cogs. ([#1989](https://github.com/Pycord-Development/pycord/pull/1989))
- Fixed an issue in editing webhook messages in forum posts and private threads.
  ([#1981](https://github.com/Pycord-Development/pycord/pull/1981)).
- Fixed `View.message` not being set when view is sent using webhooks, including
  `Interaction.followup.send` or when a message is edited.
  ([#1997](https://github.com/Pycord-Development/pycord/pull/1997))
- Fixed `None` being handled incorrectly for avatar in `ClientUser.edit`.
  ([#1994](https://github.com/Pycord-Development/pycord/pull/1994))
- Fixed scheduled events breaking when changing the location from external to a channel.
  ([#1998](https://github.com/Pycord-Development/pycord/pull/1998))
- Fixed boolean converter breaking for Bridge Commands.
  ([#1999](https://github.com/Pycord-Development/pycord/pull/1999))
- Fixed bridge command options not working.
  ([#1999](https://github.com/Pycord-Development/pycord/pull/1999))
- Fixed `TypeError` being raised when passing `name` argument to bridge groups.
  ([#2000](https://github.com/Pycord-Development/pycord/pull/2000))
- Fixed `TypeError` in `AutoModRule`.
  ([#2029](https://github.com/Pycord-Development/pycord/pull/2029))
- Fixed the functionality to override the default `on_application_command_error`
  behavior using listeners.
  ([#2044](https://github.com/Pycord-Development/pycord/pull/2044))
- Fixed unloading of cogs with bridge commands.
  ([#2048](https://github.com/Pycord-Development/pycord/pull/2048))
- Fixed the `individual` slash command synchronization method.
  ([#1925](https://github.com/Pycord-Development/pycord/pull/1925))
- Fixed an issue that occurred when `webhooks_update` event payload channel ID was
  `None`. ([#2078](https://github.com/Pycord-Development/pycord/pull/2078))
- Fixed major `TypeError` when an `AuditLogEntry` has no user.
  ([#2079](https://github.com/Pycord-Development/pycord/pull/2079))
- Fixed `HTTPException` when trying to create a forum thread with files.
  ([#2075](https://github.com/Pycord-Development/pycord/pull/2075))
- Fixed `before_invoke` not being run for `SlashCommandGroup`.
  ([#2091](https://github.com/Pycord-Development/pycord/pull/2091))
- Fixed `AttributeError` when accessing a `Select` object's values when it has not been
  interacted with. ([#2104](https://github.com/Pycord-Development/pycord/pull/2104))
- Fixed `before_invoke` being run twice for slash subcommands.
  ([#2139](https://github.com/Pycord-Development/pycord/pull/2139))
- Fixed `Guild._member_count` sometimes not being set.
  ([#2145](https://github.com/Pycord-Development/pycord/pull/2145))
- Fixed `Thread.applied_tags` not being updated.
  ([#2146](https://github.com/Pycord-Development/pycord/pull/2146))
- Fixed type-hinting of `author` property of `ApplicationContext` to include
  type-hinting of `User` or `Member`.
  ([#2148](https://github.com/Pycord-Development/pycord/pull/2148))
- Fixed missing `delete_after` parameter in overload type-hinting for `Webhook.send()`.
  ([#2156](https://github.com/Pycord-Development/pycord/pull/2156))
- Fixed `ScheduledEvent.creator_id` returning `str` instead of `int`.
  ([#2162](https://github.com/Pycord-Development/pycord/pull/2162))
- Fixed `_bytes_to_base64_data` not defined.
  ([#2185](https://github.com/Pycord-Development/pycord/pull/2185))
- Fixed inaccurate `Union` type hint of `values` argument of `basic_autocomplete` to
  include `Iterable[OptionChoice]`.
- Fixed initial message inside of the create thread payload sending legacy beta payload.
  ([#2191](https://github.com/Pycord-Development/pycord/pull/2191))
- Fixed a misplaced payload object inside of the thread creation payload.
  ([#2192](https://github.com/Pycord-Development/pycord/pull/2192))
- Fixed `DMChannel.recipient` and `User.dm_channel` being `None`.
  ([#2219](https://github.com/Pycord-Development/pycord/pull/2219))
- Fixed `ffmpeg` being terminated prematurely when piping audio stream.
  ([#2240](https://github.com/Pycord-Development/pycord/pull/2240))
- Fixed tasks looping infinitely when `tzinfo` is neither `None` nor UTC.
  ([#2196](https://github.com/Pycord-Development/pycord/pull/2196))
- Fixed `AttributeError` when running permission checks without the `bot` scope.
  ([#2113](https://github.com/Pycord-Development/pycord/issues/2113))
- Fixed `Option` not working on bridge commands because `ext.commands.Command` does not
  recognize them. ([#2256](https://github.com/Pycord-Development/pycord/pull/2256))
- Fixed offset-aware tasks causing `TypeError` when being prepared.
  ([#2271](https://github.com/Pycord-Development/pycord/pull/2271))
- Fixed `AttributeError` when serializing commands with `Annotated` type hints.
  ([#2243](https://github.com/Pycord-Development/pycord/pull/2243))
- Fixed `Intents.all()` returning the wrong value.
  ([#2257](https://github.com/Pycord-Development/pycord/issues/2257))
- Fixed `AuditLogIterator` not respecting the `after` parameter.
  ([#2295](https://github.com/Pycord-Development/pycord/issues/2295))
- Fixed `AttributeError` when failing to establish initial websocket connection.
  ([#2301](https://github.com/Pycord-Development/pycord/pull/2301))
- Fixed `AttributeError` caused by `command.cog` being `MISSING`.
  ([#2303](https://github.com/Pycord-Development/pycord/issues/2303))
- Fixed `self.use_default_buttons` being assumed truthy by `Paginator.update`.
  ([#2319](https://github.com/Pycord-Development/pycord/pull/2319))
- Fixed `AttributeError` when comparing application commands with non-command objects.
  ([#2299](https://github.com/Pycord-Development/pycord/issues/2299))
- Fixed `AttributeError` when copying groups on startup.
  ([#2331](https://github.com/Pycord-Development/pycord/issues/2331))
- Fixed application command options causing errors if declared through the option
  decorator or kwarg.
  ([#2332](https://github.com/Pycord-Development/pycord/issues/2332))
- Fixed options declared using the parameter default value syntax always being optional.
  ([#2333](https://github.com/Pycord-Development/pycord/issues/2333))
- Fixed `BridgeContext` type hints raising an exception for unsupported option type.
  ([#2337](https://github.com/Pycord-Development/pycord/pull/2337))
- Fixed `TypeError` due to `(Sync)WebhookMessage._thread_id` being set to `None`.
  ([#2343](https://github.com/Pycord-Development/pycord/pull/2343))
- Fixed `AttributeError` due to `entitlements` not being included in
  `Interaction.__slots__`.
  ([#2345](https://github.com/Pycord-Development/pycord/pull/2345))
- Fixed `Thread.me` being out of date and added the thread owner to `Thread.members` on
  creation. ([#1296](https://github.com/Pycord-Development/pycord/issues/1296))
- Fixed keyword argument wildcard of `bridge.has_permissions` having the wrong type
  hint. ([#2364](https://github.com/Pycord-Development/pycord/pull/2364))
- Fixed enum to support stringified annotations.
  ([#2367](https://github.com/Pycord-Development/pycord/pull/2367))

## [2.4.1] - 2023-03-20

### Changed

- Updated the values of the `Color.embed_background()` classmethod to correspond with
  new theme colors in the app.
  ([#1931](https://github.com/Pycord-Development/pycord/pull/1931))

### Fixed

- Fixed the type-hinting of `SlashCommandGroup.walk_commands()` to reflect actual
  behavior. ([#1838](https://github.com/Pycord-Development/pycord/pull/1838))
- Fixed the voice IP discovery due to the recent
  [announced change](https://discord.com/channels/613425648685547541/697138785317814292/1080623873629884486).
  ([#1955](https://github.com/Pycord-Development/pycord/pull/1955))
- Fixed `reason` being passed to the wrong method in
  `guild.create_auto_moderation_rule`.
  ([#1960](https://github.com/Pycord-Development/pycord/pull/1960))

## [2.4.0] - 2023-02-10

### Added

- Added new AutoMod trigger metadata properties `regex_patterns`, `allow_list`, and
  `mention_total_limit`; and added the `mention_spam` trigger type.
  ([#1809](https://github.com/Pycord-Development/pycord/pull/1809))
- Added missing `image` parameter to `Guild.create_scheduled_event()` method.
  ([#1831](https://github.com/Pycord-Development/pycord/pull/1831))
- New `ApplicationRoleConnectionMetadata` class for application role connection
  metadata, along with the `fetch_role_connection_metadata_records` and
  `update_role_connection_metadata_records` methods in `Client`.
  ([#1791](https://github.com/Pycord-Development/pycord/pull/1791))
- Added new message types, `role_subscription_purchase`, `interaction_premium_upsell`,
  `stage_start`, `stage_end`, `stage_speaker`, `stage_raise_hand`, `stage_topic`, and
  `guild_application_premium_subscription`.
  ([#1852](https://github.com/Pycord-Development/pycord/pull/1852))
- Added new `EmbeddedActivity` values.
  ([#1859](https://github.com/Pycord-Development/pycord/pull/1859))
- Added new `suppress_notifications` to `MessageFlags`.
  ([#1912](https://github.com/Pycord-Development/pycord/pull/1912))
- Added GIF sticker format type to the `StickerFormatType` enum.
  ([#1915](https://github.com/Pycord-Development/pycord/pull/1915))
- Added new raw events: `raw_member_remove`, `raw_thread_update`, and
  `raw_thread_member_remove`.
  ([#1880](https://github.com/Pycord-Development/pycord/pull/1880))
- Improved support for setting channel types & added new channel types for
  `discord.Option`. ([#1883](https://github.com/Pycord-Development/pycord/pull/1883))

### Changed

- Changed `EmbeddedActivity` values to update accordingly with the new activities.
  ([#1859](https://github.com/Pycord-Development/pycord/pull/1859))
- Advanced version info is now stored as a dict in `version_info.advanced` instead of
  attributes on the `version_info` object.
  ([#1920](https://github.com/Pycord-Development/pycord/pull/1920))
- The `version_info.release_level` attribute has been reverted to its previous name,
  `releaselevel`. ([#1920](https://github.com/Pycord-Development/pycord/pull/1920))

### Fixed

- Fixed bugs in `Page.update_files` where file objects stored in memory were causing an
  `AttributeError`, and `io.BytesIO` files did not send properly more than once.
  ([#1869](https://github.com/Pycord-Development/pycord/pull/1869) &
  [#1881](https://github.com/Pycord-Development/pycord/pull/1881))
- Fixed bridge groups missing the `parent` attribute.
  ([#1823](https://github.com/Pycord-Development/pycord/pull/1823))
- Fixed issues with creating auto moderation rules.
  ([#1822](https://github.com/Pycord-Development/pycord/pull/1822))

## [2.3.3] - 2023-02-10

- Fixed an unhandled `KeyError` exception when receiving GIF stickers, causing crashes.
  ([#1915](https://github.com/Pycord-Development/pycord/pull/1915))

## [2.3.2] - 2022-12-03

### Fixed

- Fixed another `AttributeError` relating to the new `bridge_commands` attribute on
  `ext.bridge.Bot`. ([#1815](https://github.com/Pycord-Development/pycord/pull/1815))
- Fixed an `AttributeError` in select relating to the select type.
  ([#1814](https://github.com/Pycord-Development/pycord/pull/1814))
- Fixed `Thread.applied_tags` always returning an empty list.
  ([#1817](https://github.com/Pycord-Development/pycord/pull/1817))

## [2.3.1] - 2022-11-27

### Fixed

- Fixed `AttributeError` relating to the new `bridge_commands` attribute on
  `ext.bridge.Bot`. ([#1802](https://github.com/Pycord-Development/pycord/pull/1802))

## [2.3.0] - 2022-11-23

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
- Added `bridge_commands` attribute to `ext.bridge.Bot` for access to bridge command
  objects. ([#1787](https://github.com/Pycord-Development/pycord/pull/1787))
- Updated `Guild.features` to include new and previously missing features.
  ([#1788](https://github.com/Pycord-Development/pycord/pull/1788))

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
-

### Removed

- Removed the guild feature `PRIVATE_THREADS` due to paywall limitation removal.
  ([#1789](https://github.com/Pycord-Development/pycord/pull/1789))

## [2.2.2] - 2022-10-05

### Fixed

- Fixed `parent` attribute of second-level subcommands being set to the base level
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
- `proxy` and `proxy_auth` params to many Webhook-related methods.
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
- Fix type issues in `options.py`
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
- Avoid unnecessary calls to `sync_commands` during runtime.
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
- Fix busy-loop in `DecodeManager` when the decode queue is empty, causing 100% CPU
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
- Fix the error when Discord does not send the `app_permissions` data in `Interaction`.
  ([#1467](https://github.com/Pycord-Development/pycord/pull/1467))
- Fix AttributeError when voice client `play()` function is not completed yet.
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
- Component field limits are now enforced at the library level
  ([#1065](https://github.com/Pycord-Development/pycord/pull/1065) &
  [#1289](https://github.com/Pycord-Development/pycord/pull/1289))
- Support providing option channel types as a list.
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
- `Option` class and usage were rewritten.
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
- Make the channel `position` attribute optional.
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
- Remove voice client when the bot disconnects.
  ([#1273](https://github.com/Pycord-Development/pycord/pull/1273))
- Fix conversion exception in `ext.bridge`.
  ([#1250](https://github.com/Pycord-Development/pycord/pull/1250))
- `Context.me` returns ClientUser when guilds intent is absent.
  ([#1286](https://github.com/Pycord-Development/pycord/pull/1286))
- Updated `Message.edit` type-hinting overload and removed resulting redundant
  overloads. ([#1299](https://github.com/Pycord-Development/pycord/pull/1299))
- Improved validation regex for command names & options.
  ([#1309](https://github.com/Pycord-Development/pycord/pull/1309))
- Correct `Guild.fetch_members()` type-hints.
  ([#1323](https://github.com/Pycord-Development/pycord/pull/1323))
- Multiple fixes and enhancements for `PageGroup` handling.
  ([#1350](https://github.com/Pycord-Development/pycord/pull/1350))
- Make `TextChannel._get_channel` async.
  ([#1358](https://github.com/Pycord-Development/pycord/pull/1358))

## [2.0.0-beta.7] - 2022-04-09

### Fixed

- Fix py3.10 UnionType checks issue.
  ([#1240](https://github.com/Pycord-Development/pycord/pull/1240))

[unreleased]: https://github.com/Pycord-Development/pycord/compare/v2.7.0rc1...HEAD
[2.7.0rc1]: https://github.com/Pycord-Development/pycord/compare/v2.6.0...v2.7.0rc1
[2.6.1]: https://github.com/Pycord-Development/pycord/compare/v2.6.0...v2.6.1
[2.6.0]: https://github.com/Pycord-Development/pycord/compare/v2.5.0...v2.6.0
[2.5.0]: https://github.com/Pycord-Development/pycord/compare/v2.4.1...v2.5.0
[2.4.1]: https://github.com/Pycord-Development/pycord/compare/v2.4.0...v2.4.1
[2.4.0]: https://github.com/Pycord-Development/pycord/compare/v2.3.3...v2.4.0
[2.3.3]: https://github.com/Pycord-Development/pycord/compare/v2.3.2...v2.3.3
[2.3.2]: https://github.com/Pycord-Development/pycord/compare/v2.3.1...v2.3.2
[2.3.1]: https://github.com/Pycord-Development/pycord/compare/v2.3.0...v2.3.1
[2.3.0]: https://github.com/Pycord-Development/pycord/compare/v2.2.2...v2.3.0
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
