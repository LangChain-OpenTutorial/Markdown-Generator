import codecs
import json
import argparse
from typing import List, Dict, Any, Optional


def get_default_css() -> str:
    """기본 CSS 스타일을 반환합니다."""
    return """<style>
    .custom {
        background-color: #008d8d;
        color: white;
        padding: 0.25em 0.5em 0.25em 0.5em;
        white-space: pre-wrap;       /* css-3 */
        white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
        white-space: -pre-wrap;      /* Opera 4-6 */
        white-space: -o-pre-wrap;    /* Opera 7 */
        word-wrap: break-word;    
    }
    
    pre {
        background-color: #027c7c;
        padding-left: 0.5em;
    }
</style>"""


def _read_notebook_file(filename: str) -> Dict[str, Any]:
    """노트북 파일을 읽어서 JSON으로 파싱합니다."""
    try:
        with codecs.open(filename, "r") as f:
            source = f.read()
    except UnicodeDecodeError:
        with codecs.open(filename, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        raise Exception(f"파일 변환에 실패했습니다. 에러 메시지: {str(e)}")

    return json.loads(source)


def _process_code_output(output: Dict[str, Any], cells: List[str]) -> None:
    """코드 셀의 출력을 처리합니다."""
    if "data" in output:
        outputs_data = output["data"]
        for key, value in outputs_data.items():
            if key == "text/html":
                v = [v_.replace("\n", "") for v_ in value]
                cells.extend(v)
                cells.append("\n")
                break
            elif key == "text/plain":
                v = [v_.replace("\n", "") for v_ in value]
                v.insert(0, '<pre class="custom">')
                v.append("</pre>")
                cells.extend(v)
                cells.append("\n\n")
                break
            elif key == "image/png":
                plain_image = '<img src="data:image/png;base64,{}"/>\n'.format(
                    value.replace("\n", "")
                )

                cells.append(plain_image)
                cells.append("\n\n")
                break
    elif output.get("output_type") == "stream":
        v = output["text"]
        v.insert(0, '<pre class="custom">')
        v.append("</pre>\n\n")
        cells.extend(v)


def _process_code_cell(cell: Dict[str, Any], cells: List[str]) -> None:
    """코드 셀을 처리합니다."""
    work_flag = True

    if "source" in cell:
        cells.append("\n```python\n")
        cells.extend(cell["source"])
        cells.append("\n```\n")
        work_flag = False

    outputs = cell["outputs"]
    if outputs:
        for output in outputs:
            _process_code_output(output, cells)
    elif work_flag:
        cells.append("\n```python")
        code = [c.replace("\n", "") for c in cell["source"]]
        cells.extend(code)
        cells.append("```\n\n")


def _convert_markdown_from_notebook(filename: str, output_filename: str) -> str:
    """노트북을 마크다운으로 변환합니다."""
    notebook = _read_notebook_file(filename)
    cells: List[str] = []

    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            _process_code_cell(cell, cells)
        elif cell["cell_type"] == "markdown":
            cells.extend(cell["source"])
            cells.append("\n")

    final_output = f"{get_default_css()}\n\n{''.join(cells)}"

    with open(output_filename, "w") as f:
        f.write(final_output)

    return output_filename


def convert_markdown_from_notebook(
    filename: str, post_fix: str = "-(NEED-REVIEW)"
) -> str:
    """노트북 파일을 마크다운으로 변환하는 메인 함수입니다."""

    output_filename = filename.replace(".ipynb", f"{post_fix}.md")

    return _convert_markdown_from_notebook(filename, output_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="주피터 노트북을 마크다운으로 변환합니다."
    )
    parser.add_argument(
        "--filename", required=True, help="변환할 주피터 노트북 파일 경로"
    )
    args = parser.parse_args()

    convert_markdown_from_notebook(args.filename)
