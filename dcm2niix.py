"""Function to implement dcm2niix."""

import logging
import os
from distutils import util

from nipype.interfaces.dcm2nii import Dcm2niix

logging.getLogger('nipype.interface').setLevel('CRITICAL')
log = logging.getLogger()

def run_dcm2niix(configuration, source_dir, output_dir):
    """Run dcm2niix.

    Args:
        configuration (dict): key-value pairs of dcm2niix command flags from input config.
        source_dir (str): the absolute path to the output directory containing
            the files from the input(s).
        output_dir (str): absolute path to the output directory to place the converted results.

    Returns:
        output (nipype.interfaces.base.support.InterfaceResult): dcm2niix output results.

    """
    try:

        converter = Dcm2niix()
        log.info(f'Starting dcm2niix {converter.version}')

        converter.inputs.source_dir = source_dir
        converter.inputs.output_dir = output_dir

        # dcm2niix command configurations for bids sidecar generation and anonymization
        if configuration['bids_sidecar'] == 'o':
            converter.inputs.args = '-b o'
            converter.inputs.anon_bids = configuration['anonymize_bids']
        else:
            # always select bids format to get json sidecars for updating metadata
            converter.inputs.bids_format = True

            if bool(util.strtobool(configuration['bids_sidecar'])):
                converter.inputs.anon_bids = configuration['anonymize_bids']

        # dcm2niix command configurations for filename and compression
        if configuration['vol3D']:
            configuration['compress_nifti'] = '3'

        if configuration['compress_nifti'] == '3':
            log.info(f'Outputs will be saved as uncompressed 3D volumes. \
                       \nFilename will be set to %p_%s to prevent overwritting files.')
            configuration['filename'] = '%p_%s'

        converter.inputs.compress = configuration['compress_nifti']
        converter.inputs.compression = configuration['compression_level']
        converter.inputs.out_filename = configuration['filename']

        # additional dcm2niix command configurations
        converter.inputs.crop = configuration['crop']
        converter.inputs.has_private = configuration['text_notes_private']
        converter.inputs.ignore_deriv = configuration['ignore_derived']
        converter.inputs.merge_imgs = configuration['merge2d']
        converter.inputs.philips_float = configuration['philips_scaling']
        converter.inputs.single_file = configuration['single_file_mode']

        if configuration['lossless_scaling']:
            converter.inputs.args = '-l y'

        # TODO: logic before and after this config setting is needed
        if configuration['convert_only_series'] != 'all':
            converter.inputs.series_numbers = configuration['convert_only_series']

        # log the dcm2niix command configuration and run
        log.info(f'Command to be executed: \n\n{converter.cmdline}\n')
        output = converter.run()

        log.info('Output from dcm2niix ...')
        log.info('\n\n' + output.runtime.stdout + '\n')

        # if error from dcm2niix software, then raise exception
        if output.runtime.returncode == 1:
            raise Exception('The dcm2niix software pacakage returned an error.')
        else:
            log.info('Finished dcm2niix conversion.\n')

    except Exception as e:

        log.error(f'Did not complete dcm2niix conversion. Exiting.')
        log.exception(e, exc_info=False)

        if not configuration["ignore_errors"]:
            os.sys.exit(1)

    return output
