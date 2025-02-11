import logging
from typing import Any

from playwright.sync_api import expect, Page


class LoginPage:
    """Page Object to handle interactions with Login Page."""

    LOGILICA_LOGIN = "https://logilica.io/login"

    def __init__(self, page: Page, credentials: dict[str, Any]):
        self.page = page
        self.credentials: dict[str, Any] = credentials
        self.email_login_button = page.get_by_role("button", name="Log in With Email")
        self.domain_field = page.locator("#domain")
        self.email_field = page.locator("#email")
        self.password_field = page.locator("#password")
        self.login_button = page.get_by_role("button", name="Login")

    def navigate(self):
        self.page.goto(self.LOGILICA_LOGIN)

    def login(self):
        logging.info("Logging into Logilica")
        self.email_login_button.click()
        self.domain_field.fill(self.credentials["domain"])
        self.email_field.fill(self.credentials["username"])
        self.password_field.fill(self.credentials["password"])
        self.login_button.click()

        try:
            expect(self.page).not_to_have_url(self.LOGILICA_LOGIN)
        except AssertionError:
            logging.error("Login failed")
            raise ValueError("Login credentials rejected")
        logging.debug("Login to Logilica complete")
