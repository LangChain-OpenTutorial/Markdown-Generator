from typing import Any
from mdconverter.mdconverter import get_default_css
from nbconvert import MarkdownExporter
import nbformat


class Mdconverter:
    def __init__(self) -> None:
        self.css_filename = ""
        self.filename = ""
        self.output_filename = ""

    def run(self):
        # TODO making mdconverter using mdconvert.py
        # self.run_mdconverter()
        self.run_ndconverter(
            filename=self.filename,
            output_filename=self.output_filename,
            css_filename=self.css_filename,
        )

    def run_ndconverter(
        self, filename: str, output_filename: str, css_filename: str
    ) -> None:
        notebook_content = self.load_ipynb(filename)
        script = self.markdown_exporter(notebook_content)
        self.ndconverter_script = self.add_prefix_css(script, css_filename)
        self.save_script(self.ndconverter_script, output_filename)

    def load_ipynb(self, filename: str) -> Any:
        with open(filename, "r", encoding="utf-8") as f:
            notebook_content = nbformat.read(f, as_version=4)
        return notebook_content

    def markdown_exporter(self, notebook_content: Any) -> str:
        exporter = MarkdownExporter()
        # MarkdownExporter를 사용하여 md로 변환
        (script, resources) = exporter.from_notebook_node(notebook_content)
        return script

    def add_prefix_css(self, script: str, css_filename: str):
        return f"{get_default_css(css_filename)}\n\n{''.join(script)}"

    def save_script(self, script: str, output_filename: str) -> None:
        # 변환된 스크립트 저장
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(script)


# TODO Creating Multi loader
