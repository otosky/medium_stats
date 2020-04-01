import unittest
from medium_stats.cli import get_argparser, parse_scraper_args
from medium_stats.cli import valid_date, MODE_CHOICES
import os, sys
import argparse
from datetime import datetime, timedelta
from contextlib import contextmanager
from io import StringIO

@contextmanager
def capture_sys_output():
    capture_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = capture_out, capture_err
        yield capture_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err

class TestScraperCLIArguments(unittest.TestCase):
    
    def setUp(self):
        self.parser = get_argparser()
        self.default_creds = os.path.join(os.path.expanduser('~'), '.medium_creds.ini')
    
    def test_sid_and_uid_required_together_if_input(self):
        
        invalid_sid = 'scrape --sid foo -u test_user'.split()
        invalid_uid = 'scrape --uid bar -u test_user'.split()
        
        invalids = [invalid_sid, invalid_uid]
        invalids = [self.parser.parse_args(i) for i in invalids]
        
        for i in invalids:
            with self.assertRaises(SystemExit) as e:
                with capture_sys_output() as (out, err): 
                    _ = parse_scraper_args(i, self.parser)
            msg = err.getvalue()
            self.assertIn('both "sid" and "uid" arguments', msg)
        
    def test_creds_path_and_cookies_mutually_exclusive(self):

        invalid = 'scrape --sid foo --uid bar --creds path/to/file -u test_user'.split()

        args = self.parser.parse_args(invalid)

        with self.assertRaises(SystemExit) as e:
            with capture_sys_output() as (out, err): 
                    _ = parse_scraper_args(args, self.parser)
        msg = err.getvalue()
        self.assertRegex(msg, r'Set creds via "creds".+ Not both.$')

    def test_period_set(self):

        invalid_cred_explicit = 'scrape --creds path/to -u test_user'.split()
        invalid_cred_implicit = 'scrape -u test_user'.split()

        invalids = [invalid_cred_explicit, invalid_cred_implicit]
        invalids = [self.parser.parse_args(i) for i in invalids]
        
        for i in invalids:
            with self.assertRaises(SystemExit) as e:
                with capture_sys_output() as (out, err): 
                        _ = parse_scraper_args(i, self.parser)
            msg = err.getvalue()
            self.assertIn('Period must be set', msg)

    def test_all_and_period_flags_mutually_exclusive(self):

        invalid1 = 'scrape -u test_user --all --start 2020-01-01'.split()
        invalid2 = 'scrape -u test_user --all --end 2020-01-01'.split()
        invalid3 = 'scrape -u test_user --all --start 2020-01-01 --end 2020-02-01'.split()

        invalids = [invalid1, invalid2, invalid3]
        invalids = [self.parser.parse_args(i) for i in invalids]

        for i in invalids:
            with self.assertRaises(SystemExit) as e:
                with capture_sys_output() as (out, err): 
                        _ = parse_scraper_args(i, self.parser)
            msg = err.getvalue()
            self.assertIn('Can\'t use "--all" flag with', msg)

    def test_period_end_defaults_to_most_recent_full_day_utc(self):
        
        input_ = 'scrape -u test_user --start 2020-01-01'.split()

        now = datetime.utcnow()
        now = datetime(*now.timetuple()[:3])
        args = self.parser.parse_args(input_)
        args = parse_scraper_args(args, self.parser)

        self.assertEqual(args.end, now)

    def test_period_start_defaults_beginning_day_prior_to_end(self):
        
        input_d = 'scrape -u test_user --end 2020-02-01'.split()
        input_dt = 'scrape -u test_user --end 2020-02-01T12:00:00'.split()

        start = datetime.strptime('2020-01-31', '%Y-%m-%d')
        for i in [input_d, input_dt]:
            args = self.parser.parse_args(i)
            args = parse_scraper_args(args, self.parser)
            self.assertEqual(args.start, start)
    
    def test_valid_date_func_returns_datetime(self):
        
        dt_ = '2020-01-01T12:00:05'
        dt_correct = datetime.strptime(dt_, '%Y-%m-%dT%H:%M:%S')
        d_ = '2020-01-01'
        d_correct = datetime.strptime(d_, '%Y-%m-%d')

        self.assertEqual(valid_date(dt_), dt_correct)
        self.assertEqual(valid_date(d_), d_correct)

    def test_valid_date_func_returns_argument_error_type(self):

        wrong_dt = '2020-01-01T12:99:00'
        wrong_d = '2020-15-01'

        for c in [wrong_dt, wrong_d]:
            with self.assertRaises(argparse.ArgumentTypeError) as e:
                _ = valid_date(c)
            self.assertIsInstance(e.exception, argparse.ArgumentTypeError)

    def test_valid_date_func_raises_datetime_format_msg(self):

        dt1 = '2020-01-01T120005'
        dt2 = '20200101T999999'
        dt3 = '2020-01-01T12:99:00'
        dt4 = 'elevenchars'

        cases = [dt1, dt2, dt3, dt4]
        for c in cases:
            with self.assertRaises(argparse.ArgumentTypeError) as e:
                _ = valid_date(c)
            msg = e.exception.args[0]
            self.assertIn('not a valid datetime - must be of form YYYY-MM-DDThh:mm:ss', msg)
            
    def test_valid_date_func_returns_date_format_msg(self): 

        d1 = '2020-15-01'
        d2 = '20200101'
        d3 = '01/01/2020'
        d4 = 'atTenChars'
        d5 = 'wrong'

        cases = [d1, d2, d3, d4, d5]
        for c in cases:
            with self.assertRaises(argparse.ArgumentTypeError) as e:
                _ = valid_date(c)
            msg = e.exception.args[0]
            self.assertIn('not a valid date - must be of form YYYY-MM-DD', msg)

    def test_period_start_accepts_date_string_format(self):
        
        start = '2020-01-01'
        start_dt = datetime.strptime(start, '%Y-%m-%d')

        input_ = f'scrape -u test_user --start {start}'.split()
    
        args = self.parser.parse_args(input_)
        self.assertEqual(args.start, start_dt)

    def test_period_start_accepts_datetime_string_format(self):
        
        start = '2020-01-01T12:00:59'
        start_dt = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')

        input_ = f'scrape -u test_user --start {start}'.split()
        
        args = self.parser.parse_args(input_)
        self.assertEqual(args.start, start_dt)

    def test_period_end_accepts_date_string_format(self):
        
        end = '2020-01-01'
        end_dt = datetime.strptime(end, '%Y-%m-%d')

        input_ = f'scrape -u test_user --end {end}'.split()
    
        args = self.parser.parse_args(input_)
        self.assertEqual(args.end, end_dt)

    def test_period_end_accepts_datetime_string_format(self):
        
        end = '2020-01-01T12:00:59'
        end_dt = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')

        input_ = f'scrape -u test_user --end {end}'.split()
        
        args = self.parser.parse_args(input_)
        self.assertEqual(args.end, end_dt)

    def test_period_flags_obey_correct_time_order(self):
    
        start = '2020-01-02'
        start_dt = '2020-01-02T00:00:00'
        end = '2020-01-01'
        end_dt = '2020-01-01T00:00:00'

        input1 = f'scrape -u test_user --start {start} --end {end}'.split()
        input2 = f'scrape -u test_user --start {start_dt} --end {end_dt}'.split()

        args_list = [self.parser.parse_args(i) for i in [input1, input2]]
        for a in args_list:
            with self.assertRaises(SystemExit) as e:
                with capture_sys_output() as (out, err): 
                        _ = parse_scraper_args(a, self.parser)
            msg = err.getvalue()
            self.assertIn('"--end" cannot be prior to "--start"', msg)

    def test_output_dir_default(self):
        
        input_ = 'scrape -u test_user --all'.split()
        parsed = self.parser.parse_args(input_)
        parsed = parse_scraper_args(parsed, self.parser)
        
        self.assertEqual(parsed.output_dir, os.getcwd())
    
    # def test_output_dir_exists(self):
    #     pass

    def test_creds_default_location_beneath_home(self):
        
        input_ = 'scrape -u test_user --all'.split()
        parsed = self.parser.parse_args(input_)
        parsed = parse_scraper_args(parsed, self.parser)
        
        self.assertEqual(parsed.creds, self.default_creds)

    def test_mode_flag_returns_list(self):

        input1 = 'scrape -u test_user --all --mode events'.split()
        input2 = 'scrape -u test_user --all --mode events referrers'.split() 
        input3 = 'scrape -u test_user --start 2020-01-01 --end 2020-02-01'.split()

        parsed = [self.parser.parse_args(i) for i in [input1, input2, input3]]
        parsed = [parse_scraper_args(p, self.parser) for p in parsed]

        for p in parsed:
            self.assertIsInstance(p.mode, list)

    def test_implicit_mode_defaults_to_all_choices(self):
        
        input1 = 'scrape -u test_user --all'.split()
        input2 = 'scrape -u test_user --start 2020-01-01 --end 2020-02-01'.split()

        parsed = [self.parser.parse_args(i) for i in [input1, input2]]
        parsed = [parse_scraper_args(p, self.parser) for p in parsed]
        
        for p in parsed:
            self.assertEqual(p.mode, MODE_CHOICES)
        
