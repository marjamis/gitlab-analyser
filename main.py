import click
import os
import outputs.csv_processing as csv_processing
import engine.get as get

from outputs import html as html_output


def generate_input_data(output_directory: str):
    get.workflow(
        output_pickle_filename=os.path.join(output_directory, "gitlab-analyser.pickle"),
    )


@click.command()
@click.option("--generate-data", default=True, show_default=True, help="Generate new data instead of using saved data")
@click.option(
    "--output-format", type=click.Choice(["html", "csv"]), default="html", show_default=True, help="Type of output"
)
@click.option("--output-directory", type=str, default=".", show_default=True, help="Output location")
def cli(generate_data, output_format, output_directory):
    if generate_data:
        generate_input_data(output_directory=output_directory)

    if output_format == "html":
        output_html(output_directory=output_directory)
    elif output_format == "csv":
        output_csv(output_directory=output_directory)


def output_html(output_directory: str):
    # TODO this is temporarily required to ensure there is csv data for the html render
    output_csv(output_directory)

    html_output.html_report(
        jupyter_notebook_location="./jupyter-notebooks/analysis.ipynb",
        input_csv_directory=os.path.join(output_directory),
        output_html_location=os.path.join(output_directory, "output.html"),
    )


def output_csv(output_directory: str):
    csv_processing.create_csv_outputs(
        input_pickle_file=os.path.join(output_directory, "gitlab-analyser.pickle"),
        output_directory=output_directory,
    )


if __name__ == "__main__":
    cli()
