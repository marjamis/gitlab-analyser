import engine.process as process
import engine.get as get

get.get_data(
    "./data/data.pickle",
)

process.create_csv_outputs(
    "./data/data.pickle",
    branches_csv="./data/output.csv",
    pipeline_schedules_csv="./data/schedules.csv",
)