class TestCookieFetcherCLIArguments(unittest.TestCase):
    
    def setUp(self):
        self.parser = get_argparser()
        self.default_creds = os.path.join(os.path.expanduser('~'), '.medium_creds.ini')

    def test_required_email_missing_triggers_arg_error(self):
        
        input_ = 'fetch_cookies --pwd foobar'.split()

        with self.assertRaises(SystemExit) as e:
            with capture_sys_output() as (out, err): 
                _ = self.parser.parse_args(input_)
            self.assertRaises(e.exception.__context__, argparse.ArgumentError)
            # TODO add message test akin to "the following arguments are required..."


    def test_password_or_env_flag_missing_triggers_arg_error(self):
        
        input_ = 'fetch_cookies --email foo@bar.com'.split()

        with self.assertRaises(SystemExit) as e:
            with capture_sys_output() as (out, err): 
                _ = self.parser.parse_args(input_)
            self.assertRaises(e.exception.__context__, argparse.ArgumentError)

    def test_unspecified_creds_path_defaults_under_home_dir(self):
        
        input_ = 'fetch_cookies --email foo@bar.com --pwd foobar'.split()

        parsed = self.parser.parse_args(input_)
        self.assertEqual(parsed.creds, self.default_creds)

    def test_pwd_or_env_flag_mutually_exclusive(self):

        input_ = 'fetch_cookies --email foo@bar.com --pwd foobar --pwd-in-env'.split()

        with self.assertRaises(SystemExit) as e:
            with capture_sys_output() as (out, err): 
                _ = self.parser.parse_args(input_)
            self.assertRaises(e.exception.__context__, argparse.ArgumentError)


if __name__ == '__main__':
    unittest.main()