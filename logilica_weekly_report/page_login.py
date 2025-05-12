import logging
from typing import Any

import click
from playwright.sync_api import expect, Page


class LoginPage:
    """Page Object to handle interactions with Login Page."""

    LOGILICA_LOGIN = "https://logilica.io/login"

    def __init__(self, page: Page, credentials: dict[str, Any]):
        self.page = page
        self.credentials: dict[str, Any] = credentials
        self.email_login_button = page.get_by_role("button", name="Log in With Email")
        self.sso_login_button = page.get_by_role("button", name="Log in With SSO")
        self.domain_field = page.locator("#domain")
        self.email_field = page.locator("#email")
        self.password_field = page.locator("#password")
        self.login_button = page.get_by_role("button", name="Login")

    def navigate(self):
        self.page.goto(self.LOGILICA_LOGIN)

    def login_with_email(self):
        logging.info("Logging into Logilica via email")
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

    def login_with_sso(self):
        logging.info("Logging into Logilica via SSO")
        self.sso_login_button.click()
        self.domain_field.fill(self.credentials["domain"])
        self.login_button.click()

        click.echo("Please complete the SSO login in the Chromium window.")
        self.page.wait_for_url(
            "**/*redirect*", timeout=120000
        )  # "https://logilica.io/thirdPartyLogin/redirect"
        click.echo(
            "SSO login completed successfully; continuing. (Please do not disturb the Chromium window.)"
        )

        # There are some intermediate steps that have to complete before we
        # can return to navigation, so wait for the main page to appear before
        # returning control to the caller.  (The main page is locally unique in
        # that its URL ends in a slash (https://logilica.io/).
        self.page.wait_for_url(lambda s: s.endswith("/"))
