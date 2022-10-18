import functools
import requests

from requests.adapters import HTTPAdapter, Retry


class ModelSessionMeta(type):
    """Meta class that is used to create a static attribute called request.
    This request attribute can be used just like the regular 'requests'
    function from the requests module.

    This prevents having to do a new handshake for every request
    we send towards the API.
    """

    @property
    def request(cls) -> requests.Session:
        if not cls._request_session:
            cls._request_session = requests.Session()
            cls._request_session.request = functools.partial(
                cls._request_session.request,
                timeout=9,
            )
            adapter = HTTPAdapter(
                max_retries=Retry(
                    total=2,
                    backoff_factor=0.3,
                    status_forcelist=[500, 502, 503, 504],
                )
            )
            cls._request_session.mount("http://", adapter)
            cls._request_session.mount("https://", adapter)
        return cls._request_session


class ModelSessionMixin(metaclass=ModelSessionMeta):
    _request_session: requests.Session | None = None
