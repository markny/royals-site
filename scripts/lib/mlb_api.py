import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://statsapi.mlb.com/api/v1"
ROYALS_TEAM_ID = 118


class MlbApiError(RuntimeError):
    pass


def get_json(path, params=None, timeout=20):
    query = f"?{urlencode(params)}" if params else ""
    request = Request(
        f"{BASE_URL}{path}{query}",
        headers={"User-Agent": "royals-season-tracker/0.1"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise MlbApiError(str(exc)) from exc
