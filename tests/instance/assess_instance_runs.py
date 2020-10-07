import flywheel
import pandas as pd


input_dir = "~/Documents/flywheel/gears/dcm2niix/tests/instance"

original = pd.read_csv(
    f"{input_dir}/dcm2niix_instance_runs_0.9.0_1.0.20190902.rc2_2020-09-30.csv"
)
rewrite = pd.read_csv(
    f"{input_dir}/dcm2niix_rewrite_test_1.0.0_1.0.20200331_2020-09-30.csv"
)

# Remove where inputs, outputs, and job status are equivalent
equivalent = original.merge(
    rewrite, how="inner", on=["inputs", "destination_id", "state", "outputs"]
)
original = original.loc[~original["job_id"].isin(equivalent["job_id_x"].to_list())]
rewrite = rewrite.loc[~rewrite["job_id"].isin(equivalent["job_id_y"].to_list())]


compare = original.merge(rewrite, how="left", on=["inputs", "destination_id"])
compare = compare[
    ["job_id_x", "job_id_y", "state_x", "state_y", "outputs_x", "outputs_y"]
]


fw = flywheel.Client()


job_id = ""
job_logs = fw.get_job_logs(job_id)
with open("logfile.txt", "w") as logfile:
    for log in job_logs["logs"]:
        logfile.write(log["msg"].rstrip())
