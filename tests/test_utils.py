import unittest
from medium_stats.utils import convert_datetime_to_unix, valid_date, dt_formatter
from medium_stats.utils import make_utc_explicit
from datetime import datetime, timezone, timedelta

class TestConvertDatetimeToUnix(unittest.TestCase):

    def setUp(self):

        self.now = datetime.now(timezone.utc)
        self.now_unix = self.now.timestamp()

    def test_convert_datetime_to_unix_returns_int(self):
        
        ms_false = convert_datetime_to_unix(self.now, ms=False)
        ms_true = convert_datetime_to_unix(self.now, ms=True)
        self.assertIsInstance(ms_false, int)
        self.assertIsInstance(ms_true, int)

    def test_convert_datetime_to_unix_returns_ms_as_default(self):
        
        ms_true = convert_datetime_to_unix(self.now)
        self.assertEqual(ms_true, int(self.now_unix) * 1000)

    def test_convert_datetime_to_unix_returns_ms_if_set(self):
        
        ms_true = convert_datetime_to_unix(self.now, ms=True)
        self.assertEqual(ms_true, int(self.now_unix) * 1000)

    def test_convert_datetime_to_unix_returns_seconds_if_ms_false(self):
        
        ms_true = convert_datetime_to_unix(self.now, ms=False)
        self.assertEqual(ms_true, int(self.now_unix))

class TestValidDate(unittest.TestCase):
    
    def setUp(self):
        
        self.valid_d = '2020-01-01' 
        self.valid_dt = '2020-01-01T12:30:00'
        self.error_arg = TypeError # this is arbitrary for testing purposes

    def test_accepts_both_date_and_datetime_strings(self):
        
        expected_d = datetime(year=2020, month=1, day=1)
        expected_dt = expected_d.replace(hour=12, minute=30)
        self.assertEqual(valid_date(self.valid_d, self.error_arg), expected_d)
        self.assertEqual(valid_date(self.valid_dt, self.error_arg), expected_dt)

    def test_error_type_arg_raised_if_value_error_exception(self):
        
        wrong_dt = '2020-01-01T12:99:00'
        wrong_d = '2020-15-01'

        for c in [wrong_dt, wrong_d]:
            with self.assertRaises(self.error_arg) as e:
                _ = valid_date(c, self.error_arg)
            self.assertIsInstance(e.exception, self.error_arg)
        
    def test_error_message_shows_date_format_if_lte_10_char(self):
        
        d1 = '2020-15-01'
        d2 = '20200101'
        d3 = '01/01/2020'
        d4 = 'atTenChars'
        d5 = 'wrong'

        cases = [d1, d2, d3, d4, d5]
        for c in cases:
            with self.assertRaises(self.error_arg) as e:
                _ = valid_date(c, self.error_arg)
            msg = e.exception.args[0]
            self.assertIn('must be of form YYYY-MM-DD', msg)

    def test_error_message_shows_date_format_if_gt_10_char(self):
        
        dt1 = '2020-01-01T120005'
        dt2 = '20200101T999999'
        dt3 = '2020-01-01T12:99:00'
        dt4 = 'elevenchars'

        cases = [dt1, dt2, dt3, dt4]
        for c in cases:
            with self.assertRaises(self.error_arg) as e:
                _ = valid_date(c, self.error_arg)
            msg = e.exception.args[0]
            self.assertIn('must be of form YYYY-MM-DDThh:mm:ss', msg)

class TestDtFormatter(unittest.TestCase):
    
    def setUp(self):
        self.dt = datetime(year=2020, month=2, day=14)

    def test_filename_output_of_form_YYYYMMDDTHHMMSS(self):
        
        actual = dt_formatter(self.dt, "filename")
        self.assertRegex(actual, r'\d{8}T\d{6}')
    
    def test_returns_string(self):

        self.assertIsInstance(dt_formatter(self.dt, "json"), str)

    def test_input_not_datetime_raises_attribute_error(self):

        invalid = [123, 'foobar', True]

        for i in invalid:
            with self.assertRaises(AttributeError):
                _ = dt_formatter(i, 'filename')

    def test_value_error_raised_if_output_not_json_or_filename(self):

        valid = ['json', 'filename']
        invalid = ['foobar', 'invalid', 123, True]

        for i in valid:
            self.assertIsNotNone(dt_formatter(self.dt, i))
        
        for i in invalid:
            with self.assertRaises(ValueError):
                _ = dt_formatter(self.dt, i)

class TestMakeUtcExplicit(unittest.TestCase):
    
    def setUp(self):
        
        self.naive_local = datetime(year=2020, month=1, day=15)
        local_tz = timezone(timedelta(hours=5))
        self.aware_local = self.naive_local.replace(tzinfo=local_tz)
        self.naive_utc = datetime.utcnow()
        self.aware_utc = datetime.now(timezone.utc)

    def test_returns_tz_aware_datetime(self):
        
        inputs = [self.naive_local, self.aware_local, self.naive_utc, self.aware_utc]

        returned1 = [make_utc_explicit(i, True) for i in inputs]
        returned2 = [make_utc_explicit(i, False) for i in inputs]
        returned = returned1 + returned2

        for i in returned:
            self.assertIsInstance(i, datetime)
            self.assertIsNotNone(i.tzinfo)

    def test_converts_local_naive_tz_into_utc_aware(self):
        
        actual = make_utc_explicit(self.naive_local, utc_naive=False)
        self.assertEqual(actual.tzinfo, timezone.utc)

    def test_offsets_local_tz_naive_to_utc(self):
        # TODO - need to create a mock for this
        pass

    def test_offsets_local_tz_aware_to_utc(self):
        
        local_tz = timezone(timedelta(hours=5))
        aware_local = self.naive_local.replace(tzinfo=local_tz)
        
        expected = aware_local - timedelta(hours=5)
        expected = expected.replace(tzinfo=timezone.utc)
        
        actual = make_utc_explicit(aware_local, utc_naive=False)

        self.assertEqual(actual, expected)

    def test_input_not_offset_when_utc_naive_true(self):

        actual = make_utc_explicit(self.naive_utc, utc_naive=True)
        expected = self.naive_utc.replace(tzinfo=timezone.utc)
        self.assertEqual(actual, expected)
    
    def test_utc_aware_input_returns_unchanged_regardless_of_utc_naive_param(self):

        actual1 = make_utc_explicit(self.aware_utc, utc_naive=True)
        actual2 = make_utc_explicit(self.aware_utc, utc_naive=False)

        self.assertEqual(actual1, self.aware_utc)
        self.assertEqual(actual2, self.aware_utc)

class TestCheckDependenciesMissing(unittest.TestCase):
    pass
    #TODO create mocks

if __name__ == "__main__":
    unittest.main()