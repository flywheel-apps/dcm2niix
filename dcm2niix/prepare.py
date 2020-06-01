import glob
import logging
import os

import pydicom

from dcm2niix import arrange
from dcm2niix import dcm2niix_utils


log = logging.getLogger(__name__)


def setup(infile, rec_infile, work_dir, remove_incomplete_volumes, decompress_dicoms):

    # prepare dcm2niix input from compressed archive
    dcm2niix_input_dir = arrange.prepare_dcm2niix_input(infile, rec_infile, work_dir)

    # remove incomplete volumes
    if remove_incomplete_volumes:
        dicom_file = glob.glob(dcm2niix_input_dir + "/*")[0]

        try:
            pydicom.filereader.dcmread(dicom_file)
        except pydicom.errors.InvalidDicomError:
            log.info(
                (
                    "Unable to run incomplete volume correction. "
                    "Input archive does not contain dicoms. Exiting."
                )
            )
            os.sys.exit(1)

        dcm2niix_utils.remove_incomplete_volumes(dcm2niix_input_dir)

    # decompress dicom files
    if decompress_dicoms:
        dcm2niix_utils.decompress_dicoms(dcm2niix_input_dir)

    return dcm2niix_input_dir
