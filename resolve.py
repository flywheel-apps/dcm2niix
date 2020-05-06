import logging
import os
import re
import shutil
from distutils import util


log = logging.getLogger()


def move_gear_outputs(configuration, output, metadata_file, work_dir, output_dir):
    """Move gear outputs to the output directory.

    Args:
        output (nipype.interfaces.base.support.InterfaceResult): TODO
        metadata_file (str): absolute path to the metadata file.
        work_dir (str): absolute path to the working directory.
        output_dir (str): absolute path to the gear output directory.

    Returns:
        None

    """
    log.info('Resolving gear outputs.')

    niftis = output.outputs.converted_files
    if type(niftis) == str:
        niftis = [niftis]

    for file in niftis:

        # move nifti file
        shutil.move(file, output_dir)

        # move bids json sidecar file, if indicated
        if not bool(util.strtobool(configuration['bids_sidecar'])):
            bids_sidecar = os.path.join(work_dir, re.sub(r'(\.nii\.gz|\.nii)',
                                                     '.json',
                                                     os.path.basename(file)))
            shutil.move(bids_sidecar, output_dir)

        # move bval file, if exists
        bval = os.path.join(work_dir, re.sub(r'(\.nii\.gz|\.nii)',
                                             '.bval',
                                             os.path.basename(file)))
        if os.path.isfile(bval):
            shutil.move(bval, output_dir)

        # move bvec file, if exists
        bvec = os.path.join(work_dir, re.sub(r'(\.nii\.gz|\.nii)',
                                             '.bvec',
                                             os.path.basename(file)))
        if os.path.isfile(bvec):
            shutil.move(bvec, output_dir)

    # move metadata file
    shutil.move(metadata_file, output_dir)

    log.info('Gear outputs resolved.')
