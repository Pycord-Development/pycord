import logging
from typing import Optional

from persistqueue import SQLiteAckQueue
from proxy.plugin import CacheResponsesPlugin
from proxy.http.exception import HttpRequestRejected
from proxy.http.parser import HttpParser

class PyCordTestMiddleware(CacheResponsesPlugin):

    def handle_client_request(self, request: HttpParser) -> Optional[HttpParser]:
        super().handle_client_request(request)
        q = SQLiteAckQueue(path='testing.q')
        allow = bool(int(request.header(b'X-Allow-Through')))
        q.put(request)
        if allow:
            return request
        else:
            raise HttpRequestRejected

