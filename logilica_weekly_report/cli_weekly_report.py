import logging
import os
from pathlib import Path
import shutil

import click

from logilica_weekly_report.page_dashboard import DashboardPage
from logilica_weekly_report.page_login import LoginPage
from logilica_weekly_report.pdf_convert import PDFConvert
from logilica_weekly_report.pdf_extract import PDFExtract
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
    "--downloads-temp-dir",
    "-t",
    "downloads_temp_dir",
    type=click.Path(writable=True, file_okay=False, path_type=Path, resolve_path=True),
    default=DEFAULT_DOWNLOADS_DIR,
    show_default=True,
    help="Path to a directory to receive downloaded files"
    " (will be created if it doesn't exist; will be deleted if created)",
)
@click.option(
    "--input",
    "-I",
    "source",  # parameter name, since Python reserves "input"
    type=click.Choice(["logilica", "local"], case_sensitive=False),
    default="logilica",
    show_default=True,
    help="Input source -- download from Logilica or use pre-downloaded files",
)
@click.option(
    "--output",
    "--output-type",
    "-O",
    type=click.Choice(
        [
            "gdoc",
            "console",
            "images-only",
            "markdown",
            "html",
            "markdown-with-refs",
            "html-with-refs",
        ],
        case_sensitive=False,
    ),
    default="gdoc",
    show_default=True,
    help="""Output format of how individual PDF file is processed:

    gdoc: HTML with an embedded image represeting whole dashboard and
        stored as a Google Doc on Google Drive
    console: HTML with an embedded image represeting whole dashboard to stdout
    images-only: Embedded image only as a PNG.
    markdown: PDF parsed by docling into Markdown, with images embedded
        in it. Images might represent individual charts.
    html: PDF parsed by docling into HTML, with images embedded in it.
        Images might represent individual charts.
    markdown-with-refs: PDF parsed by docling into Markdown, with images stored
        externally and referenced. Images might represent individual charts.
    html-with-refs: PDF parsed by docling into HTML, with images stored
        externally and referenced. Images might represent individual charts.
    """,
)
@click.option(
    "--scale",
    "-s",
    "scale",
    type=float,
    default=1.0,
    show_default=True,
    help="Resolution of the images scale factor * 72 DPI. Higher the number,"
    " higher the resolution and size of the images",
)
@click.pass_context
def weekly_report(
    context: click.Context,
    downloads_temp_dir: Path,
    source: str,
    output: str,
    scale: int,
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
            filename: board1_report.pdf
            url: some-string
      Team 2:
        team_dashboards:
          Board 1:
            filename: board2_report.pdf
            url: some-string
        ...
    ...
    """
    exit_status = 0
    configuration = context.obj["configuration"]
    config = configuration.get("config", {})
    logilica_credentials = context.obj["logilica_credentials"]
    output_dir_path = context.obj["output_dir_path"]

    # If needed, get the credentials now to enable "failing early".
    google_credentials = get_google_credentials(config) if output == "gdoc" else None

    remove_downloads = not downloads_temp_dir.exists()
    logging.debug(
        "download directory %s", "does not exist" if remove_downloads else "exists"
    )
    if remove_downloads:
        os.mkdir(downloads_temp_dir)
        logging.info("download directory, %s, created", downloads_temp_dir)

    try:
        if source == "logilica":
            logging.info("Starting session")
            with PlaywrightSession() as page:
                login_page = LoginPage(page=page, credentials=logilica_credentials)
                login_page.navigate()
                login_page.login()

                dashboard_page = DashboardPage(page=page)
                dashboard_page.download_team_dashboards(
                    teams=configuration["teams"], base_dir_path=downloads_temp_dir
                )

        convertor = PDFConvert(
            output_dir_path=output_dir_path,
            download_dir_path=downloads_temp_dir,
            scale=scale,
        )
        if output in {"markdown", "html", "markdown-with-refs", "html-with-refs"}:
            parts = output.split("-", 1)
            (format, embedd_images) = (parts[0], False if len(parts) > 1 else True)
            convertor.to_format_multiple(
                teams=configuration["teams"],
                format=format,
                embedd_images=embedd_images,
            )
        else:
            pdf_items = PDFExtract(scale=scale).get_pdf_objects(
                teams=configuration["teams"], download_dir_path=downloads_temp_dir
            )
            if output == "images-only":
                convertor.to_images(pdf_items=pdf_items)
            else:
                doc = generate_html(pdf_items)
                if output == "gdoc":
                    url = upload_doc(doc.getvalue(), google_credentials, config)
                    click.echo(f"Report uploaded to {url}")
                else:
                    click.echo(doc.getvalue(), err=False)

    except Exception as err:
        click.echo(f"Unexpected exception, {type(err).__name__}: {err}", err=True)
        exit_status = 1
    finally:
        if remove_downloads:
            logging.info("removing downloads directory")
            shutil.rmtree(downloads_temp_dir)

    context.exit(exit_status)
