from datetime import datetime
from datetime import timezone
from importlib.util import find_spec
from typing import Sequence, List

extras = ("selenium", "webdriver_manager")


def check_dependencies_missing(extras: Sequence[str]=extras) -> List[str]:
    dependencies = [bool(find_spec(e)) for e in extras]
    if sum(dependencies) == len(extras):
        return []

    missing = [z[0] for z in zip(extras, dependencies) if not z[1]]
    return missing


def valid_date(ds: str, error: Exception)-> datetime:
    if len(ds) > 10:
        try:
            dt = datetime.strptime(ds, "%Y-%m-%dT%H:%M:%S")
            return dt
        except ValueError:
            msg = f"'{ds}' cannot be parsed as datetime - must be of form YYYY-MM-DDThh:mm:ss"
            raise error(msg)
    else:
        try:
            dt = datetime.strptime(ds, "%Y-%m-%d")
            return dt
        except ValueError:
            msg = f"'{ds}' cannot be parsed as datetime - must be of form YYYY-MM-DD"
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


def convert_datetime_to_unix(dt: datetime, ms: bool=True) -> int:

    dt = dt.astimezone(timezone.utc)
    dt = int(dt.timestamp())

    if ms:
        dt = dt * 1000

    return dt
