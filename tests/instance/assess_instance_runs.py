import datetime

import flywheel
import pandas as pd

versions = ["1.0.0_1.0.20200331", "1.1.0_1.0.20201102_dev1"]


input_dir = "~/Documents/flywheel/gears/dcm2niix/tests/instance"
date = str(datetime.date.today())

previous = pd.read_csv(f"{input_dir}/dcm2niix_instance_runs_{versions[0]}_{date}.csv")
updated = pd.read_csv(f"{input_dir}/dcm2niix_instance_runs_{versions[1]}_{date}.csv")

# Remove where inputs, outputs, and job status are equivalent
equivalent = previous.merge(
    updated, how="inner", on=["inputs", "destination_id", "state", "outputs"]
)
previous = previous.loc[~previous["job_id"].isin(equivalent["job_id_x"].to_list())]
updated = updated.loc[~updated["job_id"].isin(equivalent["job_id_y"].to_list())]


compare = previous.merge(updated, how="left", on=["inputs", "destination_id"])
compare = compare[
    ["job_id_x", "job_id_y", "state_x", "state_y", "outputs_x", "outputs_y"]
]


fw = flywheel.Client()

job_id = ""
job_logs = fw.get_job_logs(job_id)
with open("logfile.txt", "w") as logfile:
    for log in job_logs["logs"]:
        logfile.write(log["msg"].rstrip())
