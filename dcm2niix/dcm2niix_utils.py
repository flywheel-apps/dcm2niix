"""Utility functions for pre and post dcm2niix execution."""

import glob
import logging
import os
import shutil
import subprocess

import nibabel as nb


log = logging.getLogger(__name__)


def remove_incomplete_volumes(dcm2niix_input_dir):
    """Implement the incomplete volume correction by removal of dicom files.

    Args:
        dcm2niix_input_dir (str): The absolute path to a set of dicoms.

    Returns:
        None; removes dicoms from dcm2niix_input_dir.

    """
    n_dicom_files = len(glob.glob(dcm2niix_input_dir + "/*"))
    log.info(
        f"Running incomplete volume correction. {n_dicom_files} dicom files found."
    )
    script = f"{os.getenv('FLYWHEEL')}/fix_dcm_vols.py"
    command = ["python3", script, dcm2niix_input_dir]
    log.info(f"Command to be executed: {' '.join(command)}")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    with process.stdout:
        log.info(
            "Output from incomplete volume correction:" f"\n\n{process.stdout.read()}\n"
        )

    if process.wait() != 0:
        log.error("Incomplete volume removal script failed. Exiting.")
        os.sys.exit(1)
    else:
        log.info("Success.")

        # If missing volumes found, two directories (corrected_dcm and orphan_dcm)
        # in the dcm2niix input directory are created.
        corrected_dcm_dir = os.path.join(dcm2niix_input_dir, "corrected_dcm")
        orphan_dcm = "/".join([dcm2niix_input_dir, "orphan_dcm"])

        if os.path.isdir(corrected_dcm_dir):
            log.info("Dicoms from incomplete volumes were found and will be removed.")

            # Ensure that the dcm2niix input directory is empty except the two recently
            # created subdirectories; otherwise, fix_dcm_vols.py failed unexpectedly.
            subdirs = glob.glob(dcm2niix_input_dir + "/**")

            if len(subdirs) != 2:
                log.error(
                    "Output from incomplete volume removal script is unexpected. "
                    "Exiting."
                )
                os.sys.exit(1)

            else:
                # If dcm2niix input directory is empty:
                # 1. Remove orphan directory
                shutil.rmtree(orphan_dcm)

                # 2. Move corrected dicoms into original dcm2niix input directory
                dicoms = glob.glob(corrected_dcm_dir + "/**")
                for file in dicoms:
                    shutil.move(file, dcm2niix_input_dir)

                # 3. Remove corrected dicoms directory
                shutil.rmtree(corrected_dcm_dir)
        else:
            log.info(
                (
                    "No file removal performed. "
                    "No dicoms from incomplete volumes were found."
                )
            )

        n_dicom_files = len(glob.glob(dcm2niix_input_dir + "/*"))
        log.info(
            (
                f"{n_dicom_files} dicom files remain. "
                "Completed incomplete volume correction."
            )
        )


def decompress_dicoms(dcm2niix_input_dir):
    """Implement decompression of dicom files.

           For some types of dicom files, compression can be applied to the image data
           which will cause dcm2niix to fail. We use a method, gdcmconv, recommended by
           dcm2niix's author Chris Rorden to decompress these images prior to
           conversion. For additional details, see:
           https://www.nitrc.org/plugins/mwiki/index.php/dcm2nii:MainPage#DICOM_Transfer_Syntaxes_and_Compressed_Images

    Args:
        dcm2niix_input_dir (str): The absolute path to a set of dicoms.

    Returns:
        None; decompresses dicoms in dc2miix_input_dir.

    """
    dicom_files = glob.glob(dcm2niix_input_dir + "/*")
    n_dicom_files = len(dicom_files)
    log.info(
        f"Running decompression of dicom files. {n_dicom_files} dicom files found."
    )

    for file in dicom_files:

        # Decompress with gcdmconv in place (overwriting the compressed dicom)
        command = ["gdcmconv", "--raw", file, file]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        if process.wait() != 0:
            log.info("Output from gdcmconv ...")

            with process.stdout:
                log.info("\n\n" + process.stdout.read())

            log.error("Error decompressing dicom file using gdcmconv. Exiting.")
            os.sys.exit(1)

    log.info("Success. Completed decompression of dicom files.")


def coil_combine(nifti_files):
    """Implement the coil combined method.

    Args:
        nifti_files (list): A set of absolute paths to nifti files to
            generate coil combined data for.

    Returns:
        None; replaces the input nifti file with coil combined version.

    """
    log.warning(
        "Expert Option (coil_combine). "
        "We trust that since you have selected this option "
        "you know what you are asking for. "
        "Continuing."
    )

    for nifti_file in nifti_files:

        try:

            log.info(f"Start implementing coil combined method for {nifti_file}")
            n1 = nb.load(nifti_file)
            d1 = n1.get_data()
            d2 = d1[..., -1]
            n2 = nb.Nifti1Image(d2, n1.get_affine(), header=n1.get_header())
            nb.save(n2, nifti_file)
            log.info(f"Generated coil combined data for {nifti_file}")

        except Exception as e:

            log.error(
                f"Could not generate coil combined data for {nifti_file}. Exiting."
            )
            log.exception(e)
            os.sys.exit(1)
