import os, yaml

from playwright.sync_api import Playwright, sync_playwright


def run(playwright: Playwright) -> None:
    #Read and load weekly_report.yaml file
    with open("weekly_report.yaml", "r")as yaml_file:
        teams_data = yaml.safe_load(yaml_file)

    # Specify the download directory
    download_path = teams_data["config"]["Download_path"]

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    # Navigate to the login page
    page.goto("https://logilica.io/login")

    # Fill the login form using environment variables
    page.get_by_role("button", name="Log in With Email").click()
    page.locator("#domain").fill(os.getenv("LOGILICA_DOMAIN"))
    page.locator("#email").fill(os.getenv("LOGILICA_EMAIL"))
    page.locator("#password").fill(os.getenv("LOGILICA_PASSWORD"))

    # Submit the form
    page.get_by_role("button", name="Login").click()
    page.get_by_role("link", name="Custom Reports").click()

    # Cycle though list of teams dashboards to download a pdf for each team
    for team, dashboards in teams_data["teams"].items():
        for dashboard, options in dashboards["team_dashboards"].items():
            print("loop")
            page.get_by_role("link", name=dashboard).click()
            page.get_by_role("button", name="Export PDF").click()
            # Handle download
            with page.expect_download() as download_info:
                page.get_by_role("button", name="Download").click()
            download = download_info.value
            download.save_as(download_path + options["Filename"])
            # Close PDF view dialog
            page.get_by_role("button", name="Close").click()

    # Clean up
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
