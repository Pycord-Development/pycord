from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import shutil
import ssl
import string
from contextlib import contextmanager
from typing import Any, Dict, Generator, Union
from unittest import IsolatedAsyncioTestCase, TestResult
from unittest.mock import PropertyMock, patch

import aiohttp
import magic
from aiohttp.client import ClientSession
from aiohttp.client_exceptions import ServerDisconnectedError
from aiohttp.client_reqrep import ClientResponse
from multidict import CIMultiDict
from parsing import CombinedHttpRequest
from persistqueue import PDict
from proxy import Proxy
from yarl import URL

import discord
from discord.client import Client
from discord.http import HTTPClient, Route

RANDOM_ID_CHARS = string.ascii_letters + string.digits

RouteTrackingContext = Generator[None, None, None]
JsonDict = Dict[str, Union[str, bool, int, None]]

logging.getLogger("proxy").setLevel(logging.WARNING)

if os.name == "nt":  # SSL on windows breaks without this
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)


class PyCordBaseTestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        """Called to set up environment before testing"""
        logging.info("Starting setUp()")
        super().setUp()
        for var in ("CERT_PATH", "BOT_TOKEN", "TEST_MODE"):
            if os.getenv(f"PYCORD_{var}") is None:
                raise RuntimeError(f"PYCORD_{var} is not set")
        for var in ("cert", "key", "signkey"):
            filename = f"pycord-{var}.pem"
            assert os.path.exists(
                os.path.join(os.path.dirname(__file__), filename)
            ), f"{filename} does not exist"
        self.proxy_url = "http://localhost:8899"
        self.ssl = ssl.create_default_context(cafile=os.getenv("PYCORD_CERT_PATH"))
        self.request_queue = PDict("testing.q", "requests")
        # Setting default value allows pycord to raise LoginFailure
        self.token = os.getenv("PYCORD_BOT_TOKEN", "")
        self.client = Client(proxy=self.proxy_url)
        self.request_ids = set()
        await self.client.login(self.token)
        logging.info("Finished setUp()")

    @contextmanager
    def assertRouteCalled(
        self,
        route: Route,
        allow_through_proxy: bool = False,
        mock_response=None,
        params: dict[str, str] | None = None,
    ) -> RouteTrackingContext:
        """Context manager to check if a route is called in its body

        Parameters
        ----------
        route: Route
            The route to test for
        allow_through_proxy: bool
            Weather or not to allow requests through proxy inside the block
        mock_response
            A mock response to return. Will override the actual response even if ``allow_through_proxy`` is True.
        """
        request_bin = self._create_request_bin()
        client_request_method = HTTPClient.request

        async def wrapped_route_request(*args, **kwargs):
            kwargs["proxy"] = self.proxy_url
            kwargs["ssl"] = self.ssl
            try:
                resp = await client_request_method(*args, **kwargs)
            except ServerDisconnectedError:
                # When the request is blocked
                resp = None
            if mock_response is not None:
                resp = mock_response
            return resp

        with patch.object(HTTPClient, "request", wrapped_route_request):
            logging.info("Patched HTTPClient request method")
            with patch.object(
                ClientSession,
                "_default_headers",
                create=True,
                new_callable=PropertyMock,
                return_value=CIMultiDict(
                    {
                        "X-Allow-Through": str(int(allow_through_proxy)),
                        "X-PyCord-Testing-ReqId": request_bin,
                    }
                ),
            ):
                logging.info("Patched session headers")
                yield

        logging.info("All patches reversed")

        filled_bin: list[CombinedHttpRequest] = self.request_queue[request_bin]
        all_visited_urls = {req.full_url for req in filled_bin}
        target_url = URL(route.url)
        if params is not None:
            target_url = target_url.with_query(params)
        target_url = str(target_url).split("://")[-1]
        route_visited = target_url in all_visited_urls
        if not route_visited:
            raise AssertionError(
                f"Route {route.path!r} was not visited, visited URLs: {all_visited_urls}, route: {target_url}"
            )
        else:
            logging.info(f"Route {target_url!r} was called, assertion passed!")

    def _create_request_bin(self) -> str:
        """Generates a unique request ID

        Returns
        -------
        str
            A bucket marker plus a four digit unique request ID
        """
        return f"bucket:{self._generate_request_id()}"

    def _generate_request_id(self) -> str:
        """Generates a unique request ID

        Returns
        -------
        str
            A four digit unique request ID
        """
        new_id = "".join(random.sample(RANDOM_ID_CHARS, 4))
        # Ensure that a random ID does not clash
        if new_id in self.request_ids:
            return self._generate_request_id()
        else:
            self.request_ids.add(new_id)
            return new_id

    def _tracking_header(self, reqid: str) -> dict[str, str]:
        """Generate a header used to track request

        Parameters
        ----------
        reqid: int
            A four character unique string to be used as the request ID

        Returns
        -------
        Dict[str, str]
            A dictionary intended to be merged with all other headers
        """
        return {"X-PyCord-Testing-ReqId": reqid}

    async def asyncTearDown(self) -> None:
        """Called to take down environment after testing"""
        super().tearDown()
        del self.request_queue
        await self.client.close()

    def run(self, result: TestResult | None = None) -> None:
        """Ensure the tests are run with a running proxy"""
        with Proxy(
            [
                "--num-workers",
                "1",
                "--plugins",
                "middlewareplugin.PyCordTestMiddleware",
                "--ca-key-file",
                "pycord-key.pem",
                "--ca-cert-file",
                "pycord-cert.pem",
                "--ca-signing-key-file",
                "pycord-signkey.pem",
                "--port",
                "8899",
            ]
        ):
            super().run(result)
        shutil.rmtree("testing.q")

    async def proxied_route_request(
        self, route: Route, allow_through_proxy: bool = False, mock_response=None
    ) -> tuple[CombinedHttpRequest, dict[str, Any] | str | None]:
        """Send a request through the proxy to view request data

        This function will make a request to a URL through the testing proxy
        which will dump the request out and prevent it from being sent to
        discord's servers. This allows functionality to be tested without
        any side-effects

        Parameters
        ----------
        route: Route
            The API endpoint to make the request to
        allow_through_proxy: bool
            Should the request continue to the destination? (defaults to False)
        headers: Optional[dict]
            The headers to be sent with the request, defaults to an empty dict
        mock_response
            A mock response to return. Will override the actual response even if ``allow_through_proxy`` is True.

        Returns
        -------
        Tuple[HttpParser, Optional[Union[Dict[str, Any], str]]]
            A tuple containing the request, and the response if it was
            allowed through, otherwise None
        """
        reqid = self._generate_request_id()
        try:
            resp = await self.client.http.request(
                route,
                ssl=self.ssl,
                headers={
                    "X-Allow-Through": str(int(allow_through_proxy)),
                    **self._tracking_header(reqid),
                },
            )
        except ServerDisconnectedError:  # Raised when the proxy blocks request
            resp = None
        finally:
            if mock_response is not None:
                resp = mock_response
            # Queue module has weird typing that creates errors
            req: CombinedHttpRequest = self.request_queue.get()  # type: ignore
            # Ignore unreachable code warning, as resp is always not None
            # provided the try block is executed or ServerDisconnectedError is raised
            return (req, resp)  # type: ignore

    async def proxied_request(
        self,
        method: str,
        url: str,
        allow_through_proxy: bool = False,
        headers: dict[str, str] = {},
        body: str | bytes | dict[str, Any] = "",
        mock_response: ClientResponse | None = None,
    ) -> tuple[CombinedHttpRequest, ClientResponse | None]:
        """Send a request through the proxy to view request data

        This function will make a request to a URL through the testing proxy
        which will dump the request out and prevent it from being sent to
        discord's servers. This allows functionality to be tested without
        any side-effects

        Parameters
        ----------
        method: str
            The request method(GET, POST, etc)
        url: str
            The URL to request
        allow_through_proxy: bool
            Should the request continue to the destination? (defaults to False)
        headers: Optional[dict]
            The headers to be sent with the request, defaults to an empty dict
        body: Union[str, bytes, Dict[str, Any]]
            The body of the request, can either be
            a string, json data, or raw bytes
        mock_response: Optional[ClientResponse]
            A mock response to return. Will override the actual response even if ``allow_through_proxy`` is True.

        Returns
        -------
        Tuple[HttpParser, Optional[Union[Dict[str, Any], str]]]
            A tuple containing the request, and the response if it was
            allowed through, otherwise None
        """

        reqid = self._generate_request_id()
        try:
            content_type = magic.from_buffer(body, mime=True)
            async with aiohttp.ClientSession(
                headers={
                    "Connection": "close",
                    "Content-Type": content_type,
                    "X-Allow-Through": str(int(allow_through_proxy)),
                    **self._tracking_header(reqid),
                    **headers,
                }
            ) as cs:
                if type(body) is dict:
                    json = body
                    data = None
                else:
                    json = None
                    data = body

                async with cs.request(
                    method,
                    url,
                    proxy=self.proxy_url,
                    data=data,
                    json=json,
                    ssl=self.ssl,
                ) as r:
                    resp = r
        except ServerDisconnectedError:  # Raised when the proxy blocks request
            resp = None
        finally:
            if mock_response is not None:
                resp = mock_response
            req: CombinedHttpRequest = self.request_queue[reqid]
            logging.info(f"Reading request {reqid!r} from queue")
            # Ignore unreachable code warning, as resp is always not None
            # provided the try block is executed or ServerDisconnectedError is raised
            return (req, resp)  # type: ignore


