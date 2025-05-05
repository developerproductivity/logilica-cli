from typing import Optional

from playwright.sync_api import Page

from logilica_weekly_report.page_login import LoginPage
from logilica_weekly_report.playwright_session import PlaywrightSession


class LogilicaSession:
    """Encapsulation of a logged-in Logilica session"""

    def __init__(self, oauth: bool, logilica_credentials: dict[str, str]):
        self.oauth = oauth
        self.credentials = logilica_credentials
        self.pws: Optional[PlaywrightSession] = None

    def __enter__(self) -> Page:
        """Create a Playwright session, log into Logilica, and return the
        Playwright Page for additional navigation"""
        self.pws = PlaywrightSession(headless=not self.oauth)
        page = self.pws.__enter__()
        login_page = LoginPage(page=page, credentials=self.credentials)
        login_page.navigate()
        if self.oauth:
            login_page.login_with_sso()
        else:
            login_page.login_with_email()
        return page

    def __exit__(self, exc_type, exc_value, traceback):
        """End the login session and exit the Playwright Session"""
        # TODO:  Should we actually try to log out?
        self.pws.__exit__(exc_type, exc_value, traceback)
