import logging
import pathlib
from typing import Any

from playwright.sync_api import expect, Page

from logilica_weekly_report.page_navigation import NavigationPanel


class DashboardPage:
    LOAD_TIMEOUT = 30000

    def __init__(self, page: Page):
        self.page = page
        self.export_pdf_button = page.get_by_role("button", name="Export PDF")
        self.download_button = page.get_by_role("button", name="Download").nth(1)
        self.close_download_button = page.get_by_role("button", name="Close").nth(1)

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
        self,
        teams: dict[str, Any],
        base_dir_path: pathlib.Path,
        *,
        menu_dropdown="Custom Reports",
    ) -> None:
        for team, dashboards in teams.items():
            for dashboard, options in dashboards["team_dashboards"].items():
                logging.debug(
                    "Downloading dashboard '%s / %s' for team '%s'",
                    menu_dropdown,
                    dashboard,
                    team,
                )
                NavigationPanel(self.page).navigate(
                    link_name=dashboard, menu_dropdown=menu_dropdown
                )
                expect(self.export_pdf_button).to_be_visible(
                    timeout=DashboardPage.LOAD_TIMEOUT
                )

                if filters := options.get("filter"):
                    for filter_, values in filters.items():
                        controls = self.page.locator("css=.css-qmtbtl-control")
                        controls.get_by_text(filter_, exact=True).click()
                        for value in values:
                            loc = self.page.locator("css=.flex.p-2.cursor-pointer")
                            loc.get_by_text(value).click()
                        self.page.get_by_role("button", name="Apply").click()

                self.download_dashboard_to(path=base_dir_path / options["Filename"])

                if filters:
                    # Clear all the filters
                    clicked = 0
                    controls = self.page.locator("css=.my-auto.cursor-pointer")
                    for control in controls.all():
                        if control.is_visible():
                            control.click()
                            clicked += 1
                    if clicked != len(filters):
                        logging.warning(
                            "Cleared %d filters but set %d", clicked, len(filters)
                        )
            logging.info(
                "Downloaded %d dashboard%s for '%s' team",
                len(dashboards["team_dashboards"]),
                "s" if len(dashboards["team_dashboards"]) > 1 else "",
                team,
            )
