import asyncio
import logging
import os
import random
import shutil
import string
from typing import Any, Dict, Optional, Union, Tuple
from unittest import IsolatedAsyncioTestCase, TestResult

import aiohttp
import magic
import ssl
from aiohttp.client_reqrep import ClientResponse
from aiohttp.client_exceptions import ServerDisconnectedError
from discord.http import HTTPClient, Route
from persistqueue import SQLiteQueue
from proxy import Proxy

from parsing import CombinedHttpRequest

RANDOM_ID_CHARS = string.ascii_letters + string.digits

logging.getLogger('proxy').setLevel(logging.WARNING)

if os.name == 'nt':  # SSL on windows breaks without this
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)


class PyCordBaseTestCase(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        """Called to set up environment before testing"""
        super().setUp()
        self.proxy_url = "http://localhost:8899"
        self.ssl = ssl.create_default_context(
            cafile=os.getenv('PYCORD_CERT_PATH'))
        self.request_queue = SQLiteQueue('testing.q')
        # Setting default value allows pycord to raise LoginFailure
        self.token = os.getenv('PYCORD_BOT_TOKEN', '')
        self.http_client = HTTPClient(proxy=self.proxy_url)
        self.request_ids = set()
        await self.http_client.static_login(self.token)

    def _generate_request_id(self) -> str:
        """Generates a unique request ID

        Returns
        -------
        str
            A four digit unique request ID
        """
        new_id = ''.join(random.sample(RANDOM_ID_CHARS, 4))
        # Ensure that a random ID does not clash
        if new_id in self.request_ids:
            return self._generate_request_id()
        else:
            self.request_ids.add(new_id)
            return new_id

    def _tracking_header(self) -> Dict[str, str]:
        """Generate a header used to track request

        Returns
        -------
        Dict[str, str]
            A dictionary intended to be merged with all other headers
        """
        return {'X-PyCord-Testing-ReqId': self._generate_request_id()}

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
                '--ca-key-file', 'pycord-key.pem',
                '--ca-cert-file', 'pycord-cert.pem',
                '--ca-signing-key-file', 'pycord-signkey.pem',
                '--port', '8899']
        ):
            super().run(result)

    async def proxied_route_request(self,
                                    route: Route,
                                    allow_through_proxy: bool = False,
                                    ) -> Tuple[CombinedHttpRequest, Optional[Union[Dict[str, Any], str]]]:
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
        Returns
        -------
        Tuple[HttpParser, Optional[Union[Dict[str, Any], str]]]
            A tuple containing the request, and the response if it was
            allowed through, otherwise None
        """

        try:
            resp = await self.http_client.request(route, ssl=self.ssl, headers={
                'X-Allow-Through': str(int(allow_through_proxy))
            } | self._tracking_header())
        except ServerDisconnectedError:  # Raised when the proxy blocks request
            resp = None
        finally:
            # Queue module has weird typing that creates errors
            req: CombinedHttpRequest = self.request_queue.get()  # type: ignore
            # Ignore unreachable code warning, as resp is always not None
            # provided the try block is executed or ServerDisconnectedError is raised
            return (req, resp)  # type: ignore

    async def proxied_request(self,
                              method: str,
                              url: str,
                              allow_through_proxy: bool = False,
                              headers: Dict[str, str] = {},
                              body: Union[str, bytes, Dict[str, Any]] = ''
                              ) -> Tuple[CombinedHttpRequest, Optional[ClientResponse]]:
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
        Returns
        -------
        Tuple[HttpParser, Optional[Union[Dict[str, Any], str]]]
            A tuple containing the request, and the response if it was
            allowed through, otherwise None
        """
        try:
            with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
                content_type = m.id_buffer(body)
            async with aiohttp.ClientSession(headers={
                'Connection': 'close',
                'Content-Type': content_type,
                'X-Allow-Through': str(int(allow_through_proxy))
            } | self._tracking_header() | headers) as cs:
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
                        ssl=self.ssl) as r:
                    resp = r
        except ServerDisconnectedError:  # Raised when the proxy blocks request
            resp = None
        finally:
            # Queue module has weird typing that creates errors
            req: CombinedHttpRequest = self.request_queue.get()  # type: ignore
            # Ignore unreachable code warning, as resp is always not None
            # provided the try block is executed or ServerDisconnectedError is raised
            return (req, resp)  # type: ignore


class TestPyCordTestingFixtures(PyCordBaseTestCase):

    async def test_proxy_sends(self) -> None:
        """Tests if the proxy will allow requests through"""
        _, resp = await self.proxied_request(
            'GET',
            'https://httpbin.org/get',
            allow_through_proxy=True)
        # Ignores the NoneType checking error, as it is guarenteed to not be None
        self.assertEqual(resp.status, 200)  # type: ignore

    async def test_proxy_blocks(self) -> None:
        """Tests if the proxy blocks requests"""
        _, resp = await self.proxied_request('GET', 'https://httpbin.org/get', allow_through_proxy=False)
        self.assertIsNone(resp)
