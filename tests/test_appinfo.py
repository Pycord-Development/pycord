from __future__ import annotations

import pytest

from discord import utils
from discord.appinfo import AppInstallParams, IntegrationTypesConfig


def _ctx(scopes: list[str], permissions: str = "0") -> dict:
    return {"oauth2_install_params": {"scopes": scopes, "permissions": permissions}}


def test_from_payload_none() -> None:
    assert IntegrationTypesConfig.from_payload(None) is None


def test_guild_only_payload_does_not_invent_user_context() -> None:
    config = IntegrationTypesConfig.from_payload({"0": _ctx(["bot"], "8")})

    assert config is not None
    assert isinstance(config.guild, AppInstallParams)
    assert config.user is utils.MISSING
    assert set(config._to_payload()) == {0}


def test_user_only_payload_does_not_invent_guild_context() -> None:
    config = IntegrationTypesConfig.from_payload({1: _ctx(["applications.commands"])})

    assert config is not None
    assert config.guild is utils.MISSING
    assert isinstance(config.user, AppInstallParams)
    assert set(config._to_payload()) == {1}


def test_both_contexts_round_trip() -> None:
    config = IntegrationTypesConfig.from_payload(
        {"0": _ctx(["bot"], "8"), "1": _ctx(["applications.commands"])}
    )

    assert config is not None
    assert set(config._to_payload()) == {0, 1}


@pytest.mark.parametrize("empty", [None, {}, {"oauth2_install_params": None}])
def test_present_but_empty_context_is_preserved_as_none(empty) -> None:
    config = IntegrationTypesConfig.from_payload({"0": empty})

    assert config is not None
    assert config.guild is None
    assert config.user is utils.MISSING
    assert config._to_payload() == {0: None}


def test_empty_payload_serializes_to_empty() -> None:
    config = IntegrationTypesConfig.from_payload({})

    assert config is not None
    assert config._to_payload() == {}
