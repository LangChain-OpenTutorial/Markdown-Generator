import os
import re
import shutil
from .mdconverter import get_default_css
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import Preprocessor
import nbformat
import matplotlib.pyplot as plt


class Ndconverter:
    """Base class for converting Jupyter Notebook (.ipynb) files to Markdown (.md) format"""

    def __init__(
        self,
        css_filename: str = "css/styles.css",
        post_fix: str = "-(NEW)",
    ) -> None:
        """
        Initialize Ndconverter class

        Args:
            css_filename: Path to the CSS file to add to the Markdown header
            post_fix: Suffix to add to the output Markdown file name
        """
        self.css_filename = css_filename
        self.filename = ""
        self.post_fix = post_fix
        self.notebook_content = None
        self.script = ""
        self.resources = None
        self.ndconverter_script = ""

    def run(self, save_on: bool = True) -> None:
        """Run the process to convert the notebook to Markdown"""
        print("<!----Start---->")
        self.run_ndconverter(save_on=save_on)
        print("<!----End---->")

    def run_ndconverter(self, save_on: bool) -> None:
        """
        Execute the full conversion process, including loading the notebook,
        exporting it to Markdown, and saving the result.

        :param save_on: Whether to save the converted Markdown file to disk.
        """
        self._load_ipynb()  # make notebook_content
        self._markdown_exporter()  # make script, resources
        self.ndconverter_script = self._add_prefix_css()
        self._replace_pre_tag()
        if save_on:
            self._save_script()

    def _load_ipynb(self) -> None:
        """Load the Jupyter Notebook content from the specified file."""
        print(f"Loading file : {self.filename}")
        with open(self.filename, "r", encoding="utf-8") as f:
            self.notebook_content = nbformat.read(f, as_version=4)

    def _markdown_exporter(self) -> None:
        """Convert notebook content to Markdown format"""
        exporter = MarkdownExporter()
        self.script, self.resources = exporter.from_notebook_node(self.notebook_content)

    def _add_prefix_css(self) -> str:
        """Add CSS content to the beginning of the Markdown script"""
        return f"{get_default_css(self.css_filename)}\n\n{self.script}"

    def _replace_pre_tag(self) -> None:
        formatted_text = self.ndconverter_script.replace(
            '    <pre class="custom">', '<pre class="custom">'
        )
        self.ndconverter_script = formatted_text.replace("    </pre>", "</pre>")

    def _save_script(self) -> None:
        """Save the converted script"""
        output_filename = os.path.join(
            "./docs", self.filename.replace(".ipynb", f"{self.post_fix}.md")
        )
        print(f"Saving file : {output_filename}")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(self.ndconverter_script)


class CustomPreprocessor(Preprocessor):
    """Override preprocess_cell"""

    def preprocess_cell(self, cell, resources, index):
        if cell.get("cell_type", "") == "markdown":
            # markdown
            pass
        elif cell.get("cell_type", "") == "code":
            # code
            cell = self._process_text_plain_output(cell)
            cell = self._process_stream_output(cell)
        return cell, resources

    def _process_stream_output(self, cell):
        """Process stream output by wrapping it in custom HTML tags"""
        try:
            if cell["outputs"][0]["output_type"] == "stream":
                stream_text = "".join(cell["outputs"][0]["text"])
                formatted_output = f"""<pre class="custom">{stream_text}</pre>"""
                cell["outputs"][0]["text"] = formatted_output.strip()

            return cell

        except:
            return cell

    def _process_text_plain_output(self, cell):
        """Process text/plain output by wrapping it in custom HTML tags"""
        try:
            output_text = "".join(cell["outputs"][0]["data"]["text/plain"])
            formatted_output = f"""<pre class="custom">{output_text}</pre>"""
            cell["outputs"][0]["data"]["text/plain"] = formatted_output.strip()
            return cell

        except:
            return cell


