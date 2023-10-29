import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors.execute import ExecutePreprocessor

from nbparameterise import extract_parameters, replace_definitions, parameter_values


# TODO convert to pick over csv at some point?
def html_report(jupyter_notebook_location: str, input_csv_directory: str, output_html_location: str):
    """Generates a html file based on the provided Jupyter notebook and saves it.

    Args:
        jupyter_notebook_location (str): "File location of the Jupyter notebook to be used"
        output_html_location (str): "File location to save the html output"
    """
    with open(jupyter_notebook_location, "r", encoding="utf-8") as file:
        notebook = nbformat.read(file, as_version=4)

    orig_parameters = extract_parameters(notebook)
    params = parameter_values(orig_parameters, csv_directory=input_csv_directory)
    new_notebook = replace_definitions(notebook, params)

    processor = ExecutePreprocessor(timeout=600, kernel_name="python3")
    processor.preprocess(new_notebook, {"metadata": {"path": "./"}})

    html_exporter = HTMLExporter(template_name="classic")
    html_exporter.exclude_input = True
    html_exporter.exclude_output_prompt = True

    (body, _) = html_exporter.from_notebook_node(new_notebook)

    with open(output_html_location, "w", encoding="utf-8") as file:
        file.write(body)
