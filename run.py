#!/usr/bin/env python3
"""Main script for dcm2niix gear."""

import logging
import os

import flywheel_gear_toolkit

from dcm2niix import prepare
from dcm2niix import dcm2niix_utils
from dcm2niix import dcm2niix_run
from pydeface import pydeface_run
from utils import parse_config
from utils import resolve


FORMAT = "[%(asctime)s - %(levelname)s - %(name)s:%(lineno)d] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%d")
log = logging.getLogger()


def main(gear_context):
    """Orchestrate dcm2niix gear."""

    # Prepare dcm2niix input, which is a directory of dicom or parrec images
    gear_args = parse_config.generate_gear_args(gear_context, "prepare")
    dcm2niix_input_dir = prepare.setup(**gear_args)

    # Run dcm2niix
    gear_args = parse_config.generate_gear_args(gear_context, "dcm2niix")
    output = dcm2niix_run.convert_directory(
        dcm2niix_input_dir, gear_context.work_dir, **gear_args
    )

    # Nipype interface output from dcm2niix can be a string or list (desired)
    if output is not None:
        nifti_files = output.outputs.converted_files

        if isinstance(nifti_files, str):
            nifti_files = [nifti_files]
    else:
        nifti_files = None

    if not isinstance(nifti_files, list):
        if not gear_context.config["ignore_errors"]:
            log.error("NIfTIs not produced from dcm2niix conversion. Exiting.")
            os.sys.exit(1)
        else:
            log.warning(
                "NIfTIs not produced from dcm2niix conversion."
                "Expert Option (ignore_errors). "
                "We trust that since you have selected this option "
                "you know what you are asking for. "
                "Continuing."
            )
            nifti_files = None

    # Apply coil combined method
    if gear_context.config["coil_combine"]:
        dcm2niix_utils.coil_combine(nifti_files)

    # Run pydeface
    if gear_context.config["pydeface"]:
        gear_args = parse_config.generate_gear_args(gear_context, "pydeface")
        pydeface_run.deface_multiple_niftis(nifti_files, **gear_args)

    # Resolve gear outputs, including metadata capture
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

    with flywheel_gear_toolkit.GearToolkitContext() as gear_context:
        log = gear_context.log
        exit_status = main(gear_context)

    log.info(f"Successful dcm2niix gear execution with exit status {exit_status}.")
