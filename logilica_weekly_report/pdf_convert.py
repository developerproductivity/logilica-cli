from functools import partialmethod
import logging
from pathlib import Path
from typing import Any, Literal

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode


class PDFConvert:
    """Converts PDF file(s) to a different format, such as images, html or
    markdown documents.

    Args:
      output_dir_path: where resulting assets are stored
      download_dir_path: where pdfs to be converted are stored
      scale: DPI of the images extracted, in multiplies of 72 DPI
    """

    def __init__(self, *, output_dir_path: Path, download_dir_path: Path, scale: float):
        self.output_dir_path = output_dir_path
        self.download_dir_path = download_dir_path
        self.scale = scale

        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = scale
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    def to_image(self, *, rawimage: bytes, team: str, dashboard: str) -> None:
        self.output_dir_path.mkdir(parents=True, exist_ok=True)
        filename = f"{team}-{dashboard}.png".lower().replace(" ", "-")
        imagepath = self.output_dir_path / filename
        logging.info("storing dashboard '%s' at '%s'", dashboard, imagepath)
        imagepath.write_bytes(rawimage)

    def to_images(self, pdf_items: dict[str, dict[str, bytes]]) -> int:
        total: int = 0
        for team, dashboards in pdf_items.items():
            for dashboard, rawimage in dashboards.items():
                self.to_image(rawimage=rawimage, team=team, dashboard=dashboard)
                total += 1
        logging.info("stored %d images in %s", total, self.output_dir_path)
        return total

    def to_format(
        self,
        *,
        format: Literal["markdown", "html"],
        pdf_path: str,
        team: str,
        dashboard: str,
        embed_images: bool = True,
    ) -> None:
        self.output_dir_path.mkdir(parents=True, exist_ok=True)

        result = self.converter.convert(pdf_path)
        doc_stem = f"{team}-{dashboard}".lower().replace(" ", "-")
        doc_type = "with-images" if embed_images else "with-image-refs"
        extension = "md" if format == "markdown" else "html"
        output_file = self.output_dir_path / f"{doc_stem}-{doc_type}.{extension}"

        image_mode = ImageRefMode.EMBEDDED if embed_images else ImageRefMode.REFERENCED

        if format == "markdown":
            result.document.save_as_markdown(
                filename=output_file, image_mode=image_mode
            )
        else:
            result.document.save_as_html(filename=output_file, image_mode=image_mode)

        logging.debug(
            "Converted team's '%s' dashboard '%s' into %s (%s mode)",
            team,
            dashboard,
            str(output_file),
            "embedded" if embed_images else "referenced",
        )

    def to_format_multiple(
        self,
        *,
        format: Literal["markdown", "html"],
        teams: dict[str, dict[str, Any]],
        embed_images: bool = True,
    ) -> int:

        total = 0
        for team, dashboards in teams.items():
            for dashboard, options in dashboards["team_dashboards"].items():
                logging.info("Processing items from '%s' for %s", dashboard, team)
                path = self.download_dir_path / str(options["filename"])
                self.to_format(
                    format=format,
                    pdf_path=path,
                    dashboard=dashboard,
                    team=team,
                    embed_images=embed_images,
                )
                total += 1
        logging.debug("Converted %d dashboards for %d teams", total, len(teams.items()))
        return total

    to_markdowns = partialmethod(to_format_multiple, format="markdown")
    to_htmls = partialmethod(to_format_multiple, format="html")
