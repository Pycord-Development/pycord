import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar, Union

from proxy.http.parser import HttpParser

T = TypeVar('T', bound='CombinedHttpRequest')


@dataclass
class CombinedHttpRequest:
    headers: Dict[str, str]
    host: str
    path: str
    body: Optional[Union[str, bytes, Dict[str, Any]]]

    @classmethod
    def from_request_pair(cls: Type[T], connect_req: HttpParser, final_req: HttpParser) -> T:
        headers_merged = connect_req.headers | final_req.headers
        parsed_headers = {k.decode('utf-8'): v.decode('utf-8')
                          for k, v in headers_merged.values()}
        host = connect_req.url.netloc.decode('utf-8').split(':')[0]
        path = final_req.url.path.decode('utf-8')
        content_type = parsed_headers['Content-Type']
        if content_type == 'text/plain':
            body = final_req.body.decode('utf-8')
        elif content_type == 'application/json':
            body = json.loads(final_req.body)
        else:
            body = final_req.body
        return cls(headers=parsed_headers, host=host, body=body, path=path)
