import pathlib

from pytest import approx

from logilica_cli.pdf_extract import PDFExtract


def test_get_pdf_objects():
    config = {
        "Mock Team": {
            "team_dashboards": {
                "Mock Team Dashboard": {"filename": "sample_report.pdf"}
            }
        }
    }

    result = PDFExtract().get_pdf_objects(
        config, pathlib.Path(__file__).parent / "fixtures"
    )
    assert len(result) == 1, "Unexpected number of teams found."
    assert len(result["Mock Team"]) == 1, "Unexpected number of dashboards found."
    assert len(result["Mock Team"]["Mock Team Dashboard"]) == approx(
        175640, abs=15
    ), "Unexpected image length"
