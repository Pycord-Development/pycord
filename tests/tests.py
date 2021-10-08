import asyncio
import os
import shutil
from typing import Any, Dict, Optional, Union, Tuple
from unittest import IsolatedAsyncioTestCase, TestResult

import aiohttp
import ssl
from aiohttp.client_reqrep import ClientResponse
from aiohttp.client_exceptions import ServerDisconnectedError
from discord.http import HTTPClient, Route
from persistqueue import SQLiteQueue
from proxy.http.parser import HttpParser
from proxy import Proxy

if os.name == 'nt':  # SSL on windows breaks without this
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)


class PyCordBaseTestCase(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        """Called to set up environment before testing"""
        super().setUp()
        self.proxy_url = "http://localhost:8899"
        self.ssl = ssl.create_default_context(cafile='ca-cert.pem')
        self.request_queue = SQLiteQueue('testing.q')
        self.token = os.environ.get('PYCORD_BOT_TOKEN')
        self.http_client = HTTPClient(proxy=self.proxy_url)
        await self.http_client.static_login(self.token)

    async def asyncTearDown(self) -> None:
        """Called to take down environment after testing"""
        super().tearDown()
        del self.request_queue
        shutil.rmtree('testing.q')
        await self.http_client.close()

    def run(self, result: Optional[TestResult] = None) -> None:
        """Ensure the tests are run with a running proxy"""
        with Proxy([
                '--num-workers', '1',
                '--plugins', 'middlewareplugin.PyCordTestMiddleware',
                '--ca-key-file', 'ca-key.pem',
                '--ca-cert-file', 'ca-cert.pem',
                '--ca-signing-key-file', 'ca-signing-key.pem',
                '--port', '8899']
                ):
            super().run(result)

    async def proxied_route_request(self,
                                    route: Route,
                                    allow_through_proxy: bool = False,
                                    ) -> Tuple[HttpParser, Optional[Union[Dict[str, Any], str]]]:
        """Send a request through the proxy to view request data

        This function will make a request to a URL through the testing proxy
        which will dump the request out and prevent it from being sent to
        discord's servers. This allows functionality to be tested without
        any side-effects

        Parameters
        ----------
        route : Route
            The API endpoint to make the request to
        allow_through_proxy : bool
            Should the request continue to the destination? (defaults to False)
        headers : Optional[dict]
            The headers to be sent with the request, defaults to an empty dict
        Returns
        -------
        Tuple[HttpParser, Optional[Union[Dict[str, Any], str]]]
            A tuple containing the request, and the response if it was
            allowed through, otherwise None
        """

        try:
            resp = await self.http_client.request(route, ssl=self.ssl, headers={
                'X-Allow-Through': str(int(allow_through_proxy))
            })
        except ServerDisconnectedError:  # Raised when the proxy blocks request
            resp = None
        finally:
            req = self.request_queue.get()
            return(req, resp)

    async def proxied_request(self,
                              method: str,
                              url: str,
                              allow_through_proxy: bool = False,
                              headers: Dict[str, str] = {}
                              ) -> Tuple[HttpParser, Optional[ClientResponse]]:
        """Send a request through the proxy to view request data

        This function will make a request to a URL through the testing proxy
        which will dump the request out and prevent it from being sent to
        discord's servers. This allows functionality to be tested without
        any side-effects

        Parameters
        ----------
        method : str
            The request method (GET, POST, etc)
        url : str
            The URL to request
        allow_through_proxy : bool
            Should the request continue to the destination? (defaults to False)
        headers : Optional[dict]
            The headers to be sent with the request, defaults to an empty dict
        Returns
        -------
        Tuple[HttpParser, Optional[Union[Dict[str, Any], str]]]
            A tuple containing the request, and the response if it was
            allowed through, otherwise None
        """

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.request(
                        method,
                        url,
                        proxy=self.proxy_url,
                        ssl=self.ssl, headers={
                            'X-Allow-Through': str(int(allow_through_proxy))
                            } | headers) as r:
                    resp = r
        except ServerDisconnectedError:  # Raised when the proxy blocks request
            resp = None
        finally:
            req = self.request_queue.get()
            return (req, resp)


class TestPyCordTestingFixtures(PyCordBaseTestCase):

    async def test_proxy_sends(self) -> None:
        _, resp = await self.proxied_request(
            'GET',
            'https://discord.com',
            allow_through_proxy=True)
        self.assertEqual(resp.status, 200)
