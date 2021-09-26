import re
from datetime import datetime
from datetime import timezone

import pytest

from medium_stats.utils import check_dependencies_missing
from medium_stats.utils import convert_datetime_to_unix
from medium_stats.utils import dt_formatter
from medium_stats.utils import make_utc_explicit
from medium_stats.utils import valid_date


class TestCheckDependenciesMissing:
    def test_none_missing_returns_empty_list(self):
        assert check_dependencies_missing(extras=("pytest",)) == []

    def test_missing_returns_list_of_missing(self):
        fake_package = "asldfkjblkasjdlk"
        assert check_dependencies_missing(extras=(fake_package,)) == [fake_package]


class TestValidDate:
    @pytest.mark.parametrize(
        "ds,dt",
        [
            ("2020-01-01T00:00:01", datetime(2020, 1, 1, 0, 0, 1)),
            ("2020-01-01", datetime(2020, 1, 1, 0, 0, 0)),
        ],
    )
    def test_valid_datestring(self, ds, dt):
        assert valid_date(ds) == dt

    @pytest.mark.parametrize(
        "invalid_ds,exc,help_txt",
        [
            ("greater_than_10_chars", ValueError, "must be of form YYYY-MM-DDThh:mm:ss"),
            ("lt_10", ValueError, "must be of form YYYY-MM-DD"),
        ],
    )
    def test_invalid_raises_error(self, invalid_ds, exc, help_txt):
        with pytest.raises(exc) as e:
            valid_date(invalid_ds, exc)
            assert help_txt in e.exception.args[0]


class TestDtFormatter:
    def test_when_output_type_json(self):
        dt = datetime(year=2020, month=1, day=1)
        date_string = dt_formatter(dt, "json")

        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", date_string)

    def test_when_output_type_filename(self):
        dt = datetime(year=2020, month=1, day=1)
        date_string = dt_formatter(dt, "filename")

        assert re.match(r"\d{8}T\d{6}", date_string)

    def test_raises_value_error_when_not_a_correct_output_type(self):
        with pytest.raises(ValueError) as e:
            dt_formatter(datetime(2020, 1, 1), "foo")


class TestMakeUtcExplicit:
    def test_when_utc_naive_is_true(self):
        dt = datetime(2020, 1, 1)
        actual = make_utc_explicit(dt, utc_naive=True)

        assert actual.tzinfo == timezone.utc

    def test_when_utc_naive_is_false(self):
        dt = datetime(2020, 1, 1)
        actual = make_utc_explicit(dt, utc_naive=False)

        assert actual.tzinfo == timezone.utc


class TestConvertDatetimeToUnix:
    def test_when_ms_is_true(self):

        dt = datetime.fromtimestamp(1, tz=timezone.utc)
        assert convert_datetime_to_unix(dt, ms=True) == 1000

    def test_when_ms_is_false(self):
        dt = datetime.fromtimestamp(1, tz=timezone.utc)
        assert convert_datetime_to_unix(dt, ms=False) == 1
