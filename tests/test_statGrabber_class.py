import unittest
from medium_stats.scraper import StatGrabber
from datetime import datetime

class TestStatGrabberHelpers(unittest.TestCase):

    def setUp(self):

        self.now = datetime.utcnow()
        self.now_unix = self.now.timestamp()

    def test_ensure_date_string_accepts_correct_type(self):
        
        self.assertTrue(StatGrabber._ensure_date_string('2020-01-01'))
        valid_dt = datetime(year=2020, month=1, day=1)
        self.assertTrue(StatGrabber._ensure_date_string(valid_dt))
        self.assertRaises(ValueError, StatGrabber._ensure_date_string,
                              '2020-31-01')
        self.assertRaises(ValueError, StatGrabber._ensure_date_string,
                              '20200101')
        self.assertRaises(TypeError, StatGrabber._ensure_date_string, 1)
    
    def test_ensure_date_string_returns_dt(self):

        from_str = StatGrabber._ensure_date_string('2020-01-01')
        from_dt = StatGrabber._ensure_date_string(datetime(year=2020, month=1, day=1))

        self.assertIsInstance(from_str, datetime)
        self.assertIsInstance(from_dt, datetime)

    def test_convert_datetime_to_unix_returns_int(self):
        
        ms_false = StatGrabber._convert_datetime_to_unix(self.now, ms=False)
        ms_true = StatGrabber._convert_datetime_to_unix(self.now, ms=True)
        self.assertIsInstance(ms_false, int)
        self.assertIsInstance(ms_true, int)

    def test_convert_datetime_to_unix_returns_ms_as_default(self):
        
        ms_true = StatGrabber._convert_datetime_to_unix(self.now)
        self.assertEqual(ms_true, int(self.now_unix) * 1000)

    def test_convert_datetime_to_unix_returns_ms_if_set(self):
        
        ms_true = StatGrabber._convert_datetime_to_unix(self.now, ms=True)
        self.assertEqual(ms_true, int(self.now_unix) * 1000)

    def test_convert_datetime_to_unix_returns_seconds_if_ms_false(self):
        
        ms_true = StatGrabber._convert_datetime_to_unix(self.now, ms=False)
        self.assertEqual(ms_true, int(self.now_unix))

# class TestStatGrabber(unittest.TestCase):

#     def setUp(self):

#         pass

    # def test_init_converts_periods_to_unix_timestamp(self):
    
    # def test_totals_endpoint_contains_unix_timestamps(self):
    
    # TODO add mock objects for testing API calls

    # def test_fetch_raises_http_error_when_response_not_200(self):

    # def test_events_true_param_triggers_call_to_totals_endpoint(self):
    
    # def test_events_false_param_triggers_call_to_stats_url(self):

    # def test_fetch_response_contains_replacement_text(self):

    # def test_fetch_response_loads_as_json_after_replacement_text_removed(self):
    
    # def test_get_summary_stats_returns_dict(self):

    # def test_get_summary_stats_dict_contains_keys(self):

    # def test_get_summary_stats_resets_start_period_when_set_before_user_creation(self):

    # def test_reset_start_period_is_same_type_as_init(self):

    # def test_reset_start_unix_is_same_type_as_init(self):
    
    # def test_get_article_ids_sets_attribute(self):

    # def test_get_article_ids_returns_flat_list(self)

    # def test_get_article_ids_returns_correct_ids_from_json(self)

    # TODO: outline test cases for article_grabber

if __name__ == '__main__':
    unittest.main()