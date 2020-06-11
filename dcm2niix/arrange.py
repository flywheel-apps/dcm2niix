"""Functions to arrange dcm2niix input."""

import glob
import logging
import os
import re
import shutil
import tarfile
import zipfile

import nibabel as nb


log = logging.getLogger(__name__)


def prepare_dcm2niix_input(infile, rec_infile=None, work_dir):
    """Prepare dcm2niix input directory.

        The input can be a zip archive (.zip), a compressed tar archive (.tgz), or a
        par/rec file pair. Input contents are placed in a single directory. The path to
        this directory is the output.

    Args:
        infile (str): The absolute path to the input file.
        rec_infile (str): The absolute path to the rec file for a par/rec file pair;
            note, the infile input must be a valid par file. Optional.
        work_dir (str): The absolute path to the working directory where the output
            directory is created.

    Returns:
        dcm2niix_input_dir (str): The absolute path to the output directory containing
            the files from the input(s).

    """
    log.info("Prepare dcm2niix input.")

    if infile.endswith(".zip"):

        try:

            with zipfile.ZipFile(infile, "r") as zipObj:
                log.info(f"Establishing input as zip file: {infile}")
                is_archive_empty(zipObj)
                dcm2niix_input_dir = extract_archive_contents(zipObj, work_dir)

        except zipfile.BadZipFile:
            log.exception(
                (
                    "Incorrect gear input. "
                    "File is not a zip archive file (.zip). Exiting."
                )
            )
            os.sys.exit(1)

    elif infile.endswith(".tgz"):

        try:
            with tarfile.open(infile, "r") as tarObj:
                log.info(f"Establishing input as tar file: {infile}")
                is_archive_empty(tarObj)
                dcm2niix_input_dir = extract_archive_contents(tarObj, work_dir)

        except tarfile.ReadError:
            log.exception(
                (
                    "Incorrect gear input. "
                    "File is not a compressed tar archive file (.tgz). Exiting."
                )
            )
            os.sys.exit(1)

    elif rec_infile:
        log.info(f"Establishing input as par/rec file pair: {infile} & {rec_infile}")

        try:
            nb.parrec.load(rec_infile).shape
        except UnicodeDecodeError:
            log.exception(
                (
                    "Incorrect gear input. "
                    "rec_file_input must be a valid REC file. Exiting."
                )
            )
            os.sys.exit(1)

        # If a REC file input was provided, check infile for a valid PAR file
        if infile.lower().endswith("par"):

            try:
                nb.parrec.load(infile).shape
            except UnicodeDecodeError:
                log.exception(
                    (
                        "Incorrect gear input. If rec_file_input provided, "
                        "dcm2niix_input must be a valid PAR file. Exiting."
                    )
                )
                os.sys.exit(1)

            dcm2niix_input_dir, dirname = setup_dcm2niix_input_dir(infile, work_dir)
            shutil.copy2(rec_infile, dcm2niix_input_dir)
            shutil.copy2(infile, dcm2niix_input_dir)
            adjust_parrec_filenames(dcm2niix_input_dir, dirname)

    else:
        log.error("Incorrect gear input. Exiting.")
        os.sys.exit(1)

    log.info("Input for dcm2niix prepared successfully.")

    return dcm2niix_input_dir


def is_archive_empty(archiveObj):
    """If the archive contents are empty, log an error and exit."""
    if type(archiveObj) == zipfile.ZipFile:
        size_contents = sum([zipinfo.file_size for zipinfo in archiveObj.filelist])

    elif type(archiveObj) == tarfile.TarFile:
        size_contents = sum([tarinfo.size for tarinfo in archiveObj.getmembers()])

    else:
        log.info(
            "Unsupported archive format. Unable to establish size of input archive."
        )

    if size_contents == 0:
        log.error("Incorrect gear input. Input archive is empty. Exiting.")
        os.sys.exit(1)


