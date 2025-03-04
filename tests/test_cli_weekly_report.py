from pathlib import Path
import shutil

from click.testing import CliRunner
import yaml

from logilica_weekly_report.__main__ import cli

with open(Path(__file__).parent / "fixtures/config.yaml", "r") as yaml_file:
    FULL_CONFIG = yaml.safe_load(yaml_file)


def test_weekly_report_image_generation():
    runner = CliRunner()
    fixtures_dir = Path(__file__).parent / "fixtures"

    with runner.isolated_filesystem():
        with open("config.yaml", "w") as f:
            f.write(yaml.safe_dump(FULL_CONFIG))

        target_dir = Path(".") / "downloads"
        shutil.copytree(fixtures_dir, target_dir)

        result = runner.invoke(
            cli,
            [
                "-u",
                "testuser",
                "-p",
                "testpassword",
                "-d",
                "testorg",
                "-C",
                "config.yaml",
                "weekly-report",
                "-t",
                "downloads",
                "-I",
                "local",
                "-O",
                "images-only",
            ],
        )

        assert result.exit_code == 0, result.output
        assert Path(
            "output/my-awesome-team-team-productivity-dashboard.png"
        ).exists(), "Awesome Team Dashboard PNG was not extracted"
