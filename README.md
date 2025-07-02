# `logilica-cli`

`logilica-cli` is a command-line tool which provides CLI access to the Logilica
UI. The tool currently provides two subcommands. The first exports charts and
text from Logilica reports and makes them available in a variety of formats,
including HTML, Markdown, and as a Google Docs document. The second is used to
configure Logilica integrations, supporting a "configuration as code" approach.

The tool is configured via a YAML file which contains tool configuration
options as well as options for exporting data or configuring Logilica. By
default, the file `logica-cli.yaml` in the current directory is used, but an
alternate path can be specified on the command line.

For export, the configuration includes a list of teams. For each team, it
specifies a list of Logilica dashboards and the team's Jira project. For each
dashboard, it specifies the name of an output file (which must not conflict
with any other team's dashboards' output files) and possibly other attributes.

For configuring Logilica integrations, the configuration provides a list of
connectors, where each entry is the credential used for the connection, under
which there is a `connector` type and a list of `membership_boards`,
`membership_repositories`, or `public_repositories` depending on whether the
connector is for (e.g., Jira) boards, privately-accessed (e.g. GitHub)
repositories, or publicly-accessed (e.g., GitHub) repositories, respectively.

To onboard a new team, add connectors for its data sources, create a new
Logilica dashboard for it, and add the team and the dashboard information to
the configuration file.

Credentials for accessing Logilica are provided by command line options or by
the environment variables, `LOGILICA_DOMAIN`, `LOGILICA_EMAIL`, and
`LOGILICA_PASSWORD`. (Note to the Developer Practices Team: the appropriate
values for the bot accounts can be obtained from the Bitwarden vault; users
with admin privileges can also create their own username/password credentials
using the Logilica UI.) For interactive use, OAuth or SSO credentials can be
used. The tool normally runs in "headless" mode; however, in order to enable
the user to perform an SSO login, the tool opens a browser window during the
run. (You should not interact with this window unless it prompts for your SSO
credentials; otherwise, you are likely to disrupt the functioning of the tool.)

To install the tool, check out the Git repo and run:

```
pip install -r requirements.txt .
playwright install chromium
```

