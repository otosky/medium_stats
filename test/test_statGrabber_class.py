import unittest
from medium_stats.scraper import StatGrabberBase, StatGrabberUser, StatGrabberPublication
from datetime import datetime
import requests

class TestStatGrabberBase(unittest.TestCase):

    def setUp(self):

        self.valid_start = datetime(year=2020, month=1, day=11, hour=12, minute=15)
        self.valid_stop = datetime(year=2020, month=2, day=11, hour=20, minute=15)

    # def test_init_start_stop_param_must_be_datetime(self):

    # def test_init_start_stop_converted_to_tz_aware_from_naive(self):

    # def test_init_start_stop_times_unchanged_if_already_utc_is_true(self):

    # def test_init_converts_periods_to_unix_timestamp(self):

    def test_init_cookies_attr_contains_sid_and_uid_keys(self):
        
        sg = StatGrabberBase('sid', 'uid', self.valid_start, self.valid_stop)
        self.assertIn('sid', sg.cookies.keys())
        self.assertIn('uid', sg.cookies.keys())

    def test_init_cookies_attr_contains_sid_and_uid_values(self):
        
        sg = StatGrabberBase('foo', 'bar', self.valid_start, self.valid_stop)
        self.assertEqual(sg.cookies.get('sid'), 'foo')
        self.assertEqual(sg.cookies.get('uid'), 'bar')

    # def test_init_now_param_requires_tz_aware_datetime_arg(self):

    def test_init_session_attr_is_request_Sessions_object(self):

        sg = StatGrabberBase('sid', 'uid', self.valid_start, self.valid_stop)
        self.assertIsInstance(sg.session, requests.Session)
    
    def test_init_session_attr_has_headers_content_type_and_accept(self):
        
        sg = StatGrabberBase('sid', 'uid', self.valid_start, self.valid_stop)
        
        self.assertIn('content-type', sg.session.headers.keys())
        self.assertIn('accept', sg.session.headers.keys())
    
    def test_init_session_attr_has_headers_content_type_and_accept_values_json(self):
        
        sg = StatGrabberBase('sid', 'uid', self.valid_start, self.valid_stop)
        
        expected = 'application/json'
        self.assertIn(expected, sg.session.headers['content-type'])
        self.assertIn(expected, sg.session.headers['accept'])

    def test_init_session_attr_has_cookies_sid_and_uid(self):

        sg = StatGrabberBase('foo', 'bar', self.valid_start, self.valid_stop)
        
        self.assertEqual('foo', sg.session.cookies.get('sid'))
        self.assertEqual('bar', sg.session.cookies.get('uid'))

    
    
    # TODO add mock objects for testing API calls

    # def test_fetch_raises_http_error_when_response_not_200(self):

    # def test_decode_json_raises_type_error_if_param_is_not_response(self):

    # def test_decode_json_returns_valid_json_dict(self):

        # TODO - mock input has to be a response object with "while" text and json with "payload" as a key

    # def test_get_article_ids_returns_list(self):

    def test_get_article_ids_stashes_articles_list_to_attr(self):
    
        sg = StatGrabberBase('foo', 'bar', self.valid_start, self.valid_stop)
        json_input = [
            {
                "postId": "a1",
                "slug": "test-story"
            },
            {
                "postId": "a2",
                "slug": "another-test"
            },
            {
                "postId": "a3",
                "slug": "last-one"
            }
        ]
        articles = sg.get_article_ids(json_input)
        expected = ["a1", "a2", "a3"]

        self.assertEqual(articles, expected)

    def test_get_story_stats_raises_value_error_if_type_param_not_valid(self):
        
        sg = StatGrabberBase('foo', 'bar', self.valid_start, self.valid_stop)
        
        with self.assertRaises(ValueError):
            sg.get_story_stats("foobar", 'invalid')
            sg.get_story_stats("foobar", 123)
            sg.get_story_stats("foobar", True)
            sg.get_story_stats("foobar", 'views_read')

    # def test_get_story_stats_returns_json_dict(self):

    # def test_get_story_stats_makes_post_request(self):


class TestStatGrabberUser(unittest.TestCase):

    def test_class_inherits_from_StatGrabberBase(self):
        
        subclassed = issubclass(StatGrabberUser, (StatGrabberBase))
        self.assertTrue(subclassed)
    # def test_events_true_param_triggers_call_to_totals_endpoint(self):
    
    # def test_events_false_param_triggers_call_to_stats_url(self):

    # def test_totals_endpoint_contains_unix_timestamps(self):

    # def test_get_summary_stats_returns_dict(self):

    # def test_get_summary_stats_dict_contains_keys(self):

    # def test_get_summary_stats_resets_start_period_when_set_before_user_creation(self):

    # def test_reset_start_period_is_same_type_as_init(self):

    # def test_reset_start_unix_is_same_type_as_init(self):
    
    # def test_get_article_ids_sets_attribute(self):

    # def test_get_article_ids_returns_flat_list(self)

    # def test_get_article_ids_returns_correct_ids_from_json(self)

    # TODO: outline test cases for article_grabber

class TestStatGrabberPublication(unittest.TestCase):

    def test_class_inherits_from_StatGrabberBase(self):
        
        subclassed = issubclass(StatGrabberPublication, (StatGrabberBase))
        self.assertTrue(subclassed)

if __name__ == '__main__':
    unittest.main()