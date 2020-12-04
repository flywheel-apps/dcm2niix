"""Functions to resolve dcm2niix gear outputs."""

import glob
import logging
import os
import re
import shutil

from utils import metadata


log = logging.getLogger(__name__)


def setup(
    output_image_files,
    work_dir,
    dcm2niix_input_dir,
    output_dir,
    ignore_errors=False,
    retain_sidecar=True,
    retain_nifti=True,
    output_nrrd=False,
    pydeface_intermediaries=False,
    classification=None,
    modality=None,
):
    """Orchestrate resolution of gear, including metadata capture and file retention.

    Args:
        output_image_files (list): The absolute paths to gear image files to resolve.
            Typically these are NIfTI files, but can be the two files constituting the
            NRRD format (i.e., ".raw" and ".nhdr").
        work_dir (str): The absolute path to the output directory of dcm2niix and where
            the metadata file generated is written to.
        dcm2niix_input_dir (str): The absolute path to the input directory to dcm2niix.
        retain_sidecar (bool): If true, sidecar is retained in final output.
        retain_nifti (bool): If true, NIfTI is retained in final output.
        output_nrrd (bool): If true, export as NRRD instead of NIfTI.
        pydeface_intermediaries (bool): If true, PyDeface intermediary files are
            retained. The files created when --nocleanup flag is applied to the
            PyDeface command.
        classification (dict): File classification, typically from gear config.
        modality (str): File modality, typically from gear config.

    Returns:
        None

    """
    # Ignoring errors configuration option; move all files from work_dir to output_dir
    if ignore_errors is True:
        log.warning(
            "Expert Option (ignore_errors). "
            "We trust that since you have selected this option "
            "you know what you are asking for. "
            "Continuing."
        )
        if output_image_files is not None:
            # Capture metadata
            metadata_file = metadata.generate(
                output_image_files,
                work_dir,
                dcm2niix_input_dir,
                retain_sidecar=True,
                retain_nifti=True,
                output_nrrd=False,
                pydeface_intermediaries=pydeface_intermediaries,
                classification=classification,
                modality=modality,
            )

        work_dir_contents = glob.glob(work_dir + "/*")
        for item in work_dir_contents:
            if not os.path.isdir(item):
                shutil.move(item, output_dir)
                log.info(f"Moving {item} to output directory for upload to Flywheel.")

    else:

        # Capture metadata
        metadata_file = metadata.generate(
            output_image_files,
            work_dir,
            dcm2niix_input_dir,
            retain_sidecar=retain_sidecar,
            retain_nifti=retain_nifti,
            output_nrrd=output_nrrd,
            pydeface_intermediaries=pydeface_intermediaries,
            classification=classification,
            modality=modality,
        )

        # Retain gear outputs
        retain_gear_outputs(
            output_image_files,
            metadata_file,
            work_dir,
            output_dir,
            retain_sidecar=retain_sidecar,
            retain_nifti=retain_nifti,
            output_nrrd=output_nrrd,
            pydeface_intermediaries=pydeface_intermediaries,
        )


def retain_gear_outputs(
    output_image_files,
    metadata_file,
    work_dir,
    output_dir,
    retain_sidecar=True,
    retain_nifti=True,
    output_nrrd=False,
    pydeface_intermediaries=False,
):
    """Move selected gear outputs to the output directory.

    Args:
        output_image_files (list): The absolute paths to gear image files to resolve.
            Typically these are NIfTI files, but can be the two files constituting the
            NRRD format (i.e., ".raw" and ".nhdr").
        metadata_file (str): The absolute path to the metadata file.
        work_dir (str): The absolute path to the output directory of dcm2niix and
            where the generated metadata file is.
        output_dir (str): The absolute path to the gear output directory.
        retain_sidecar (bool): If true, sidecar is retained in final output.
        retain_nifti (bool): If true, NIfTI is retained in final output.
        output_nrrd (bool): If true, export as NRRD instead of NIfTI.
        pydeface_intermediaries (bool): If true, pydeface intermediary files are
            retained. The files created when --nocleanup flag is applied to the
            pydeface command.

    Returns:
        None

    """
    log.info("Resolving gear outputs.")

    if retain_nifti == output_nrrd:
        log.critical(
            "Function arguments retain_nifti and output_nrrd are exclusive. Gear config logic is broken. Exiting."
        )
        os.sys.exit(1)

    # fmt: off

    for file in output_image_files:

        # Move bids json sidecar file, if indicated
        # If NRRD format, two files per sidecar - move sidecar once
        if retain_sidecar and not file.endswith(".nhdr"):
            bids_sidecar = os.path.join(
                                        work_dir, re.sub(
                                                         r"(\.nii\.gz|\.nii|.nhdr|\.raw\.gz|\.nrrd)",
                                                         ".json",
                                                         os.path.basename(file))
            )

            shutil.move(bids_sidecar, output_dir)
            log.info(f"Moving {bids_sidecar} to output directory.")

        # Move niftis and associated files (.bval, .bvec, .mat), if indicated
        if retain_nifti and not output_nrrd:

            # Move bval file, if exists
            bval = os.path.join(
                                work_dir, re.sub(
                                                 r"(\.nii\.gz|\.nii)",
                                                 ".bval",
                                                 os.path.basename(file))
            )

            if os.path.isfile(bval):
                shutil.move(bval, output_dir)
                log.info(f"Moving {bval} to output directory.")

            # Move bvec file, if exists
            bvec = os.path.join(
                                work_dir, re.sub(
                                                 r"(\.nii\.gz|\.nii)",
                                                 ".bvec",
                                                 os.path.basename(file))
            )

            if os.path.isfile(bvec):
                shutil.move(bvec, output_dir)
                log.info(f"Moving {bvec} to output directory.")

            # Move pydeface intermediary files, if exists
            if pydeface_intermediaries:

                # The output mask of PyDeface is a compressed nifti, even if .nii input
                pydeface_mask = os.path.join(
                                             work_dir, re.sub(
                                                              r"(\.nii\.gz|\.nii)",
                                                              "_pydeface_mask.nii.gz",
                                                              os.path.basename(file))
                )

                if os.path.isfile(pydeface_mask):
                    shutil.move(pydeface_mask, output_dir)
                    log.info(f"Moving {pydeface_mask} to output directory.")

                pydeface_matlab = os.path.join(
                                               work_dir, re.sub(
                                                                r"(\.nii\.gz|\.nii)",
                                                                "_pydeface.mat",
                                                                os.path.basename(file))
                )

                if os.path.isfile(pydeface_matlab):
                    shutil.move(pydeface_matlab, output_dir)
                    log.info(f"Moving {pydeface_matlab} to output directory.")

            # Move nifti file
            shutil.move(file, output_dir)
            log.info(f"Moving {file} to output directory.")

        # Move nrrd files
        if output_nrrd and not retain_nifti:
            shutil.move(file, output_dir)
            log.info(f"Moving {file} to output directory.")

    # Move metadata file
    shutil.move(metadata_file, output_dir)
    log.info(f"Moving {metadata_file} to output directory.")

    # fmt: on
    log.info("Gear outputs resolved.")
