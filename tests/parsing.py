import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar, Union

from proxy.http.parser import HttpParser

T = TypeVar("T", bound="CombinedHttpRequest")


@dataclass
class CombinedHttpRequest:
    headers: Dict[str, str]
    host: str
    path: str
    full_url: str
    body: Optional[Union[str, bytes, Dict[str, Any]]]

    @classmethod
    def from_request_pair(
        cls: Type[T], connect_req: HttpParser, final_req: HttpParser
    ) -> T:

        headers_merged = connect_req.headers | final_req.headers
        parsed_headers = {
            k.decode("utf-8"): v.decode("utf-8") for k, v in headers_merged.values()
        }
        logging.info(str(connect_req.type))
        logging.info(str(final_req.protocol))
        # scheme = connect_req._url.scheme.decode('utf-8')
        # host = connect_req._url.netloc.decode('utf-8').split(':')[0]
        host = connect_req.host.decode("utf-8")
        path = final_req.path.decode("utf-8")
        full_url = f"{host}{path}"
        content_type = parsed_headers.get("Content-Type", None)

        if content_type == "application/json":
            body = json.loads(final_req.body)
        else:
            body = None

        return cls(
            headers=parsed_headers, host=host, body=body, path=path, full_url=full_url
        )
