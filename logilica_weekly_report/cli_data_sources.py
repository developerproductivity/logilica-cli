import click

from logilica_weekly_report import common_options, sort_click_command_parameters
from logilica_weekly_report.logilica_session import LogilicaSession
from logilica_weekly_report.page_login import LoginPage
from logilica_weekly_report.page_settings import SettingsPage
from logilica_weekly_report.playwright_session import PlaywrightSession

# Default values for command options
DEFAULT_CONFIG_FILE = "./weekly_report.yaml"
DEFAULT_DOWNLOADS_DIR = "./lwr_downloaded_pdfs"


@sort_click_command_parameters
@click.command()
@common_options
@click.pass_context
def data_sources(
    context: click.Context,
    username: str,
    password: str,
    domain: str,
    oauth: bool,
) -> None:
    """Synchronizes configuration of integrations with the configuration file.

    \f

    Configures Integrations in Logilica to contain repositories listed
    in the configuration file. It is able to process public repositories
    and membership repositories - membership repositories require
    the integration bot to be a member of the repository with read access.

    Configuration example snippet:
    \b
    >>>
    ...
    integrations:
      integration_name:
        connector: GitHub
        membership_repositories:
          - org/repository1
          - org/repository2
        public_repositories:
          - public-org/repository1
          - public-org/repository2
      integration_name_2:
        ...
    ...
    """

    exit_status = 0
    configuration = context.obj["configuration"]
    logilica_credentials = {
        "username": username,
        "password": password,
        "domain": domain,
    }
    try:
        with LogilicaSession(oauth, logilica_credentials) as page:
            settings_page = SettingsPage(page=page)
            settings_page.sync_integrations(integrations=configuration["integrations"])

    except Exception as err:
        click.echo(f"Unexpected exception, {type(err).__name__}: {err}", err=True)
        exit_status = 1

    context.exit(exit_status)
