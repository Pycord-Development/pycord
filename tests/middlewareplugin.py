import logging
from typing import Any, Dict, List, Optional

from persistqueue import SQLiteQueue
from proxy.plugin import CacheResponsesPlugin
from proxy.http.exception import HttpRequestRejected
from proxy.http.parser import HttpParser

from parsing import CombinedHttpRequest

RequestTrackingDict = Dict[bytes, HttpParser]


class PyCordTestMiddleware(CacheResponsesPlugin):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.q = SQLiteQueue(path='testing.q')
        self.request_tracker: RequestTrackingDict = {}

    def __del__(self):
        del self.q

    def handle_client_request(self, request: HttpParser) -> Optional[HttpParser]:
        super().handle_client_request(request)
        header_present = request.has_header(b'X-Allow-Through')
        request_tracked = request.has_header(b'X-PyCord-Testing-ReqId')
        if request_tracked:
            request_id = request.header(b'X-PyCord-Testing-ReqId')
        # Allow the initial CONNECT request go through and block the following one
        if request.method == b'CONNECT':
            logging.info(
                f"Allowing CONNECT request to {request.host.decode('utf-8')!r} Tracking ID: {request_id.decode('utf-8') if request_tracked else None!r}")
            # First time around, request is allowed and is added to tracked requests
            if request_tracked:
                self.request_tracker[request_id] = request
            return request
        else:
            if request_tracked:
                first_request = self.request_tracker.pop(request_id)
                merged = CombinedHttpRequest.from_request_pair(
                    first_request, request)
                self.q.put(merged)

            destination = request.url.netloc.decode(
                'utf-8') if request.url.netloc else request.url.path.decode('utf-8')
            if not header_present or bool(int(request.header(b'X-Allow-Through'))):
                logging.info(
                    f"Allowing request to {destination!r} Tracking ID: {request_id.decode('utf-8') if request_tracked else None!r}")
                return request
            else:
                logging.info(
                    f"Rejecting request to {destination!r} Tracking ID: {request_id.decode('utf-8') if request_tracked else None!r}")
                raise HttpRequestRejected
