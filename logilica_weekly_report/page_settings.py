from collections import defaultdict
from functools import partial
import logging
import re
from typing import Any, Callable, Generator, Optional, Tuple

try:
    from typing import TypeAlias  # Python 3.10+
except ImportError:
    from typing_extensions import TypeAlias  # Python 3.9

from playwright.sync_api import expect, Locator, Page

from logilica_weekly_report.page_navigation import NavigationPanel

IntegrationSyncFailures: TypeAlias = dict[Tuple[str, str], list[Tuple[str, str]]]


class SettingsPage:
    """Page Object to handle interactions with Logilica Settings.

    Provides interactions with Settings / Integrations.
    """

    IMPORT_TIMEOUT = 9000
    AVAILABLE_LIST_TIMEOUT = 54000

    def __init__(self, page: Page):

        self.page = page
        # UI elements for public access
        self.add_public_repository_dialog_button = page.get_by_role(
            "button", name="Add Public Repository"
        )
        self.add_public_repository_confirm_button = page.get_by_role(
            "button", name="Add Project"
        )
        self.add_public_repository_input = page.locator(
            "label:has-text('Repo URL') + input"
        )
        # UI elements for membership-based access
        self.search_imported_repos_field = page.locator(
            "input[placeholder='Search repository...']"
        ).nth(0)
        self.search_available_repos_field = page.locator(
            "input[placeholder='Search repository...']"
        ).nth(1)
        self.search_imported_boards_field = page.locator(
            "input[placeholder='Search board...']"
        ).nth(0)
        self.search_available_boards_field = page.locator(
            "input[placeholder='Search board...']"
        ).nth(1)

    def open_integration_configuration(
        self, *, integration: str, connector: str
    ) -> None:
        """Opens Integration Configuration.

        Opens Integration configuration. Assumes that Settings/Integrations is
        opened prior to that.
        """

        logging.debug(
            "Opening integration '%s', connector type:'%s'", integration, connector
        )
        self.page.locator("div.items-center").filter(has_text=connector).filter(
            has_text=integration
        ).get_by_role("button", name="Configure").click()
        expect(
            self.page.get_by_role("heading", name=f"{connector} Settings")
        ).to_be_visible()

    def sync_integrations(self, integrations: dict[str, Any]) -> None:
        """Synchronizes integration configuration from file to UI.

        Updates Logilica integration configuration for all connectors specified
        in integrations sections of the local configuration file.

        Raises:
          RuntimeError: If any repositories could not have been added to the configuration.
        """

        sync_failures: IntegrationSyncFailures = defaultdict(list)
        for integration_name, details in integrations.items():
            connector = details["connector"]
            public_repos = details.get("public_repositories", [])
            member_repos = details.get("membership_repositories", [])
            boards = details.get("membership_boards", [])
            logging.debug(
                "Syncing integration '%s' (connector '%s'), "
                "%d public repositories, %d membership-based repositories, "
                "%d membership-based boards.",
                integration_name,
                connector,
                len(public_repos),
                len(member_repos),
                len(boards),
            )

            # open configuration UI
            NavigationPanel(self.page).navigate(
                link_name="Integrations", menu_dropdown="Settings"
            )
            self.open_integration_configuration(
                integration=integration_name, connector=connector
            )
            # process public repositories
            self.process_repositories(
                connector=connector,
                integration_name=integration_name,
                repositories=public_repos,
                add_function=self.add_public_repository,
                failures=sync_failures,
            )
            # process membership-based repositories
            self.process_repositories(
                connector=connector,
                integration_name=integration_name,
                repositories=member_repos,
                add_function=partial(
                    self.add_membership_entity,
                    search_field=self.search_available_repos_field,
                ),
                failures=sync_failures,
            )
            # process membership based boards
            self.process_boards(
                connector=connector,
                integration_name=integration_name,
                boards=boards,
                add_function=partial(
                    self.add_membership_entity,
                    search_field=self.search_available_boards_field,
                ),
                failures=sync_failures,
            )

        if sync_failures:
            logging.error(
                "There are failures for %d integrations in syncing sources",
                len(sync_failures),
            )
            for (connector, name), failures in sync_failures.items():
                logging.error("Failures in connector %s named '%s':", connector, name)
                for repo, f in failures:
                    logging.error("%s: %s", repo, f)
            raise RuntimeError(sync_failures)

    # helpers

    def wait_for_available_entities(
        self,
        *,
        entity_ids: list[str],
        entity_type: str,
    ) -> Generator[str, None, None]:
        """Waits for Integration / Settings / Available Repositories or
        Available Boards, afterwards yields the list.
        """
        if entity_ids:
            logging.debug(
                "Waiting up to %d milliseconds for %s to appear on the screen prior starting adding them.",
                self.AVAILABLE_LIST_TIMEOUT,
                f"{entity_type}s" if len(entity_ids) > 1 else entity_type,
            )
            self.page.wait_for_timeout(self.AVAILABLE_LIST_TIMEOUT)
            yield from entity_ids

    def process_entities(
        self,
        *,
        connector: str,
        integration_name: str,
        entity_ids: list[str],
        search_function: Callable[[str, str, Locator], bool],
        add_function: Callable[[str, str, Locator], None],
        check_function: Callable[[list[str]], list[str]],
        failures: IntegrationSyncFailures,
    ) -> None:
        """Makes sure that entities (could be a repository slug, or a board
        name) are configured for given integration.

        First, it checks the presence by using search_function, if not found,
        uses add_function and afterwards validates presence of all added items
        using check_function.
        """
        added_entities: list[str] = []
        entity_type = self.entity_type(connector)

        for entity_id in self.wait_for_available_entities(
            entity_ids=entity_ids, entity_type=entity_type
        ):
            if not search_function(entity_id=entity_id):
                if add_function(entity_id=entity_id):
                    added_entities.append(entity_id)
                else:
                    failures[(connector, integration_name)].append(
                        (
                            entity_id,
                            f"❌{entity_type} {entity_id} was not in the list of available {entity_type}s or import failed.",
                        )
                    )
        missing_entries = check_function(entity_ids=added_entities)
        if missing_entries:
            failures[(connector, integration_name)].extend(missing_entries)

    def process_repositories(
        self,
        *,
        connector: str,
        integration_name: str,
        repositories: list[str],
        add_function: Callable[[str, str, Locator], bool],
        failures: IntegrationSyncFailures,
    ) -> None:
        """Adds all repositories into connector setup as membership or public
        repositories.
        """

        entity_type = self.entity_type(connector)

        search_repository = partial(
            self.has_entity_imported,
            entity_type=entity_type,
            search_field=self.search_imported_repos_field,
        )
        check_repositories = partial(
            self.check_imported_entities,
            entity_type=entity_type,
            search_function=search_repository,
        )
        self.process_entities(
            connector=connector,
            integration_name=integration_name,
            entity_ids=repositories,
            search_function=search_repository,
            add_function=partial(add_function, entity_type=entity_type),
            check_function=check_repositories,
            failures=failures,
        )

    def process_boards(
        self,
        *,
        connector: str,
        integration_name: str,
        boards: list[str],
        add_function: Callable[[str, str, Locator], bool],
        failures: IntegrationSyncFailures,
    ) -> None:
        """Adds all boards into connector setup as membership boards."""

        entity_type = self.entity_type(connector)

        search_board = partial(
            self.has_entity_imported,
            entity_type=entity_type,
            search_field=self.search_imported_boards_field,
        )
        check_boards = partial(
            self.check_imported_entities,
            entity_type=entity_type,
            search_function=search_board,
        )
        self.process_entities(
            connector=connector,
            integration_name=integration_name,
            entity_ids=boards,
            search_function=search_board,
            add_function=partial(add_function, entity_type=entity_type),
            check_function=check_boards,
            failures=failures,
        )

    def has_entity_imported(
        self, *, entity_id: str, entity_type: str, search_field: Locator
    ) -> bool:
        search_field.fill(entity_id)

        # here we need to find the innermost div element that exactly matches repository slug
        found = self.page.get_by_text(text=entity_id, exact=True).nth(0).is_visible()
        if found:
            logging.debug("✅%s '%s' is imported", entity_type, entity_id)

        search_field.clear()
        return found

    def check_imported_entities(
        self,
        *,
        entity_ids: list[str],
        entity_type: str,
        search_function: Callable[[str, str, Locator], bool],
    ) -> list[(str, str)]:
        if not entity_ids:
            return []

        logging.debug(
            "Waiting %d milliseconds for %d newly added %s to be reflected in the UI",
            self.IMPORT_TIMEOUT,
            len(entity_ids),
            entity_type,
        )
        # we should not run a generic wait however the UI doesn't give us other option
        self.page.wait_for_timeout(self.IMPORT_TIMEOUT)
        missing_entries = [
            (entry, f"❌{entity_type} {entry} was not imported.")
            for entry in entity_ids
            if not search_function(entity_id=entry)
        ]
        return missing_entries

    def add_public_repository(
        self,
        *,
        entity_id: str,
        entity_type: str,
        host="https://github.com",
    ) -> bool:
        logging.debug("⏳ Adding public %s at '%s/%s'", entity_type, host, entity_id)
        self.add_public_repository_dialog_button.click()
        self.add_public_repository_input.fill(f"{host}/{entity_id}.git")
        self.add_public_repository_confirm_button.click()
        # as UI refresh is triggered independently of the click and there is no guarantee the repository will be added
        # at the top of the page, we don't validate the action success here but later
        return True

    def add_membership_entity(
        self, *, entity_id: str, entity_type: str, search_field: Locator
    ) -> bool:
        logging.debug("⏳📝 Adding %s '%s'", entity_type, entity_id)
        search_field.fill(entity_id)
        locator = self.control_button(entity_id, order=1)
        if locator:
            locator.click()
            self.page.get_by_text("Add", exact=True).click()
            return True

        return False

    def entity_type(self, connector: str) -> str:
        if re.search(r"github", connector, re.IGNORECASE):
            return "💻 Repository"
        return "📝 Board"

    def control_button(self, entity_id: str, *, order=0) -> Optional[Locator]:
        """Finds control button.

        As there might be multiple buttons (up to 2), the function provides
        an additional logic to pick up the right one. The first button might
        be found in imported entities, the other one in available entities.

        Args:
          entity_id:
            git slug that identifies the repository, e.g. org_name/repo_name
          order: optional
            identifies what button is returned if 2 are found (by default the
            first one, indexed from 0)

        Returns:
          Control button.

        Raises:
          RuntimeError: in case more than 2 buttons are found.
        """

        # let's find the row that lists specific text exactly
        # in that row, there is a hamburger button with control menu
        locator = (
            self.page.get_by_role("row", name=entity_id)
            .filter(has=self.page.get_by_text(text=entity_id, exact=True))
            .get_by_role("button")
        )

        # there might be the same slug in both imported repositories and available repositories
        # in that case, we want to be able to select one specifically
        count = locator.count()
        if count == 1:
            return locator
        if count == 2:
            return locator.nth(order)
        if count > 2:
            raise RuntimeError(
                f"There should be up to 2 rows with {entity_id} however the script has found {locator.count()} instead. Details {str(locator)}"
            )

        return None
