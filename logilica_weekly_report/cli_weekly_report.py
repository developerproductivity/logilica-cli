import logging
import os
import pathlib
import shutil

import click

from logilica_weekly_report.page_dashboard import DashboardPage
from logilica_weekly_report.page_login import LoginPage
from logilica_weekly_report.pdf_extract import get_pdf_objects
from logilica_weekly_report.playwright_session import PlaywrightSession
from logilica_weekly_report.update_gdoc import (
    generate_html,
    get_google_credentials,
    upload_doc,
)

# Default values for command options
DEFAULT_DOWNLOADS_DIR = "./lwr_downloaded_pdfs"


@click.command()
@click.option(
    "--downloads",
    "-d",
    "download_dir_path",
    type=click.Path(
        writable=True, file_okay=False, path_type=pathlib.Path, resolve_path=True
    ),
    default=DEFAULT_DOWNLOADS_DIR,
    show_default=True,
    help="Path to a directory to receive downloaded files"
    " (will be created if it doesn't exist; will be deleted if created)",
)
@click.option(
    "--output",
    "-O",
    type=click.Choice(["gdoc", "html"], case_sensitive=False),
    default="gdoc",
    show_default=True,
    help="Output format -- HTML to stdout or stored as a Google Doc on Google Drive",
)
@click.pass_context
def weekly_report(
    context: click.Context, download_dir_path: pathlib.Path, output: str
) -> None:
    """Downloads and processes weekly report for teams specified in the
    configuration.

    \f

    Downloads Logilica dashboards as PDFs and parses the content into
    a single file.

    Configuration example snippet:
    \b
    >>>
    ...
    teams:
      Team 1:
        team_dashboards:
          Board 1:
            Filename: board1_report.pdf
        jira_projects: issues.redhat.com/FOO
      Team 2:
        team_dashboards:
          Board 1:
            Filename: board2_report.pdf
        jira_projects: issues.redhat.com/BAR
        ...
    ...
    """
    exit_status = 0
    configuration = context.obj["configuration"]
    logilica_credentials = context.obj["logilica_credentials"]

    # Get the credentials now to enable "failing early".
    google_credentials = get_google_credentials(configuration["config"])

    remove_downloads = not download_dir_path.exists()
    logging.debug(
        "download directory %s", "does not exist" if remove_downloads else "exists"
    )
    if remove_downloads:
        os.mkdir(download_dir_path)
        logging.info("download directory, %s, created", download_dir_path)

    try:
        with PlaywrightSession() as page:
            # Fill the login form using environment variables
            login_page = LoginPage(page=page, credentials=logilica_credentials)
            login_page.navigate()
            login_page.login()

            dashboard_page = DashboardPage(page=page)
            dashboard_page.download_team_dashboards(
                teams=configuration["teams"], base_dir_path=download_dir_path
            )

        pdf_items = get_pdf_objects(
            teams=configuration["teams"], download_dir_path=download_dir_path
        )
        doc = generate_html(pdf_items)
        if output == "gdoc":
            upload_doc(doc.getvalue(), google_credentials, configuration["config"])
        else:
            click.echo(doc.getvalue(), err=False)
    except Exception as err:
        click.echo(err, err=True)
        exit_status = 1
    finally:
        if remove_downloads:
            logging.info("removing downloads directory")
            shutil.rmtree(download_dir_path)

    context.exit(exit_status)