class TestPyCordTestingFixtures(PyCordBaseTestCase):
    async def test_route_visited(self) -> None:
        r = Route("GET", "/users/@me")
        with self.assertRouteCalled(r, allow_through_proxy=True):
            await self.client.http.request(r)


class TestPyCordGuild(PyCordBaseTestCase):
    _GUILD_ID = 881207955029110855

    def _route(self, method: str, path: str, **parameters) -> Route:
        """Helper function to create a route prefixed with /guilds/{self._GUILD_ID}"""
        return Route(method, f"/guilds/{self._GUILD_ID}{path}", **parameters)

    async def test_get_guild(self) -> None:
        with open("data/guild.json") as f:
            data = json.load(f)
        r = self._route("GET", "")
        with self.assertRouteCalled(r, params=dict(with_counts=1), mock_response=data):
            guild = await self.client.fetch_guild(881207955029110855)
        guild_dict = dict(
            id=str(guild.id),
            name=guild.name,
            icon=guild.icon.key if guild.icon else None,
            description=guild.description,
            splash=guild.splash.key if guild.splash else None,
            discovery_splash=guild.discovery_splash.key
            if guild.discovery_splash
            else None,
            features=guild.features,
            approximate_member_count=guild.approximate_member_count,
            approximate_presence_count=guild.approximate_presence_count,
            emojis=[
                dict(
                    name=emoji.name,
                    roles=emoji.roles,
                    id=str(emoji.id),
                    require_colons=emoji.require_colons,
                    managed=emoji.managed,
                    animated=emoji.animated,
                    available=emoji.available,
                )
                for emoji in guild.emojis
            ],
            stickers=[
                dict(
                    id=str(sticker.id),
                    name=sticker.name,
                    tags=sticker.emoji,
                    type=sticker.type.value,
                    format_type=sticker.format.value,
                    description=sticker.description,
                    asset="",  # Deprecated
                    available=sticker.available,
                    guild_id=str(sticker.guild_id),
                )
                for sticker in guild.stickers
            ],
            banner=guild.banner.key if guild.banner else None,
            owner_id=str(guild.owner_id),
            application_id=data["application_id"],  # TODO: Fix
            region=data["region"],  # Deprecated
            afk_channel_id=str(guild.afk_channel.id) if guild.afk_channel else None,
            afk_timeout=guild.afk_timeout,
            system_channel_id=str(guild._system_channel_id)
            if guild._system_channel_id
            else None,
            widget_enabled=data["widget_enabled"],  # TODO: Fix
            widget_channel_id=data["widget_channel_id"],  # TODO: Fix
            verification_level=guild.verification_level.value,
            roles=[
                dict(
                    id=str(role.id),
                    name=role.name,
                    permissions=str(role.permissions.value),
                    position=role.position,
                    color=role.color.value,
                    hoist=role.hoist,
                    managed=role.managed,
                    mentionable=role.mentionable,
                    icon=role.icon.key if role.icon else None,
                    unicode_emoji=role.unicode_emoji,
                    flags=list(
                        filter(lambda d: d["id"] == str(role.id), data["roles"])
                    )[0][
                        "flags"
                    ],  # TODO: Fix
                )
                for role in guild.roles
            ],
            default_message_notifications=guild.default_notifications.value,
            mfa_level=guild.mfa_level,
            explicit_content_filter=guild.explicit_content_filter.value,
            max_presences=guild.max_presences,
            max_members=guild.max_members,
            max_stage_video_channel_users=data[
                "max_stage_video_channel_users"
            ],  # TODO: Fix
            max_video_channel_users=guild.max_video_channel_users,
            vanity_url_code=data["vanity_url_code"],  # TODO: Fix
            premium_tier=guild.premium_tier,
            premium_subscription_count=guild.premium_subscription_count,
            system_channel_flags=guild.system_channel_flags.value,
            preferred_locale=guild.preferred_locale,
            rules_channel_id=str(guild._rules_channel_id)
            if guild._rules_channel_id
            else None,
            public_updates_channel_id=str(guild._public_updates_channel_id)
            if guild._public_updates_channel_id
            else None,
            hub_type=data["hub_type"],  # TODO: Fix
            premium_progress_bar_enabled=guild.premium_progress_bar_enabled,
            nsfw=data["nsfw"],  # TODO: Fix
            nsfw_level=guild.nsfw_level.value,
        )
        self.assertDictEqual(guild_dict, data)
