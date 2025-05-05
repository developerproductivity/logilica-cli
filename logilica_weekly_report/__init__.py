# logilica-weekly-report
#
# A tool for fetching Logilica reports, extracting their contents, and
# presenting them in various ways.
import inspect
from typing import Callable, List

import click


def compose_options(cmd_func: Callable, opt_list: List[Callable]) -> Callable:
    """Utility function which composes a list of click.options into a single decorator

    Args:
        cmd_func:  the Click command function to be decorated
        opt_list:  a list of click.option invocations to compose

    Returns:
        A composite decorator function value
    """
    if opt_list:
        opt_func = opt_list.pop()
        return opt_func(compose_options(cmd_func, opt_list))
    return cmd_func


def sort_click_command_parameters(cmd_func) -> Callable:
    """A decorator which sorts the Click command parameter list (arguments and options)

    We grab the list of click.Parameter's from the click.Command object which we
    are passed as our input and sort it (in place).  We use the longest option
    (including the hyphens) as the sort key value.
    """
    assert isinstance(
        cmd_func, click.Command
    ), "The {} decorator must appear before the click.command() or click.group() decorator in the source code".format(
        inspect.currentframe().f_code.co_name
    )
    cmd_func.params.sort(key=lambda x: sorted(x.opts, key=lambda s: -len(s)))
    return cmd_func


def common_options(f):
    """Options used by multiple subcommands"""

    return compose_options(
        f,
        [
            click.option(
                "--username",
                "-u",
                envvar="LOGILICA_EMAIL",
                required=False,
                show_default=True,
                show_envvar=True,
                help="Logilica Login Credentials: User Email",
            ),
            click.password_option(
                "--password",
                "-p",
                envvar="LOGILICA_PASSWORD",
                required=False,
                show_default=True,
                show_envvar=True,
                help="Logilica Login Credentials: Password",
            ),
            click.option(
                "--domain",
                "-d",
                envvar="LOGILICA_DOMAIN",
                required=True,
                show_default=True,
                show_envvar=True,
                help="Logilica Login Credentials: Organization Name",
            ),
            click.option(
                "--oauth/--email",
                "--sso/--no-sso",
                "-S/--no-oauth",
                default=False,
                required=False,
                is_flag=True,
                show_default=True,
                help="Use SSO/OAuth dialog instead of specifying a username and password for Logilica access",
            ),
        ],
    )
