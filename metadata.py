"""Generate file metadata from dcm2niix output."""

import json
import logging
import os
import re


log = logging.getLogger()


def generate_metadata(configuration, output, work_dir):
    """Generate file metadata from dcm2niix output.

        Using the BIDS json sidecar output from dcm2niix, generate file metadata
        (file.info) and set the classification (file.measurements) from the input
        configuration settings.

    Args:
        configuration (dict): TODO
        output (nipype.interfaces.base.support.InterfaceResult): TODO
        work_dir (str): the absolute path to the working directory where the metadata
            file generated is written to.

    Returns:
        metadata_file (str): absolute path to the metadata file generated.

    """
    log.info('Generating metadata.')
    classification, modality = generate_metadata_from_config(configuration)

    capture_metadata = []

    niftis = output.outputs.converted_files
    if type(niftis) == str:
        niftis = [niftis]

    for file in niftis:

        bids_sidecar = os.path.join(work_dir, re.sub(r'(\.nii\.gz|\.nii)',
                                                     '.json',
                                                     os.path.basename(file)))

        with open(bids_sidecar) as bids_sidecar_file:
            bids_info = json.load(bids_sidecar_file, strict=False)

            if not modality and 'Modality' in bids_info:
                modality = bids_info['Modality']
            elif not modality:
                modality = 'MR'

        fdict = create_file_metadata(file, 'nifti', classification, bids_info, modality)
        capture_metadata.append(fdict)

        filedata = create_file_metadata(bids_sidecar, 'source code', classification, bids_info, modality)
        capture_metadata.append(filedata)

        bval = os.path.join(work_dir, re.sub(r'(\.nii\.gz|\.nii)',
                                             '.bval',
                                             os.path.basename(file)))
        if os.path.isfile(bval):
            filedata = create_file_metadata(bval, 'bval', classification, bids_info, modality)
            capture_metadata.append(filedata)

        bvec = os.path.join(work_dir, re.sub(r'(\.nii\.gz|\.nii)',
                                             '.bvec',
                                             os.path.basename(file)))
        if os.path.isfile(bvec):
            filedata = create_file_metadata(bvec, 'bvec', classification, bids_info, modality)
            capture_metadata.append(filedata)

    # collate the metadata and write to file
    metadata = {}
    metadata['acquisition'] = {}
    metadata['acquisition']['files'] = capture_metadata
    metadata_file = os.path.join(work_dir, '.metadata.json')
    with open(metadata_file, 'w') as fObj:
        json.dump(metadata, fObj)

    log.info('Metadata generation completed successfully.')

    return metadata_file


def generate_metadata_from_config(configuration):
    """Generate metadata (classification and modality) from configuration settings."""

    try:
        classification = configuration['inputs']['dcm2niix_input']['object']['classification']
    except:
        log.info('Cannot determine classification from configuration.')
        classification = []
    try:
        modality = configuration['inputs']['dcm2niix_input']['object']['modality']
    except:
        log.info('Cannot determine modality from config.json.')
        modality = None

    return classification, modality


def create_file_metadata(filename, filetype, classification, bids_info, modality):
    """Create a dictionary storing the file metadata."""

    filedata = {}
    filedata['name'] = filename
    filedata['type'] = filetype
    filedata['classification'] = classification
    filedata['info'] = bids_info
    filedata['modality'] = modality

    return filedata