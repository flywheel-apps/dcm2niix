#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main script for dcm2niix gear."""
# MAIN: cleanse and collate logic on ignore errors and empty image output scenarios

import os

import flywheel_gear_toolkit

from dcm2niix import prepare
from dcm2niix import dcm2niix_utils
from dcm2niix import dcm2niix_run
from pydeface import pydeface_run
from utils import parse_config
from utils import resolve


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
        output_image_files = output.outputs.converted_files

        if isinstance(output_image_files, str):
            output_image_files = [output_image_files]
    else:
        output_image_files = None

    if not isinstance(output_image_files, list):
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
            output_image_files = None

    # NIfTI files are assumed to be expected for coil combined and pydeface
    if not gear_context.config["output_nrrd"]:

        # Apply coil combined method
        if gear_context.config["coil_combine"]:
            dcm2niix_utils.coil_combine(output_image_files)

        # Run pydeface
        if gear_context.config["pydeface"]:
            gear_args = parse_config.generate_gear_args(gear_context, "pydeface")
            pydeface_run.deface_multiple_niftis(output_image_files, **gear_args)

    # Resolve gear outputs, including metadata capture
    gear_args = parse_config.generate_gear_args(gear_context, "resolve")
    resolve.setup(
        output_image_files,
        gear_context.work_dir,
        dcm2niix_input_dir,
        gear_context.output_dir,
        **gear_args,
    )

    exit_status = 0

    return exit_status


if __name__ == "__main__":

    with flywheel_gear_toolkit.GearToolkitContext() as gear_context:
        gear_context.init_logging()
        log = gear_context.log
        exit_status = main(gear_context)

    log.info(f"Successful dcm2niix gear execution with exit status {exit_status}.")
