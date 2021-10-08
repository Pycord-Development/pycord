from typing import Optional

from persistqueue import SQLiteQueue
from proxy.plugin import CacheResponsesPlugin
from proxy.http.exception import HttpRequestRejected
from proxy.http.parser import HttpParser


class PyCordTestMiddleware(CacheResponsesPlugin):

    def handle_client_request(self, request: HttpParser) -> Optional[HttpParser]:
        super().handle_client_request(request)
        q = SQLiteQueue(path='testing.q')
        q.put(request)
        del q
        header_present = 'X-Allow-Through' in request.headers.keys()
        if not header_present or bool(int(request.header(b'X-Allow-Through'))):
            return request
        else:
            raise HttpRequestRejected
