"""Run two versions of the dcm2niix Gear on the same inputs and capture resulting job information."""

versions = ["1.0.0_1.0.20200331", "1.2.0_1.0.20201102_dev3"]
output_dir = "~/Documents/flywheel/gears/dcm2niix/tests/instance"

import time
import datetime
import flywheel
import pandas as pd

fw = flywheel.Client()


def main():

    # Find the collection
    collection = fw.collections.find_one(f"label=dcm2niix_rewrite_test")

    # Find all the acquisitions in the collection
    acquisitions = fw.get_collection_acquisitions(collection.id)

    # For each version, run the gear with default config and save the job information
    for version in versions:

        job_ids = run_dcm2niix_gear(acquisitions, version)
        # wait for the jobs to finish
        time.sleep(400)
        df = collate_job_info(job_ids, version)

        df.reset_index(inplace=True)
        df.rename(columns={"index": "job_id"}, inplace=True)
        date = str(datetime.date.today())
        outfile = f"{output_dir}/dcm2niix_instance_runs_{version}_{date}.csv"
        df.to_csv(outfile, index=False)


def collate_job_info(job_ids, gear_version):

    df = pd.DataFrame()

    for job_id in job_ids:

        job = fw.get_job(job_id)

        # Save job information
        df.loc[job_id, "gear_version"] = gear_version
        df.loc[job_id, "state"] = job.state
        df.loc[job_id, "inputs"] = job.inputs["dcm2niix_input"]["name"]
        df.loc[job_id, "destination_id"] = job.destination["id"]

        # Default behavior of original gear is to not save JSON sidecars
        outputs = [file for file in job.saved_files if not file.endswith(".json")]
        df.loc[job_id, "outputs"] = str(outputs)

        # Calculate time to execute job
        if job.state == "complete":
            timedelta = job.transitions["complete"] - job.transitions["running"]
            df.loc[job_id, "execution_time"] = timedelta.total_seconds()

    return df


def run_dcm2niix_gear(acquisitions, gear_version):

    gear = fw.lookup(f"gears/dcm2niix/{gear_version}")
    job_ids = []

    for acquisition in acquisitions:

        for file in acquisition.get_files():

            if file.type == "dicom":

                inputs = {"dcm2niix_input": acquisition.get_file(file.name)}

                job_id = gear.run(
                    inputs=inputs,
                    destination=acquisition,
                    tags=["dcm2niix_rewrite_test"],
                )
                job_ids.append(job_id)

    return job_ids


main()
