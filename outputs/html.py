import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors.execute import ExecutePreprocessor


def html_report(jupyter_notebook_location: str):
    """Generates a html file based on the provided Jupyter notebook.

    Args:
        jupyter_notebook_location (str): "File location of the Jupyter notebook to be used"
    """
    with open(jupyter_notebook_location) as file:
        notebook = nbformat.read(file, as_version=4)

    processor = ExecutePreprocessor(timeout=600, kernel_name="python3")
    processor.preprocess(notebook, {"metadata": {"path": "./"}})

    html_exporter = HTMLExporter(template_name="classic")
    html_exporter.exclude_input = True
    html_exporter.exclude_output_prompt = True

    (body, resources) = html_exporter.from_notebook_node(notebook)

    with open("./data/output.html", "w", encoding="utf-8") as file:
        file.write(body)
