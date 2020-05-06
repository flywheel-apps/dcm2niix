"""Function to implement pydeface."""

import logging
import os
import subprocess


log = logging.getLogger()


def run_pydeface(configuration, infile, template=None, facemask=None):
    """Run pydeface.

     Args:
        configuration (dict): key-value pairs of pydeface command flags from input config.
        infile (str): the absolute path to the input file.
        template (str): the absolute path to an optional template image that will be used
            as the registration target instead of the default
        facemask (str): the absolute path to an optional faskmask image that will be used
            instead of the default.

    Returns:
        None.
    """
    log.info('Running pydeface.')

    command = ['pydeface']

    # deface nifti in place (overwrite the existing nifti, leaving only the defaced nifti)
    command.append('--outfile')
    command.append(infile)
    command.append('--force')

    command.append('--cost')
    command.append(configuration['pydeface_cost'])

    if template:
        command.append('--template')
        command.append(template)

    if facemask:
        command.append('--facemask')
        command.append(facemask)

    if configuration["pydeface_nocleanup"]:
        command.append('--nocleanup')

    if configuration["pydeface_verbose"]:
        command.append('--verbose')

    command.append(infile)
    log_command = ' '.join(command)
    log.info(f'Command to be executed: \n\n{log_command}\n')

    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True)

    log.info('Output from pydeface ...')
    log.info('\n\n' + process.stdout.read())

    if process.wait() != 0:
        log.error('Error defacing nifti using pydeface. Exiting.')
        os.sys.exit(1)

    log.info('Success. Pydeface completed.')
