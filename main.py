import engine.csv_processing as csv_processing
import engine.get as get

get.workflow(
    "./data/data.pickle",
)

csv_processing.create_csv_outputs(
    "./data/data.pickle",
    branches_csv="./data/output.csv",
    pipeline_schedules_csv="./data/schedules.csv",
)
