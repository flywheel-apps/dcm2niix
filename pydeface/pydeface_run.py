"""Functions to implement pydeface."""

import logging
import os
import subprocess


log = logging.getLogger(__name__)


def deface_multiple_niftis(
    nifti_files,
    pydeface_cost="mutualinfo",
    template=False,
    facemask=False,
    pydeface_nocleanup=False,
    pydeface_verbose=False,
):
    """Run pydeface on a set of nifti files.

     Args:
        nifti_files (list): paths to nifti files to generate coil combined data for.
        pydeface_cost (str): FSL-Flirt cost function. Options: 'mutualinfo' (default),
            'corratio', 'normcorr', 'normal', 'leastsq', 'labeldiff', 'bbr'.
        template (str): the absolute path to an optional template image that will be used
            as the registration target instead of the default
        facemask (str): the absolute path to an optional faskmask image that will be used
            instead of the default.
        pydeface_nocleanup (bool): if True, do not clean up temporary files.
        pydeface_verbose (bool): if True, show additional status prints.

    Returns:
        None, but replaces each input nifti with a defaced version.

    """
    for file in nifti_files:
        deface_single_nifti(
            file,
            pydeface_cost=pydeface_cost,
            template=template,
            facemask=facemask,
            pydeface_nocleanup=pydeface_nocleanup,
            pydeface_verbose=pydeface_verbose,
        )


def deface_single_nifti(
    infile,
    pydeface_cost="mutualinfo",
    template=None,
    facemask=None,
    pydeface_nocleanup=False,
    pydeface_verbose=False,
):
    """Run pydeface on a single nifti file.

     Args:
        infile (str): the absolute path to the input file.
        pydeface_cost (str): FSL-Flirt cost function. Options: 'mutualinfo' (default),
            'corratio', 'normcorr', 'normal', 'leastsq', 'labeldiff', 'bbr'.
        template (str): the absolute path to an optional template image that will be used
            as the registration target instead of the default
        facemask (str): the absolute path to an optional faskmask image that will be used
            instead of the default.
        pydeface_nocleanup (bool): if True, do not clean up temporary files.
        pydeface_verbose (bool): if True, show additional status prints.

    Returns:
        None, but replaces input nifti with defaced version.

    """
    log.info(f"Running pydeface on {infile}")

    command = ["pydeface"]

    command.append("--outfile")
    command.append(infile)
    command.append("--force")

    command.append("--cost")
    command.append(pydeface_cost)

    if template:
        command.append("--template")
        command.append(template)

    if facemask:
        command.append("--facemask")
        command.append(facemask)

    if pydeface_nocleanup:
        command.append("--nocleanup")

    if pydeface_verbose:
        command.append("--verbose")

    command.append(infile)
    log_command = " ".join(command)
    log.info(f"Command to be executed: \n\n{log_command}\n")

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        log.info("Output from pydeface ...")
        log.info("\n\n" + process.stdout.read())

        if process.wait() != 0:
            log.error("Error defacing nifti using pydeface. Exiting.")
            os.sys.exit(1)

    except FileNotFoundError:
        log.exception("pydeface unable to be found as executable. Exiting.")
        os.sys.exit(1)

    log.info(f"Success. Pydeface completed on {infile}.")
