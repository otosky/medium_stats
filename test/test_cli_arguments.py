import argparse
import os
import sys
import unittest
from contextlib import contextmanager
from datetime import datetime
from datetime import timezone
from io import StringIO

from medium_stats.cli import PUB_MODE_CHOICES
from medium_stats.cli import USER_MODE_CHOICES
from medium_stats.cli import get_argparser
from medium_stats.cli import parse_scraper_args
from medium_stats.cli import valid_date


@contextmanager
def capture_sys_output():
    capture_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = capture_out, capture_err
        yield capture_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err


class TestScrapeUserCLIArguments(unittest.TestCase):
    def setUp(self):
        self.parser = get_argparser()
        self.default_creds = os.path.join(os.path.expanduser("~"), ".medium_creds.ini")

    def test_sid_and_uid_required_together_if_input(self):

        invalid_sid = "scrape_user --sid foo -u test_user".split()
        invalid_uid = "scrape_user --uid bar -u test_user".split()

        invalids = [invalid_sid, invalid_uid]
        invalids = [self.parser.parse_args(i) for i in invalids]

        for i in invalids:
            with self.assertRaises(SystemExit) as e:
                with capture_sys_output() as (out, err):
                    _ = parse_scraper_args(i, self.parser)
            msg = err.getvalue()
            self.assertIn('both "sid" and "uid" arguments', msg)

    # def test_period_set(self):
    #
    #     # TODO - this hits error because creds path needs to be mocked
    #     invalid_cred_explicit = "scrape_user --creds ~/.medium_creds.ini -u test_user --start 2020-01-01 --end 2020-01-02".split()
    #     invalid_cred_implicit = "scrape_user -u test_user --start 2020-01-01 --end 2020-01-02".split()
    #
    #     invalids = [invalid_cred_explicit, invalid_cred_implicit]
    #     invalids = [self.parser.parse_args(i) for i in invalids]
    #
    #     for i in invalids:
    #         with self.assertRaises(SystemExit) as e:
    #             with capture_sys_output() as (out, err):
    #                 _ = parse_scraper_args(i, self.parser)
    #         msg = err.getvalue()
    #         self.assertIn("Period must be set", msg)

    def test_period_start_accepts_date_string_format(self):

        start = "2020-01-01"
        start_dt = datetime.strptime(start, "%Y-%m-%d")

        input_ = f"scrape_user -u test_user --start {start}".split()

        args = self.parser.parse_args(input_)
        self.assertEqual(args.start, start_dt)

    def test_period_start_accepts_datetime_string_format(self):

        start = "2020-01-01T12:00:59"
        start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")

        input_ = f"scrape_user -u test_user --start {start}".split()

        args = self.parser.parse_args(input_)
        self.assertEqual(args.start, start_dt)

    def test_period_end_accepts_date_string_format(self):

        end = "2020-01-01"
        end_dt = datetime.strptime(end, "%Y-%m-%d")

        input_ = f"scrape_user -u test_user --end {end}".split()

        args = self.parser.parse_args(input_)
        self.assertEqual(args.end, end_dt)

    def test_period_end_accepts_datetime_string_format(self):

        end = "2020-01-01T12:00:59"
        end_dt = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")

        input_ = f"scrape_user -u test_user --end {end}".split()

        args = self.parser.parse_args(input_)
        self.assertEqual(args.end, end_dt)

    def test_period_flags_obey_correct_time_order(self):

        start = "2020-01-02"
        start_dt = "2020-01-02T00:00:00"
        end = "2020-01-01"
        end_dt = "2020-01-01T00:00:00"

        input1 = f"scrape_user -u test_user --start {start} --end {end}".split()
        input2 = f"scrape_user -u test_user --start {start_dt} --end {end_dt}".split()

        args_list = [self.parser.parse_args(i) for i in [input1, input2]]
        for a in args_list:
            with self.assertRaises(SystemExit) as e:
                with capture_sys_output() as (out, err):
                    _ = parse_scraper_args(a, self.parser)
            msg = err.getvalue()
            self.assertIn('"--end" cannot be prior to "--start"', msg)

    def test_output_dir_default(self):

        input_ = "scrape_user -u test_user --start 2020-01-01 --end 2020-01-02".split()
        parsed = self.parser.parse_args(input_)
        parsed = parse_scraper_args(parsed, self.parser)

        self.assertEqual(parsed.output_dir, os.getcwd())

    # def test_output_dir_exists(self):
    #     pass

    def test_creds_default_location_beneath_home(self):

        input_ = "scrape_user -u test_user --start 2020-01-01 --end 2020-01-02".split()
        parsed = self.parser.parse_args(input_)
        parsed = parse_scraper_args(parsed, self.parser)

        self.assertEqual(parsed.creds, self.default_creds)

    def test_mode_flag_returns_list(self):

        input3 = "scrape_user -u test_user --start 2020-01-01 --end 2020-02-01".split()

        parsed = [self.parser.parse_args(i) for i in [input3]]
        parsed = [parse_scraper_args(p, self.parser) for p in parsed]

        for p in parsed:
            self.assertIsInstance(p.mode, list)

    def test_implicit_mode_defaults_to_all_choices(self):

        in2 = "scrape_user -u test_user --start 2020-01-01 --end 2020-02-01".split()
        in4 = "scrape_publication -u test_pub --start 2020-01-01 --end 2020-02-01".split()

        parsed_user = [self.parser.parse_args(i) for i in [in2]]
        parsed_user = [parse_scraper_args(p, self.parser) for p in parsed_user]
        for p in parsed_user:
            self.assertEqual(p.mode, USER_MODE_CHOICES)

        parsed_pub = [self.parser.parse_args(i) for i in [in4]]
        parsed_pub = [parse_scraper_args(p, self.parser) for p in parsed_pub]
        for p in parsed_pub:
            self.assertEqual(p.mode, PUB_MODE_CHOICES)


class TestCookieFetcherCLIArguments(unittest.TestCase):
    def setUp(self):
        self.parser = get_argparser()
        self.default_creds = os.path.join(os.path.expanduser("~"), ".medium_creds.ini")

    def test_required_email_missing_triggers_arg_error(self):

        input_ = "fetch_cookies --pwd foobar".split()

        with self.assertRaises(SystemExit) as e:
            with capture_sys_output() as (out, err):
                _ = self.parser.parse_args(input_)
            self.assertRaises(e.exception.__context__, argparse.ArgumentError)
            # TODO add message test akin to "the following arguments are required..."

    def test_password_or_env_flag_missing_triggers_arg_error(self):

        input_ = "fetch_cookies --email foo@bar.com".split()

        with self.assertRaises(SystemExit) as e:
            with capture_sys_output() as (out, err):
                _ = self.parser.parse_args(input_)
            self.assertRaises(e.exception.__context__, argparse.ArgumentError)

    def test_unspecified_creds_path_defaults_under_home_dir(self):

        input_ = "fetch_cookies --email foo@bar.com --pwd foobar".split()

        parsed = self.parser.parse_args(input_)
        self.assertEqual(parsed.creds, self.default_creds)

    def test_pwd_or_env_flag_mutually_exclusive(self):

        input_ = "fetch_cookies --email foo@bar.com --pwd foobar --pwd-in-env".split()

        with self.assertRaises(SystemExit) as e:
            with capture_sys_output() as (out, err):
                _ = self.parser.parse_args(input_)
            self.assertRaises(e.exception.__context__, argparse.ArgumentError)


if __name__ == "__main__":
    unittest.main()
