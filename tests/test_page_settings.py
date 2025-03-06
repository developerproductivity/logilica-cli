from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest import raises
import yaml

from logilica_weekly_report.page_settings import SettingsPage

with open(Path(__file__).parent / "fixtures/config.yaml", "r") as yaml_file:
    FULL_CONFIG = yaml.safe_load(yaml_file)


GH_INTEGRATION_MEMBERSHIP = {
    "foobar-bot": {
        "connector": "GitHub",
        "membership_repositories": ["my_org/my-repo", "my_org/my-repo-2"],
    }
}

GH_INTEGRATION = {
    "foobar-bot": {
        "connector": "GitHub",
        "public_repositories": ["my_org/repo", "my_org/the-repo"],
    }
}

JIRA_INTEGRATION = {"foobar-bot": {"connector": "Jira", "membership_boards": ["TEST"]}}

MISSING_ENTITIES = {
    "foobar-bot": {
        "connector": "GitHub",
        "public_repositories": ["my_org/repo", "my_org/missing-repo"],
    },
    "boards": {
        "connector": "Jira",
        "membership_boards": ["Tmiss"],
    },
}


def has_entity_id_imported_side_effect(*args, **kwargs):
    if "miss" in kwargs.get("text", "") and kwargs.get("exact") is True:
        mock_for_missing_entry = MagicMock()
        # chain: .nth(0).is_visible() => False
        mock_for_missing_entry.nth.return_value.is_visible.return_value = False
        return mock_for_missing_entry
    else:
        mock_for_existing_entry = MagicMock()
        # chain: .nth(0).is_visible() => True
        mock_for_existing_entry.nth.return_value.is_visible.return_value = True
        return mock_for_existing_entry


def test_sync_repositories():
    for integrations in [GH_INTEGRATION_MEMBERSHIP, GH_INTEGRATION]:
        with patch("logilica_weekly_report.page_settings.expect") as mock_expect:
            page_mock = MagicMock()
            page_mock.get_by_text.side_effect = has_entity_id_imported_side_effect
            mock_expect.return_value = page_mock
            page = SettingsPage(page=page_mock)
            page.sync_integrations(integrations=integrations)
            page_mock.get_by_role.assert_any_call("heading", name="GitHub Settings")


def test_sync_boards():
    with patch("logilica_weekly_report.page_settings.expect") as mock_expect:
        page_mock = MagicMock()
        page_mock.get_by_text.side_effect = has_entity_id_imported_side_effect

        mock_locator = MagicMock()
        mock_locator.count.return_value = 1
        page_mock.get_by_role.return_value.filter.return_value.get_by_role.return_value = (
            mock_locator
        )

        mock_expect.return_value = page_mock
        page = SettingsPage(page=page_mock)
        page.sync_integrations(integrations=JIRA_INTEGRATION)
        print(mock_locator.mock_calls)
        page_mock.get_by_role.assert_any_call("heading", name="Jira Settings")


def test_missing_entities():
    with patch("logilica_weekly_report.page_settings.expect") as mock_expect:
        page_mock = MagicMock()
        page_mock.get_by_text.side_effect = has_entity_id_imported_side_effect

        mock_locator = MagicMock()
        mock_locator.count.return_value = 1
        page_mock.get_by_role.return_value.filter.return_value.get_by_role.return_value = (
            mock_locator
        )

        mock_expect.return_value = page_mock
        page = SettingsPage(page=page_mock)

        with raises(RuntimeError) as error:
            page.sync_integrations(integrations=MISSING_ENTITIES)

        assert (
            sum(len(value_list) for value_list in error.value.args[0].values()) == 2
        ), "There are two integrations with 2 failures that failed to sync"