We recommend doing this inside a [virtual environment](https://docs.python.org/3/library/venv.html),
which uses Python 3.12+.

The PDF files containing the downloaded Logilica reports are stored in a
temporary directory which is created if it does not exist; if it was created by
the tool, the directory is deleted after execution is complete.

Help is available on the command line:

```text
Usage: logilica-cli [OPTIONS] COMMAND [ARGS]...

  A tool to automate UI interactions with Logilica.

Options:
  -C, --config FILE           Path to configuration file  [default:
                              ./logilica-cli.yaml]
  -o, --output-dir DIRECTORY  Path to a directory to store output if image-
                              only output is selected  [default: ./output]
  -D, --pwdebug, --PWD        Enable Playwright debug mode
  -v, --verbose               Enable verbose mode; specify multiple times to
                              increase verbosity
  --help                      Show this message and exit.

Commands:
  data-sources   Synchronizes configuration of integrations with the...
  weekly-report  Downloads and processes weekly report for teams...

  For more information, see https://github.com/developerproductivity/logilica-
  cli#logilica-cli

```

```text
logilica-cli weekly-report --help
Usage: logilica-cli weekly-report [OPTIONS]

  Downloads and processes weekly report for teams specified in the
  configuration.

Options:
  -d, --domain TEXT               Logilica Login Credentials: Organization
                                  Name  [env var: LOGILICA_DOMAIN; required]
  -t, --downloads-temp-dir DIRECTORY
                                  Path to a directory to receive downloaded
                                  files (if unspecified, a temporary directory
                                  will be used; otherwise, the specified
                                  directory will be created if it doesn't
                                  exist; if the directory is created by the
                                  tool, it will be deleted after the run)
  -I, --input [logilica|local]    Input source -- download from Logilica or
                                  use pre-downloaded files  [default:
                                  logilica]
  -S, --oauth, --sso / --email, --no-sso, --no-oauth
                                  Use SSO/OAuth dialog instead of specifying a
                                  username and password for Logilica access
                                  [default: email]
  -O, --output, --output-type [pdf|gdoc|console|images-only|markdown|html|markdown-with-refs|html-with-refs]
                                  Output format of how individual PDF file is
                                  processed:

                                  pdf: Don't process files, keep PDFs.

                                  gdoc: HTML with an embedded image
                                  representing whole dashboard and stored as a
                                  Google Doc on Google Drive

                                  console: HTML with an embedded image
                                  representing whole dashboard to stdout

                                  images-only: Embedded image only as a PNG.

                                  markdown: PDF parsed by docling into
                                  Markdown, with images embedded in it. Images
                                  might represent individual charts.

                                  html: PDF parsed by docling into HTML, with
                                  images embedded in it.  Images might
                                  represent individual charts.

                                  markdown-with-refs: PDF parsed by docling
                                  into Markdown, with images stored externally
                                  and referenced. Images might represent
                                  individual charts.

                                  html-with-refs: PDF parsed by docling into
                                  HTML, with images stored externally and
                                  referenced. Images might represent
                                  individual charts.  [default: gdoc]
  -p, --password TEXT             Logilica Login Credentials: Password  [env
                                  var: LOGILICA_PASSWORD]
  -s, --scale FLOAT               Resolution of the images scale factor * 72
                                  DPI. Higher the number, higher the
                                  resolution and size of the images  [default:
                                  1.0]
  -u, --username TEXT             Logilica Login Credentials: User Email  [env
                                  var: LOGILICA_EMAIL]
  --help                          Show this message and exit.
```

```text
Usage: logilica-cli data-sources [OPTIONS]

  Synchronizes configuration of integrations with the configuration file.

Options:
  -d, --domain TEXT               Logilica Login Credentials: Organization
                                  Name  [env var: LOGILICA_DOMAIN; required]
  -S, --oauth, --sso / --email, --no-sso, --no-oauth
                                  Use SSO/OAuth dialog instead of specifying a
                                  username and password for Logilica access
                                  [default: email]
  -p, --password TEXT             Logilica Login Credentials: Password  [env
                                  var: LOGILICA_PASSWORD]
  -u, --username TEXT             Logilica Login Credentials: User Email  [env
                                  var: LOGILICA_EMAIL]
  --help                          Show this message and exit.
```

Some dashboards can be quite slow to load into the UI, so, if you are running
the tool interactively and wish to track its progress, add a `-v` to the command
line to see informational messages. (If you are debugging or just nosy, adding
a _second_ `-v` will add debugging messages to the output.)

## Development

If you are doing development on the tool, you may want to specify `-e` in the `pip install` command to install it in editable mode.
This means that you can make changes to the package's source code and those changes will be reflected in your project without having to reinstall the package.

For details on debugging the web interactions, see the `--pwdebug` option in the command help and the [Playwright documentation](https://playwright.dev/python/docs/running-tests).

### Linting and formatting rules

This project uses `pre-commit` to handle linting and formatting. The `pre-commit` tool reads its configuration from [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) and the configuration options for the individual linters and formatters can be found in the [`pyproject.toml`](./pyproject.toml) file.
The same configuration is used in CI.

To install and execute it locally, follow these steps:

```
pip install pre-commit
pre-commit install
pre-commit run --all-files --hook-stage [pre-commit|manual]
```

If you run `pre-commit` stage, you can check your files, if you run `manual` stage, it will modify your files to correct problems it finds.

### Enabling Red Hat InfoSec plugin

If you are developing locally within Red Hat, you should enable Red Hat InfoSec plugin. You can do that by uncommenting appropriate lines in `.pre-commit-config.yaml` file.
Make sure that you don't commit that change back upstream, as it would break the CI.
