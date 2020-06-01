import glob
import logging
import os
import re
import shutil

from utils import metadata


log = logging.getLogger(__name__)


def setup(
    nifti_files,
    work_dir,
    dcm2niix_input_dir,
    output_dir,
    ignore_errors=False,
    retain_sidecar=True,
    retain_nifti=True,
    pydeface_intermediaries=False,
    classification=list(),
    modality=None,
):
    """Orchestrate resolution of gear, including metadata capture and file retention.

    Args:
        nifti_files (list): absolute paths to nifti files to resolve.
        work_dir (str): absolute path to the output directory of dcm2niix and where the
            metadata file generated is written to.
        dcm2niix_input_dir (str): absolute path to a set of dicoms as input to dcm2niix.
        retain_sidecar (bool): if True, sidecar is retained in final output.
        retain_nifti (bool): if True, nifti is retained in final output.
        pydeface_intermediaries (bool): if True, pydeface intermediary files are retained.
            The files when --nocleanup flag is applied to the pydeface command.
        classification (list): file classification, typically from gear config
        modality (str): file modality, typically from gear config

    Returns:
        None

    """
    # ignoring errors configuration option; move all files from work_dir to output_dir
    if (ignore_errors == True) and (nifti_files == None):
        log.info("Retaining gear outputs. WARNING: Using an Expert Option.")
        work_dir_contents = glob.glob(work_dir + "/*")

        for item in work_dir_contents:
            if not os.path.isdir(item):
                shutil.move(item, output_dir)

    # capture metadata
    # TODO: test with PAR/REC files
    metadata_file = metadata.generate(
        nifti_files,
        work_dir,
        dcm2niix_input_dir,
        retain_sidecar=retain_sidecar,
        retain_nifti=retain_nifti,
        pydeface_intermediaries=pydeface_intermediaries,
        classification=classification,
        modality=modality,
    )

    # retain gear outputs
    retain_gear_outputs(
        nifti_files,
        metadata_file,
        work_dir,
        output_dir,
        retain_sidecar=retain_sidecar,
        retain_nifti=retain_nifti,
        pydeface_intermediaries=pydeface_intermediaries,
    )


def retain_gear_outputs(
    nifti_files,
    metadata_file,
    work_dir,
    output_dir,
    retain_sidecar=True,
    retain_nifti=True,
    pydeface_intermediaries=False,
):
    """Move selected gear outputs to the output directory.

    Args:
        nifti_files (list): absolute paths to nifti files to resolve.
        metadata_file (str): absolute path to the metadata file.
        work_dir (str): absolute path to the output directory of dcm2niix and where the
            generated metadata file is.
        output_dir (str): absolute path to the gear output directory.
        retain_sidecar (bool): if True, sidecar is retained in final output.
        retain_nifti (bool): if True, nifti is retained in final output.
        pydeface_intermediaries (bool): if True, pydeface intermediary files are retained.
            The files when --nocleanup flag is applied to the pydeface command.

    Returns:
        None

    """
    log.info("Resolving gear outputs.")

    for file in nifti_files:

        # move bids json sidecar file, if indicated
        if retain_sidecar:
            bids_sidecar = os.path.join(
                work_dir, re.sub(r"(\.nii\.gz|\.nii)", ".json", os.path.basename(file))
            )
            shutil.move(bids_sidecar, output_dir)

        # move niftis and associated files (.bval, .bvec, .mat), if indicated
        if retain_nifti:

            # move nifti file
            shutil.move(file, output_dir)

            # move bval file, if exists
            bval = os.path.join(
                work_dir, re.sub(r"(\.nii\.gz|\.nii)", ".bval", os.path.basename(file))
            )
            if os.path.isfile(bval):
                shutil.move(bval, output_dir)

            # move bvec file, if exists
            bvec = os.path.join(
                work_dir, re.sub(r"(\.nii\.gz|\.nii)", ".bvec", os.path.basename(file))
            )
            if os.path.isfile(bvec):
                shutil.move(bvec, output_dir)

            # move pydeface intermediary files, if exists
            if pydeface_intermediaries:

                # ??? is output of pydefaced always compressed nifti?
                pydeface_mask = os.path.join(
                    work_dir,
                    re.sub(
                        r"(\.nii\.gz|\.nii)",
                        "_pydeface_mask.nii.gz",
                        os.path.basename(file),
                    ),
                )

                if os.path.isfile(pydeface_mask):
                    shutil.move(pydeface_mask, output_dir)

                pydeface_matlab = os.path.join(
                    work_dir,
                    re.sub(
                        r"(\.nii\.gz|\.nii)", "_pydeface.mat", os.path.basename(file)
                    ),
                )

                if os.path.isfile(pydeface_matlab):
                    shutil.move(bvec, output_dir)

    # move metadata file
    shutil.move(metadata_file, output_dir)

    log.info("Gear outputs resolved.")
