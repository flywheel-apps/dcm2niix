"""Function to execute setup for dcm2niix."""

import glob
import logging
import os

import pydicom

from fw_gear_dcm2niix.dcm2niix import arrange, dcm2niix_utils

log = logging.getLogger(__name__)


def setup(infile, rec_infile, work_dir, remove_incomplete_volumes, decompress_dicoms):
    """Prepare dcm2niix input, remove incomplete volumes, and decompress dicom files."""
    log.info("Prepare dcm2niix input.")
    dcm2niix_input_dir = arrange.prepare_dcm2niix_input(infile, rec_infile, work_dir)

    if remove_incomplete_volumes:
        log.info("Remove incomplete volumes.")
        dicom_file = glob.glob(dcm2niix_input_dir + "/*")[0]

        try:
            pydicom.filereader.dcmread(dicom_file, force=True)
        except pydicom.errors.InvalidDicomError:
            log.info(
                (
                    "Unable to run incomplete volume correction. "
                    "Input archive does not contain dicoms. Exiting."
                )
            )
            os.sys.exit(1)

        dcm2niix_utils.remove_incomplete_volumes(dcm2niix_input_dir)

    if decompress_dicoms:
        log.info("Decompress dicom files.")
        dcm2niix_utils.decompress_dicoms(dcm2niix_input_dir)

    return dcm2niix_input_dir
