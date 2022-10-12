import logging
from typing import Any, Dict, Optional

from persistqueue import SQLiteQueue, PDict
from proxy.plugin import CacheResponsesPlugin
from proxy.http.exception import HttpRequestRejected
from proxy.http.parser import HttpParser

from parsing import CombinedHttpRequest

RequestTrackingDict = Dict[str, HttpParser]


class PyCordTestMiddleware(CacheResponsesPlugin):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.q = PDict('testing.q', 'requests')
        self.request_tracker: RequestTrackingDict = {}

    def __del__(self):
        del self.q

    def handle_client_request(self, request: HttpParser) -> Optional[HttpParser]:
        super().handle_client_request(request)
        # Asserts to get rid of type warnings, these should never fail
        header_present = request.has_header(b'X-Allow-Through')
        request_tracked = request.has_header(b'X-PyCord-Testing-ReqId')
        tracking_to_bin = False
        if request_tracked:
            request_id = request.header(
                b'X-PyCord-Testing-ReqId').decode('utf-8')
            if request_id.startswith('bucket'):
                tracking_to_bin = True
        else:
            request_id = 'aaaa'  # Assigning a dummy value, this should never be dumped into the queue
        # Allow the initial CONNECT request go through and block the following one
        if request.method == b'CONNECT':
            logging.info(
                f"Allowing CONNECT request to {request.host.decode('utf-8')!r} Tracking ID: {request_id if request_tracked else None!r}")
            # First time around, request is allowed and is added to tracked requests
            if request_tracked:
                if tracking_to_bin:
                    self.request_tracker[f'{request_id}:connect'] = request
                else:
                    self.request_tracker[request_id] = request
            return request
        else:
            if request_tracked:
                if tracking_to_bin:
                    first_request = self.request_tracker.pop(
                        f'{request_id}:connect')
                else:
                    first_request = self.request_tracker.pop(request_id)
                merged = CombinedHttpRequest.from_request_pair(
                    first_request, request)
                if tracking_to_bin:
                    q = self.q.get(request_id, [])
                    q.append(merged)
                    self.q[request_id] = q
                    logging.info(
                        f'Placing request into bucket: {request_id.removeprefix("bucket:")!r}')
                else:
                    self.q[request_id] = merged
                    logging.info(f'Placing request {request_id!r} into queue')

            # destination = request._url.hostname
            destination = request._url.hostname.decode(
                'utf-8') if request._url.hostname else request._url.remainder.decode('utf-8')
            if not header_present or bool(int(request.header(b'X-Allow-Through'))):
                logging.info(
                    f"Allowing request to {destination!r} Tracking ID: {request_id if request_tracked else None!r}")
                return request
            else:
                logging.info(
                    f"Rejecting request to {destination!r} Tracking ID: {request_id if request_tracked else None!r}")
                raise HttpRequestRejected
