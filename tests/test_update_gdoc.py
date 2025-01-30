from io import StringIO
from pathlib import Path
import unittest
from unittest import mock
from unittest.mock import MagicMock

import platformdirs
import yaml

from logilica_weekly_report.update_gdoc import (
    APPLICATION_NAME,
    DEFAULT_APP_CREDENTIALS_FILE_NAME,
    DEFAULT_TOKEN_FILE_NAME,
    get_app_credentials_file,
    get_google_credentials,
    get_token_file,
)

CUT = "logilica_weekly_report.update_gdoc."

DEFAULT_CONFIGS = (
    """---
config:
""",
    """---
config:
  google:
""",
    """---
config:
  google:
    "useless key": "useless value"
""",
)


class TestUpdateGDoc(unittest.TestCase):
    def test_get_token_file_default_results(self):
        expected_dir = platformdirs.user_cache_path(APPLICATION_NAME)
        expected = expected_dir / DEFAULT_TOKEN_FILE_NAME

        for entry in DEFAULT_CONFIGS:
            config = yaml.safe_load(StringIO(entry))
            result = get_token_file(config)
            self.assertEqual(expected, result)

    def test_get_token_file_partial_dir(self):
        for entry in ("subdir/", "subdir1/subdir2/"):
            config = {"google": {"token_file": entry}}
            result = get_token_file(config)
            expected_dir = platformdirs.user_cache_path(entry[:-1])
            expected = expected_dir / DEFAULT_TOKEN_FILE_NAME
            self.assertEqual(expected, result)

    def test_get_token_file_full_dir(self):
        for entry in ("./", "./subdir/", "/opt/config/"):
            config = {"google": {"token_file": entry}}
            result = get_token_file(config)
            expected = Path(entry) / DEFAULT_TOKEN_FILE_NAME
            self.assertEqual(expected, result)

    def test_get_token_file_with_no_dir(self):
        expected_dir = platformdirs.user_cache_path(APPLICATION_NAME)
        for entry in ("my_token.json",):
            config = {"google": {"token_file": entry}}
            expected = expected_dir / entry
            result = get_token_file(config)
            self.assertEqual(expected, result)

    def test_get_token_file_no_dir(self):
        for entry, expected_dir in (
            ("./my_token.json", Path(".")),
            ("partial_dir/my_token.json", platformdirs.user_cache_path("")),
            ("/opt/subdir/my_token.json", Path("")),
        ):
            config = {"google": {"token_file": entry}}
            expected = expected_dir / entry
            result = get_token_file(config)
            self.assertEqual(expected, result)

    def test_get_app_credentials_file_default_results(self):
        expected_dir = platformdirs.user_config_path(APPLICATION_NAME)
        expected = expected_dir / DEFAULT_APP_CREDENTIALS_FILE_NAME

        for entry in DEFAULT_CONFIGS:
            config = yaml.safe_load(StringIO(entry))
            result = get_app_credentials_file(config)
            self.assertEqual(expected, result)

    def test_get_app_credentials_file_partial_dir(self):
        for entry in ("subdir/", "subdir1/subdir2/"):
            config = {"google": {"app_credentials_file": entry}}
            result = get_app_credentials_file(config)
            expected_dir = platformdirs.user_config_path(entry[:-1])
            expected = expected_dir / DEFAULT_APP_CREDENTIALS_FILE_NAME
            self.assertEqual(expected, result)

    def test_get_app_credentials_file_full_dir(self):
        for entry in ("./", "./subdir/", "/opt/config/"):
            config = {"google": {"app_credentials_file": entry}}
            result = get_app_credentials_file(config)
            expected = Path(entry) / DEFAULT_APP_CREDENTIALS_FILE_NAME
            self.assertEqual(expected, result)

    def test_get_app_credentials_file_with_no_dir(self):
        expected_dir = platformdirs.user_config_path(APPLICATION_NAME)
        for entry in ("my_token.json",):
            config = {"google": {"app_credentials_file": entry}}
            expected = expected_dir / entry
            result = get_app_credentials_file(config)
            self.assertEqual(expected, result)

    def test_app_credentials_file_no_dir(self):
        for entry, expected_dir in (
            ("./my_app_credentials.json", Path(".")),
            ("partial_dir/my_app_credentials.json", platformdirs.user_config_path("")),
            ("/opt/subdir/my_app_credentials.json", Path("")),
        ):
            config = {"google": {"app_credentials_file": entry}}
            expected = expected_dir / entry
            result = get_app_credentials_file(config)
            self.assertEqual(expected, result)

    @mock.patch(CUT + "open", new_callable=unittest.mock.mock_open)
    @mock.patch(CUT + "InstalledAppFlow")
    @mock.patch(CUT + "Credentials")
    @mock.patch(CUT + "get_app_credentials_file")
    @mock.patch(CUT + "get_token_file")
    def test_get_google_credentials(
        self,
        mock_get_token_file,
        mock_get_app_credentials_file,
        mock_credentials,
        mock_installedappflow,
        mock_open,
    ):
        mock_token_file = MagicMock()
        mock_app_credentials_file = MagicMock()
        mock_cached_creds = MagicMock()
        mock_flow = MagicMock()
        mock_new_creds = MagicMock()

        mock_get_token_file.return_value = mock_token_file
        mock_get_app_credentials_file.return_value = mock_app_credentials_file
        mock_cached_creds.to_json.return_value = MagicMock()
        mock_credentials.from_authorized_user_file.return_value = mock_cached_creds
        mock_installedappflow.from_client_secrets_file.return_value = mock_flow
        mock_new_creds.to_json.return_value = MagicMock()
        mock_flow.run_local_server.return_value = mock_new_creds

        # Scenario 1:  token file exists; creds are good
        mock_token_file.exists.return_value = True
        creds = mock_cached_creds
        creds.valid = True
        result = get_google_credentials({})
        self.assertEqual(creds, result)
        mock_cached_creds.refresh.assert_not_called()
        mock_flow.run_local_server.assert_not_called()
        mock_open.assert_not_called()

        # Scenario 2:  token file exists; contains no creds
        mock_get_token_file.exists.return_value = True
        mock_credentials.from_authorized_user_file.return_value = None
        creds = mock_new_creds
        result = get_google_credentials({})
        self.assertEqual(creds, result)
        mock_cached_creds.refresh.assert_not_called()
        mock_open.assert_called_with(mock_token_file, "w")
        mock_open().write.assert_called_with(creds.to_json.return_value)
        # Reset for next scenario
        mock_credentials.from_authorized_user_file.return_value = mock_cached_creds
        mock_open().write.reset_mock()

        # Scenario 3:  have token, invalid, expired; have refresh
        mock_get_token_file.exists.return_value = True
        mock_cached_creds.valid = False
        mock_cached_creds.expired = True
        mock_cached_creds.refresh_token = True
        creds = mock_cached_creds
        result = get_google_credentials({})
        self.assertEqual(creds, result)
        mock_cached_creds.refresh.assert_called()
        mock_open.assert_called_with(mock_token_file, "w")
        mock_open().write.assert_called_with(creds.to_json.return_value)
        # Reset for next scenario
        mock_open().write.reset_mock()
        mock_cached_creds.reset_mock()

        # Scenario 4:  token file exists; creds not valid, not expired
        mock_get_token_file.exists.return_value = True
        mock_cached_creds.expired = False
        creds = mock_new_creds
        result = get_google_credentials({})
        self.assertEqual(creds, result)
        mock_cached_creds.refresh.assert_not_called()
        mock_open.assert_called_with(mock_token_file, "w")
        mock_open().write.assert_called_with(creds.to_json.return_value)
        # Reset for next scenario
        mock_open().write.reset_mock()

        # Scenario 5:  token file exists; creds not valid, expired, no refresh
        mock_get_token_file.exists.return_value = True
        mock_cached_creds.expired = True
        mock_cached_creds.refresh_token = False
        creds = mock_new_creds
        result = get_google_credentials({})
        self.assertEqual(creds, result)
        mock_cached_creds.refresh.assert_not_called()
        mock_open.assert_called_with(mock_token_file, "w")
        mock_open().write.assert_called_with(creds.to_json.return_value)
        # Reset for next scenario
        mock_open().write.reset_mock()

        # Scenario 6:  token file does not exist
        mock_get_token_file.exists.return_value = False
        creds = mock_new_creds
        result = get_google_credentials({})
        self.assertEqual(creds, result)
        mock_cached_creds.refresh.assert_not_called()
        mock_open.assert_called_with(mock_token_file, "w")
        mock_open().write.assert_called_with(creds.to_json.return_value)
        # Reset for next scenario
        mock_open().write.reset_mock()

    # TODO:
    #  - Refactor test_get_google_credentials() to remove code duplications
    #  - Consider adding testing for upload_doc(), add_teams(),
    #    generate_html(), and possibly update_gdoc().


if __name__ == "__main__":
    unittest.main()
