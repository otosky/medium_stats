import configparser
import shutil
import tempfile
import unittest
from io import BytesIO
from io import TextIOWrapper
from unittest.mock import patch

from medium_stats.cli import MediumConfigHelper


@patch("medium_stats.cli.configparser.open")
class TestValidateConfig(unittest.TestCase):
    def setUp(self):
        self.handle = "handle"
        cfg = f"[{self.handle}]\nsid = foo\nuid = bar"
        self.fake_config = TextIOWrapper(BytesIO(bytes(cfg, "utf-8")))
        self.fake_path = "~/medium_creds.ini"

    def test_incorrect_account_name_raises_value_error(self, mock_cfg_open):

        mock_cfg_open.return_value = self.fake_config

        with self.assertRaises(ValueError) as e:
            MediumConfigHelper._validate_config("irrelevant", "scooby_doo")

        msg = e.exception.args[0]
        self.assertIn("not found in section", msg)

    def test_missing_sid_triggers_value_error(self, mock_cfg_open):

        missing_sid = TextIOWrapper(BytesIO(b"[handle]\nuid = bar"))

        mock_cfg_open.return_value = missing_sid

        with self.assertRaises(ValueError) as e:
            MediumConfigHelper._validate_config("irrelevant", "handle")

        msg = e.exception.args[0]
        self.assertIn("not properly formed", msg)

    def test_missing_uid_triggers_value_error(self, mock_cfg_open):
        missing_sid = TextIOWrapper(BytesIO(b"[handle]\nsid = foo"))

        mock_cfg_open.return_value = missing_sid

        with self.assertRaises(ValueError) as e:
            MediumConfigHelper._validate_config("irrelevant", "handle")

        msg = e.exception.args[0]
        self.assertIn("not properly formed", msg)

    def test_returns_configparser_object(self, mock_cfg_open):

        mock_cfg_open.return_value = self.fake_config

        cfg = MediumConfigHelper._validate_config("irrelevant", "handle")
        self.assertIsInstance(cfg, configparser.ConfigParser)

    def test_excess_key_values_does_not_trigger_error(self, mock_cfg_open):

        data = "[handle]\nsid=foo\nuid=bar\nextra=helloworld\nextra2=qwerty"
        mock_cfg_open.return_value = TextIOWrapper(BytesIO(bytes(data, "utf-8")))

        cfg = MediumConfigHelper._validate_config("irrelevant", "handle")
        self.assertIsInstance(cfg, configparser.ConfigParser)


class TempCreds(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        data = "[handle]\nsid=foo\nuid=bar"
        self.creds_path = f"{self.test_dir}/tmp_creds.ini"
        with open(self.creds_path, "w") as f:
            f.write(data)

    def tearDown(self):
        shutil.rmtree(self.test_dir)


class TestRetrieveCookies(TempCreds):
    def test_raises_value_error_if_config_file_arg_does_not_exist(self):

        invalid_path = f"{self.test_dir}/does_not_exist.ini"
        with self.assertRaises(ValueError) as e:
            MediumConfigHelper._retrieve_cookies(invalid_path, "handle")

        msg = e.exception.args[0]
        self.assertIn("does not exist", msg)

    def test_returns_dict(self):

        res = MediumConfigHelper._retrieve_cookies(self.creds_path, "handle")
        self.assertIsInstance(res, dict)

    def test_returns_dict_of_keys_values_under_account_name_header(self):

        actual = MediumConfigHelper._retrieve_cookies(self.creds_path, "handle")
        expected = {"sid": "foo", "uid": "bar"}
        self.assertEqual(actual, expected)


class TestInit(TempCreds):
    def test_has_attr_handle(self):

        expected_attr = "handle"
        cfg = MediumConfigHelper(self.creds_path, "handle")
        self.assertEqual(cfg.handle, expected_attr)

    def test_has_attr_cookies(self):

        expected_attr = {"sid": "foo", "uid": "bar"}
        cfg = MediumConfigHelper(self.creds_path, "handle")
        self.assertEqual(cfg.cookies, expected_attr)

    def test_has_attr_sid(self):

        expected_attr = "foo"
        cfg = MediumConfigHelper(self.creds_path, "handle")
        self.assertEqual(cfg.sid, expected_attr)

    def test_has_attr_uid(self):

        expected_attr = "bar"
        cfg = MediumConfigHelper(self.creds_path, "handle")
        self.assertEqual(cfg.uid, expected_attr)


if __name__ == "__main__":
    unittest.main()
