import pathlib

from logilica_weekly_report.pdf_extract import PDFExtract


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
    assert 1 == len(result), "Unexpected number of teams found."
    assert 1 == len(result["Mock Team"]), "Unexpected number of dashboards found."
    assert 175655 == len(
        result["Mock Team"]["Mock Team Dashboard"]
    ), "Unexpected image length"