class CustomMdconverter(Ndconverter):
    """Custom Markdown converter"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.img_dir = ""

    def _markdown_exporter(self) -> None:
        """Convert to Markdown and handle images"""
        exporter = MarkdownExporter()
        exporter.register_preprocessor(CustomPreprocessor, enabled=True)
        exporter.exclude_input_prompt = True  # exclude "In[0]:"
        exporter.exclude_output_prompt = True  # exclude "Out[0]:"

        self.script, self.resources = exporter.from_notebook_node(self.notebook_content)
        self._setup_image_processing()

    def _setup_image_processing(self) -> None:
        """Set up image processing"""
        self._extracting_img_path()
        if self.resources.get("outputs"):
            self._process_output_images()
        self._process_markdown_images_pattern()

    def _extracting_img_path(self) -> None:
        """Set image directory path"""
        folder_name = os.path.dirname(self.filename)
        self.img_dir = os.path.join("./docs", folder_name, "img")
        os.makedirs(self.img_dir, exist_ok=True)
        print(f"Making image dir : {self.img_dir}")

    def _process_output_images(self) -> None:
        """Save image files and update paths"""
        for img_filename, image_data in self.resources["outputs"].items():
            img_path = os.path.join(self.img_dir, img_filename)
            self._save_image(img_path, image_data)
            self._update_image_path(img_filename, f"./img/{img_filename}")

    def _save_image(self, img_path: str, image_data: bytes) -> None:
        """Save image file"""
        print(f"Saving image : {img_path}")
        with open(img_path, "wb") as f:
            f.write(image_data)

    def _update_image_path(self, img_filename: str, img_path: str) -> None:
        """Update image path in Markdown"""
        img_type = self._get_image_type(img_filename)
        if img_type:
            old_pattern = f"![{img_type}]({img_filename})"
            new_pattern = f"![{img_type}]({img_path})"
            self.script = self.script.replace(old_pattern, new_pattern)
        print(f"Update path of imags : {img_filename} -> {img_path}")

    @staticmethod
    def _get_image_type(filename: str) -> str:
        """Check image type"""
        if filename.endswith((".jpg", ".jpeg")):
            return "jpeg"
        elif filename.endswith(".png"):
            return "png"
        return ""

    def _process_markdown_images_pattern(self) -> None:
        """Handle Markdown image patterns"""
        pattern = r"!\[([^\]]+)\]\((\.\/assets\/[^)]+)\)"
        for match in re.finditer(pattern, self.script):
            desc, old_path = match.groups()
            self._process_markdown_image(desc, old_path)

    def _process_markdown_image(self, desc: str, old_path: str) -> None:
        """Handle individual Markdown image"""
        filename = os.path.basename(old_path)
        new_path = f"{self.img_dir}/{filename}"
        abs_old_path = self._get_absolute_path(old_path)

        if os.path.exists(abs_old_path):
            shutil.copy2(abs_old_path, new_path)
            self._update_markdown_image_path(desc, old_path, f"./img/{filename}")

    def _get_absolute_path(self, old_path: str) -> str:
        """Convert relative path to absolute path"""
        return os.path.abspath(
            os.path.join(os.path.dirname(self.filename), old_path.lstrip("./"))
        )

    def _update_markdown_image_path(
        self, desc: str, old_path: str, new_path: str
    ) -> None:
        """Update image path in Markdown"""
        old_pattern = f"![{desc}]({old_path})"
        new_pattern = f"![{desc}]({new_path})"
        self.script = self.script.replace(old_pattern, new_pattern)
        print(f"In Markdown docs, image path : {old_path} -> {new_path}")


class MultiNdconverter(CustomMdconverter):
    """Multi-file converter"""

    def __init__(self, filenames: list) -> None:
        super().__init__()
        self.filenames = filenames
        self.static = self._init_static_dict(
            keys=["python_counts", "markdown_counts", "code_counts", "total_counts"]
        )

    def _init_static_dict(self, keys: list[str]) -> dict:
        """Initialize a dictionary with given keys and empty dictionaries as values."""
        return {key: {} for key in keys}

    def add_file(self, filename: str) -> None:
        """Add file to convert"""
        self.filenames.append(filename)

    def run(self, save_on: bool = True) -> None:
        """Run conversion for all files"""
        for filename in self.filenames:
            self.filename = filename
            super().run(save_on)

    def cal_static(self) -> None:
        for filename in self.filenames:
            self.filename = filename
            super()._load_ipynb()  # self.notebook_content

            python_version = self.notebook_content["metadata"]["language_info"][
                "version"
            ]
            markdown_count = sum(
                1
                for cell in self.notebook_content["cells"]
                if cell["cell_type"] == "markdown"
            )
            code_count = sum(
                1
                for cell in self.notebook_content["cells"]
                if cell["cell_type"] == "code"
            )
            total_count = markdown_count + code_count

            self._increment_count(python_version, self.static["python_counts"])
            self._increment_count(markdown_count, self.static["markdown_counts"])
            self._increment_count(code_count, self.static["code_counts"])
            self._increment_count(total_count, self.static["total_counts"])

    @staticmethod
    def _increment_count(key: str, count_dict: dict) -> None:
        """Increment count for a key in the given dictionary."""
        count_dict[str(key)] = count_dict.get(str(key), 0) + 1

    def plot_static_data(self, category: str) -> None:
        if category not in self.static:
            print(f"Category '{category}' not found in data.")
            return

        counts = self.static[category]
        keys = list(counts.keys())
        values = list(map(int, counts.values()))

        # Plot the data
        plt.figure(figsize=(10, 6))
        plt.bar(keys, values)

        # Customize the chart
        plt.title(f"Counts for {category}")
        plt.xlabel("Keys")
        plt.ylabel("Counts")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        # Show the chart
        plt.tight_layout()
        plt.show()
