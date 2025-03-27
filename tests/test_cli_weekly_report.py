from pathlib import Path
import shutil

from click.testing import CliRunner
import pytest
from pytest import approx
import yaml

from logilica_weekly_report.__main__ import cli

with open(Path(__file__).parent / "fixtures/config.yaml", "r") as yaml_file:
    FULL_CONFIG = yaml.safe_load(yaml_file)

OUTPUT_DIR = "./test-output"

BASE_ARGS = [
    "--username",
    "testuser",
    "--password",
    "testpassword",
    "--domain",
    "testorg",
    "--config",
    "config.yaml",
    "--output-dir",
    OUTPUT_DIR,
    "weekly-report",
    "-t",
    "downloads",
    "-I",
    "local",
]


@pytest.fixture(autouse=True)
def setup_cli_isolated_env():
    runner = CliRunner()
    fixtures_dir = Path(__file__).parent / "fixtures"

    with runner.isolated_filesystem():
        with open("config.yaml", "w") as f:
            f.write(yaml.safe_dump(FULL_CONFIG))

        target_dir = Path(".") / "downloads"
        shutil.copytree(fixtures_dir, target_dir)
        yield runner


def test_weekly_report_image_generation(setup_cli_isolated_env):
    runner = setup_cli_isolated_env

    result = runner.invoke(
        cli,
        [
            *BASE_ARGS,
            "--output-type",
            "images-only",
        ],
    )

    assert result.exit_code == 0, result.output
    assert Path(
        f"{OUTPUT_DIR}/my-awesome-team-team-productivity-dashboard.png"
    ).exists()


def test_weekly_report_markdown(setup_cli_isolated_env):
    runner = setup_cli_isolated_env

    result = runner.invoke(
        cli,
        [
            *BASE_ARGS,
            "--output-type",
            "markdown",
        ],
    )

    assert result.exit_code == 0, result.output
    files = list(Path(OUTPUT_DIR).rglob("*"))
    assert len(files) == 1
    assert Path(
        f"{OUTPUT_DIR}/my-awesome-team-team-productivity-dashboard-with-images.md"
    ).exists()


def test_weekly_report_html(setup_cli_isolated_env):
    runner = setup_cli_isolated_env

    result = runner.invoke(
        cli,
        [
            *BASE_ARGS,
            "--output-type",
            "html",
        ],
    )

    assert result.exit_code == 0, result.output
    files = list(Path(OUTPUT_DIR).rglob("*"))  # Recursively get all files and folders
    assert len(files) == 1
    assert Path(
        f"{OUTPUT_DIR}/my-awesome-team-team-productivity-dashboard-with-images.html"
    ).exists()


def test_weekly_report_html_with_refs(setup_cli_isolated_env):
    runner = setup_cli_isolated_env

    result = runner.invoke(
        cli,
        [
            *BASE_ARGS,
            "--output-type",
            "html-with-refs",
        ],
    )

    assert result.exit_code == 0, result.output
    files = list(Path(OUTPUT_DIR).rglob("*"))
    assert len(files) == 7
    assert Path(
        f"{OUTPUT_DIR}/my-awesome-team-team-productivity-dashboard-with-image-refs.html"
    ).exists()


def test_weekly_report_markdown_with_refs(setup_cli_isolated_env):
    runner = setup_cli_isolated_env

    result = runner.invoke(
        cli,
        [
            *BASE_ARGS,
            "--output-type",
            "markdown-with-refs",
        ],
    )

    assert result.exit_code == 0, result.output
    files = list(Path(OUTPUT_DIR).rglob("*"))
    assert len(files) == 7
    assert Path(
        f"{OUTPUT_DIR}/my-awesome-team-team-productivity-dashboard-with-image-refs.md"
    ).exists


def test_weekly_report_console(setup_cli_isolated_env):
    runner = setup_cli_isolated_env

    result = runner.invoke(
        cli,
        [
            *BASE_ARGS,
            "--output-type",
            "console",
        ],
    )

    assert result.exit_code == 0, result.output
    files = list(Path(OUTPUT_DIR).rglob("*"))
    assert len(files) == 0
    assert len(result.output) == approx(234360, abs=25), "Unexpected document length"
