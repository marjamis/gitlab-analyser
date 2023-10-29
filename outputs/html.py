import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors.execute import ExecutePreprocessor


def html_report(jupyter_notebook_location: str, output_html_location: str):
    """Generates a html file based on the provided Jupyter notebook and saves it.

    Args:
        jupyter_notebook_location (str): "File location of the Jupyter notebook to be used"
        output_html_location (str): "File location to save the html output"
    """
    with open(jupyter_notebook_location, "r", encoding="utf-8") as file:
        notebook = nbformat.read(file, as_version=4)

    processor = ExecutePreprocessor(timeout=600, kernel_name="python3")
    processor.preprocess(notebook, {"metadata": {"path": "./"}})

    html_exporter = HTMLExporter(template_name="classic")
    html_exporter.exclude_input = True
    html_exporter.exclude_output_prompt = True

    (body, _) = html_exporter.from_notebook_node(notebook)

    with open(output_html_location, "w", encoding="utf-8") as file:
        file.write(body)
