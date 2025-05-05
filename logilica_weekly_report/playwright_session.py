from typing import Optional

from playwright.sync_api import BrowserContext, Page, sync_playwright

from logilica_weekly_report.page_login import LoginPage


class PlaywrightSession:
    """Encapsulation of Playwright Browser for usage in Page Objects."""

    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(accept_downloads=True)
        self.page = self.context.new_page()
        return self.page

    def __exit__(self, exc_type, exc_value, traceback):
        self.browser.close()
        self.playwright.stop()


class LogilicaSession(PlaywrightSession):
    """Encapsulation of a logged-in Logilica session as an extension of a
    PlaywrightSession"""

    def __init__(self, oauth: bool, logilica_credentials: dict[str, str]):
        super().__init__(headless=not oauth)
        self.oauth = oauth
        self.credentials = logilica_credentials

    def __enter__(self) -> Page:
        """Start the Playwright session, log into Logilica, and return the
        Playwright Page for additional navigation"""
        page = super().__enter__()
        login_page = LoginPage(page=page, credentials=self.credentials)
        login_page.navigate()
        if self.oauth:
            login_page.login_with_sso()
        else:
            login_page.login_with_email()
        return page
