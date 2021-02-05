"""Functions to execute PyDeface on a list of NIfTI files or a single NIfTI file."""

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
    """Run PyDeface on a list of NIfTI files.

     Args:
        nifti_files (list): The paths to NIfTI files to be defaced.
        pydeface_cost (str): FSL-FLIRT cost function. Options: 'mutualinfo' (default),
            'corratio', 'normcorr', 'normal', 'leastsq', 'labeldiff', 'bbr'.
        template (str): The absolute path to an optional template image that will be
            used as the registration target instead of the default.
        facemask (str): The absolute path to an optional facemask image that will be
            used instead of the default.
        pydeface_nocleanup (bool): If true, do not clean up temporary files.
        pydeface_verbose (bool): If true, show additional status prints.

    Returns:
        None; replaces input NIfTI with defaced version.

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
    """Run PyDeface on a single of NIfTI file.

     Args:
        infile (str): The absolute path to the input NIfTI file to be defaced.
        pydeface_cost (str): FSL-FLIRT cost function. Options: 'mutualinfo' (default),
            'corratio', 'normcorr', 'normal', 'leastsq', 'labeldiff', 'bbr'.
        template (str): The absolute path to an optional template image that will be
            used as the registration target instead of the default.
        facemask (str): The absolute path to an optional facemask image that will be
            used instead of the default.
        pydeface_nocleanup (bool): If true, do not clean up temporary files.
        pydeface_verbose (bool): If true, show additional status prints.

    Returns:
        None; replaces input NIfTI with defaced version.

    """
    log.info(f"Running PyDeface on {infile}")

    command = ["pydeface"]

    command.append("--outfile")
    command.append(str(infile))
    command.append("--force")

    command.append("--cost")
    command.append(str(pydeface_cost))

    if template:
        command.append("--template")
        command.append(str(template))

    if facemask:
        command.append("--facemask")
        command.append(str(facemask))

    if pydeface_nocleanup:
        command.append("--nocleanup")

    if pydeface_verbose:
        command.append("--verbose")

    command.append(str(infile))
    log_command = " ".join(command)
    log.info(f"Command to be executed: \n\n{log_command}\n")

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        log.info(f"Output from PyDeface: \n\n{process.stdout.read()}")

        if process.wait() != 0:
            log.error("Error defacing nifti using PyDeface. Exiting.")
            os.sys.exit(1)

    except FileNotFoundError:
        log.exception("PyDeface unable to be found as executable. Exiting.")
        os.sys.exit(1)

    log.info(f"Success. PyDeface completed on {infile}.")
