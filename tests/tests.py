import shutil
from typing import Dict, Optional, Union
from unittest import IsolatedAsyncioTestCase, TestResult

import aiohttp
import ssl
from aiohttp.client_reqrep import ClientResponse
from aiohttp.client_exceptions import ServerDisconnectedError
from persistqueue import SQLiteAckQueue
from proxy import Proxy

class PyCordBaseTestCase(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        """Called to set up environment before testing"""
        super().setUp()

    def tearDown(self) -> None:
        """Called to take down environment after testing"""
        super().tearDown()
        shutil.rmtree('testing.q')

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

    async def proxied_request(self,
                              url: str,
                              method: str,
                              allow_through_proxy: bool=False,
                              headers: Dict[str, str]={}
                              ) -> Optional[ClientResponse]:
        """Send a request through the proxy to view request data

        This function will make a request to a URL through the testing proxy
        which will dump the request out and prevent it from being sent to
        discord's servers. This allows functionality to be tested without
        any side-effects

        Parameters
        ----------
        url : str
            The URL to request
        method : str
            The request method (GET, POST, etc)
        allow_through_proxy : bool
            Should the request continue to the destination? (defaults to False)
        headers : Optional[dict]
            The headers to be sent with the request, defaults to an empty dict
        Returns
        -------
        Optional[ClientResponse]
            If the request was allowed, the response is returned
        """
        sslcontext = ssl.create_default_context(cafile='ca-cert.pem')
        proxy = 'http://localhost:8899'

        try:
            async with aiohttp.ClientSession(headers={'X-Allow-Through': str(int(allow_through_proxy))}|headers) as cs:
                async with cs.request(method, url, proxy=proxy, ssl=sslcontext) as r:
                    return r
        except ServerDisconnectedError:
            return None

class TestTest(PyCordBaseTestCase):

    async def test_proxy_sends(self) -> None:
        q = SQLiteAckQueue('testing.q')
        resp = await self.proxied_request('https://www.httpbin.org/get', 'GET', allow_through_proxy=True)
        req = q.get()
        q.ack(req)
        self.assertEqual(resp.status, 200)
