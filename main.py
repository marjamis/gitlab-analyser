import engine.process as process
import engine.get as get

get.get_data(
    "./data/data.pickle",
)
process.create_csv_output(
    "./data/data.pickle",
    "./data/output.csv",
)
