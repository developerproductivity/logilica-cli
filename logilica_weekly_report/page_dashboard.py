import logging
import pathlib
from typing import Any

from playwright.sync_api import Page, TimeoutError


class DashboardPage:
    def __init__(self, page: Page):
        self.page = page
        self.export_pdf_button = page.get_by_role("button", name="Export PDF")
        self.download_button = page.get_by_role("button", name="Download").nth(1)
        self.close_download_button = page.get_by_role("button", name="Close").nth(1)

    def open_dashboard(self, dashboard_name: str, menu_category: str) -> None:
        logging.debug("Opening dashboard '%s / %s'", menu_category, dashboard_name)

        # try to find dashboard link first
        dashboard = self.page.get_by_role("link", name=dashboard_name)

        # if menu category was provided, check if dropdown is open
        if menu_category:
            try:
                dashboard.wait_for(state="visible", timeout=3000)
            except TimeoutError:
                logging.debug("Opening menu category '%s' first", menu_category)
                self.page.get_by_role("link", name=menu_category).click()
                dashboard.wait_for(state="visible", timeout=3000)

        # open dashboard
        dashboard.click()

    def download_dashboard_to(self, path: pathlib.Path) -> None:
        self.export_pdf_button.click()
        # download file and close the dialog afterwards
        with self.page.expect_download() as download_info:
            self.download_button.click()
            download = download_info.value
            download.save_as(path)
            self.close_download_button.click()
        logging.debug("Download stored in '%s'", path)

    def download_team_dashboards(
        self, teams: dict[str, Any], base_dir_path: pathlib.Path
    ):
        for team, dashboards in teams.items():
            for dashboard, options in dashboards["team_dashboards"].items():
                self.open_dashboard(
                    dashboard_name=dashboard, menu_category="Custom Reports"
                )
                self.download_dashboard_to(path=base_dir_path / options["Filename"])
            logging.info(
                "Downloaded %d dashboard(s) for '%s' team",
                len(dashboards["team_dashboards"]),
                team,
            )
