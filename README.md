# `logilica-cli`

This project exports charts and text from Logilica reports and makes them
available in a variety of formats, including HTML, Markdown, and Google Docs.
The tool can also be used to configure Logilica integrations, supporting a
"configuration as code" approach.

The tool is configured via a YAML file which contains tool configuration
options and options for exporting data or configuring Logilica.  By default,
the file `weekly_report.yaml` in the current directory is used, but an
alternate path can be specified on the command line.

For export, the configuration includes a list of teams.  For each team, it
specifies a list of Logilica dashboards and the team's Jira project.  For each
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
the environment variables,
`LOGILICA_DOMAIN`, `LOGILICA_EMAIL`, and `LOGILICA_PASSWORD`.  (Note to the
Developer Practices Team:  the appropriate values for the bot account can be
obtained from the Bitwarden vault.)  Access for export uses an "email login",
which is expected to specify a view-only "bot" account.  Access for
configuration uses "SSO login" and requires the user to provide his/her own
credentials for accountability reasons.  The tool normally runs in "headless"
mode; however, in order to enable the user to perform an SSO login, the
`data-sources` subcommand opens a browser window during the run.  (You should
not interact with this window unless it prompts for your SSO credentials;
otherwise, you are likely to disrupt the functioning of the tool.)

To run the tool, check out the Git repo and run:
```pip install -r requirements.txt .```
We recommend doing this inside a [virtual environment](https://docs.python.org/3/library/venv.html).
(If you are doing development on the tool, you may want to specify `-e` in the
`pip install` command.)  After installing the tool, you also need to install
the browser which it uses to interact with the Logilica web UI:
```playwright install chromium```  (For details on debugging the web interactions,
see the `--pwdebug` option in the command help, below, and the
[Playwright documentation](https://playwright.dev/python/docs/running-tests).)

The PDF files containing the downloaded Logilica reports are stored in a
temporary directory which is created if it does not exist; if it was created by
the tool, the directory is deleted after execution is complete.  By default,
the directory is named `lwr_downloaded_pdfs`, and it is created in the current
directory, but an alternate path can be specified on the command line.

Help is available on the command line:
```text
Usage: logilica-cli [OPTIONS] COMMAND [ARGS]...

  A tool to automate UI interactions with Logilica.

Options:
  -C, --config FILE           Path to configuration file  [default:
                              ./weekly_report.yaml]
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
Usage: logilica-cli weekly-report [OPTIONS]

  Downloads and processes weekly report for teams specified in the
  configuration.

Options:
  -d, --domain TEXT               Logilica Login Credentials: Organization
                                  Name  [env var: LOGILICA_DOMAIN; required]
  -t, --downloads-temp-dir DIRECTORY
                                  Path to a directory to receive downloaded
                                  files (will be created if it doesn't exist;
                                  will be deleted if created)  [default:
                                  ./lwr_downloaded_pdfs]
  -I, --input [logilica|local]    Input source -- download from Logilica or
                                  use pre-downloaded files  [default:
                                  logilica]
  -S, --oauth, --sso / --email, --no-sso, --no-oauth
                                  Use SSO/OAuth dialog instead of specifying a
                                  username and password for Logilica access
                                  [default: email]
  -O, --output, --output-type [gdoc|console|images-only|markdown|html|markdown-with-refs|html-with-refs]
                                  Output format of how individual PDF file is
                                  processed:

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
line to see informational messages.  (If you are debugging or just nosy, adding
a _second_ `-v` will add debugging messages to the output.)
