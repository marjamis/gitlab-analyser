import click
import outputs.csv_processing as csv_processing
import engine.get as get

from outputs import html as html_output


def generate_input_data():
    get.workflow(
        "./data/data.pickle",
    )


@click.command()
@click.option("--generate-data", default=True, show_default=True, help="Generate new data instead of using saved data")
@click.option("--output", type=click.Choice(["html", "csv"]), default="html", show_default=True, help="Type of output")
def cli(generate_data, output):
    if generate_data:
        generate_input_data()

    if output == "html":
        output_html()
    elif output == "csv":
        output_csv()


def output_html():
    html_output.html_report(jupyter_notebook_location="./jupyter-notebooks/analysis.ipynb")


def output_csv():
    csv_processing.create_csv_outputs(
        "./data/data.pickle",
        branches_csv="./data/branches.csv",
        pipeline_schedules_csv="./data/schedules.csv",
        projects_csv="./data/projects.csv",
    )


if __name__ == "__main__":
    cli()
