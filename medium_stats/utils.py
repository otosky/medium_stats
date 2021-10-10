from datetime import datetime
from datetime import timezone
from importlib.util import find_spec
from typing import List
from typing import Sequence

from typing_extensions import Type

extras = ("selenium", "webdriver_manager")


def check_dependencies_missing(extras: Sequence[str] = extras) -> List[str]:
    missing = [e for e in extras if not bool(find_spec(e))]
    return missing


def valid_date(ds: str, error: Type[Exception] = ValueError) -> datetime:
    if len(ds) > 10:
        dt_format = "%Y-%m-%dT%H:%M:%S"
        help_txt = "YYYY-MM-DDThh:mm:ss"
    else:
        dt_format = "%Y-%m-%d"
        help_txt = "YYYY-MM-DD"

    try:
        dt = datetime.strptime(ds, dt_format)
        return dt
    except ValueError:
        msg = f"'{ds}' cannot be parsed as datetime - must be of form {help_txt}"
        raise error(msg)


def dt_formatter(dt: datetime, output: str) -> str:

    if output == "json":
        dt = dt.strftime("%Y-%m-%dT%H:%M:%S")
    elif output == "filename":
        dt = dt.strftime("%Y%m%dT%H%M%S")
    else:
        raise ValueError(f'output param must be either "json" or "filename" not "{output}"')

    return dt


def make_utc_explicit(dt: datetime, utc_naive: bool) -> datetime:

    if utc_naive:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def convert_datetime_to_unix(dt: datetime, ms: bool = True) -> int:

    dt = dt.replace(tzinfo=timezone.utc)
    dt = int(dt.timestamp())

    if ms:
        dt = dt * 1000

    return dt
