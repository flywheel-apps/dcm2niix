#!/usr/bin/env python3

import glob
import logging
import os

import flywheel
import pydicom

import arrange
import dcm2niix
import metadata
import pydeface
import resolve
import utils


# TODO: reconfigure with sdk calls
logfile = "/flywheel/v0/output/logfile.log"
FORMAT = "[%(asctime)s - %(levelname)s - %(name)s:%(lineno)d] %(message)s"
dateformat = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(filename=logfile, level=logging.DEBUG, format=FORMAT, datefmt=dateformat)
log = logging.getLogger()


def main(gear_context):

    configuration = gear_context.config

    # capture input for dcm2niix
    infile = gear_context.get_input_path('dcm2niix_input')
    if gear_context.get_input_path('rec_file_input'):
        rec_infile = gear_context.get_input_path('rec_file_input')
    else:
        rec_infile = False

    # prepare dcm2niix input
    work_dir = gear_context.work_dir
    dcm2niix_input_dir = arrange.prepare_dcm2niix_input(infile, rec_infile, work_dir)

    # remove incomplete volumes
    if configuration['remove_incomplete_volumes']:
        dicom_file = glob.glob(dcm2niix_input_dir + '/*')[0]

        try:
            pydicom.filereader.dcmread(dicom_file)
        except pydicom.errors.InvalidDicomError:
            log.info(('Unable to run incomplete volume correction. '
                      'Input archive does not contain dicoms. Exiting.'))
            os.sys.exit(1)

        utils.remove_incomplete_volumes(dcm2niix_input_dir)

    # decompress dicom files
    if configuration['decompress_dicoms']:
        utils.decompress_dicoms(dcm2niix_input_dir)

    # anonymization cascade
    if configuration['pydeface']:
        configuration['anonymize_bids'] = True
        configuration['text_notes_private'] = False

    # run dcm2niix
    output = dcm2niix.run_dcm2niix(configuration, dcm2niix_input_dir,  work_dir)

    # apply coil combined method
    if configuration['coil_combine']:
        nifti_files = output.outputs.converted_files

        if isinstance(nifti_files, str):
            nifti_files = [nifti_files]
            utils.coil_combined(nifti_files)

    # run pydeface
    if configuration['pydeface']:
        log.info('Establishing inputs for pydeface.')

        niftis = output.outputs.converted_files
        if type(niftis) == str:
            niftis = [niftis]

        if gear_context.get_input_path('pydeface_template'):
            template = gear_context.get_input_path('pydeface_template')
            log.info(f'Found input template for pydeface: {template}')
        else:
            log.info('No input template provided for pydeface. Defaults assumed.')
            template = None

        if gear_context.get_input_path('pydeface_facemask'):
            facemask = gear_context.get_input_path('pydeface_facemask')
            log.info(f'Found input facemask for pydeface: {facemask}')
        else:
            log.info('No input facemask provided for pydeface. Defaults assumed.')
            facemask = None

        for file in niftis:
            log.info(f'Running pydeface on {file}')
            pydeface.run_pydeface(configuration,
                                  file,
                                  template=template,
                                  facemask=facemask)

    # capture metadata
    metadata_file = metadata.generate_metadata(configuration, output, work_dir)
    # TODO: add metadata from dicoms: aquisition duration = TR x # dynamics
    # TODO: add metadata from dicoms: add number of dynamics = time tag from DICOM header

    # resolve gear outputs
    output_dir = gear_context.output_dir
    resolve.move_gear_outputs(configuration, output, metadata_file, work_dir, output_dir)

    return 0


if __name__ == '__main__':

    with flywheel.GearContext() as gear_context:
        exit_status = main(gear_context)

    log.info(f'Successful gear execution with exit status = {exit_status}')