def extract_archive_contents(archiveObj, work_dir):
    """Extract archive contents to a directory created from the input filename."""
    # 1. Get the stage for zip or tar archive
    if type(archiveObj) == zipfile.ZipFile:
        subdirs = [info.filename for info in archiveObj.infolist() if info.is_dir()]
        filename = archiveObj.filename
        filelist = archiveObj.namelist()

    elif type(archiveObj) == tarfile.TarFile:
        subdirs = [info.name for info in archiveObj.getmembers() if info.isdir()]
        filename = archiveObj.name
        filelist = archiveObj.getnames()

    # 2. Extract archive contents to directory
    if len(subdirs) == 0:

        # Input filename will be used as the dcm2niix input directory name
        dcm2niix_input_dir, dirname = setup_dcm2niix_input_dir(filename, work_dir)
        archiveObj.extractall(dcm2niix_input_dir)

    elif len(subdirs) == 1:

        # Subdirectory name will be used as the dcm2niix input directory name
        dcm2niix_input_dir, dirname = setup_dcm2niix_input_dir(subdirs[0], work_dir)

        if type(archiveObj) == zipfile.ZipFile:
            archiveObj.extractall(
                dcm2niix_input_dir, strip_prefix_ziparchive(archiveObj, subdirs[0])
            )

        if type(archiveObj) == tarfile.TarFile:
            archiveObj.extractall(
                dcm2niix_input_dir, strip_prefix_tararchive(archiveObj, subdirs[0])
            )

    else:

        # Multiple subdirectories, input packaging not supported, exit
        log.error(
            (
                "Incorrect gear input. Input archive packaging is not supported. "
                f"Multiple subdirectories detected in archive: {subdirs}. Exiting."
            )
        )
        os.sys.exit(1)

    # 3. If PAR file in the archive, then adjust par/rec filenames
    if [file for file in filelist if file.lower().endswith(".par")]:
        adjust_parrec_filenames(dcm2niix_input_dir, dirname)

    return dcm2niix_input_dir


def setup_dcm2niix_input_dir(infile, work_dir):
    """Create dcm2niix input directory using the filename from the input filepath."""
    if os.path.isfile(infile):
        filename = os.path.split(infile)[-1]
    else:
        # Passing subdirectory name (e.g., dicom_files)
        filename = infile

    dirname = clean_filename(filename)
    dcm2niix_input_dir = "/".join([work_dir, dirname])
    os.mkdir(dcm2niix_input_dir)

    return dcm2niix_input_dir, dirname


def clean_filename(filename):
    """Clean filename for the alphanumeric filename without extensions."""
    # Drop file extension
    # Do not use os.path.splitext because filename not required to have an extension
    for extension in [".zip", ".tgz", ".par", ".PAR"]:
        if filename.endswith(extension):
            filename = filename.replace(extension, "")

    # Drop imaging extensions
    # Do not use os.path.splitext because filename may include periods
    for extension in [".dicom", ".dcm", ".parrec"]:
        if filename.endswith(extension):
            filename = filename.replace(extension, "")

    # Replace non-alphanumerics with underscore and avoiding repeat underscores
    filename = re.sub("[^0-9a-zA-Z]+", "_", filename)

    # Do not end on an underscore
    filename = filename.rstrip("_")

    return filename


def strip_prefix_ziparchive(zipObj, prefix):
    """Modify a filepath in a zip archive without the prefix."""
    for zipinfo in zipObj.infolist():

        if (
            zipinfo.filename.startswith(prefix)
            and os.path.splitext(zipinfo.filename)[0] != prefix
        ):

            zipinfo.filename = zipinfo.filename[len(prefix):]

        # Only return files
        if not zipinfo.is_dir():

            yield zipinfo


def strip_prefix_tararchive(tarObj, prefix):
    """Modify a filepath in a tar archive without the prefix."""
    for tarinfo in tarObj.getmembers():

        if (
            tarinfo.path.startswith(prefix)
            and os.path.splitext(tarinfo.path)[0] != prefix
        ):

            tarinfo.path = tarinfo.path[len(prefix)+1:]

        # Only return files
        if tarinfo.isreg():

            yield tarinfo


def adjust_parrec_filenames(dcm2niix_input_dir, filename):
    """Rename par/rec files with the specified filename and lowercase extension."""
    files = glob.glob(dcm2niix_input_dir + "/**", recursive=True)
    files = [
        file
        for file in files
        if file.lower().endswith(".par") or file.lower().endswith(".rec")
    ]

    for file in files:

        filepath = os.path.split(file)[0]
        extension = os.path.splitext(file)[-1]
        renamed = "/".join([filepath, filename]) + extension.lower()
        os.rename(file, renamed)
