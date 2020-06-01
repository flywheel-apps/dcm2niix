#!/usr/bin/env python3

import logging

import flywheel

from dcm2niix import prepare, dcm2niix_utils, dcm2niix_run
from pydeface import pydeface_run
from utils import parse_config, resolve


# FIX: logging standard?
logfile = "/flywheel/v0/output/logfile.log"
FORMAT = "[%(asctime)s - %(levelname)s - %(name)s:%(lineno)d] %(message)s"
dateformat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(
    filename=logfile, level=logging.INFO, format=FORMAT, datefmt=dateformat
)
log = logging.getLogger()


def main(gear_context):

    gear_context = flywheel.GearContext()

    # prepare dcm2niix input, which is a directory of dicom or parrec images
    gear_args = parse_config.generate_gear_args(gear_context, "prepare")
    dcm2niix_input_dir = prepare.setup(**gear_args)

    # run dcm2niix
    gear_args = parse_config.generate_gear_args(gear_context, "dcm2niix")
    output = dcm2niix_run.convert_directory(
        dcm2niix_input_dir, gear_context.work_dir, **gear_args
    )

    # nipype interface output from dcm2niix can be a string or list > standardize to list
    if output is not None:
        nifti_files = output.outputs.converted_files

        if isinstance(nifti_files, str):
            nifti_files = [nifti_files]
    else:
        nifti_files = None

    # apply coil combined method
    if gear_context.config["coil_combine"]:
        dcm2niix_utils.coil_combine(nifti_files)

    # run pydeface
    if gear_context.config["pydeface"]:
        gear_args = parse_config.generate_gear_args(gear_context, "pydeface")
        pydeface_run.deface_multiple_niftis(nifti_files, **gear_args)

    # resolve gear outputs, including metadata capture
    gear_args = parse_config.generate_gear_args(gear_context, "resolve")
    resolve.setup(
        nifti_files,
        gear_context.work_dir,
        dcm2niix_input_dir,
        gear_context.output_dir,
        **gear_args,
    )

    exit_status = 0

    return exit_status


if __name__ == "__main__":

    with flywheel.GearContext() as gear_context:
        exit_status = main(gear_context)

    log.info(f"Successful gear execution with exit status = {exit_status}")
