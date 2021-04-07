"""Functions to arrange dcm2niix input."""

import glob
import logging
import os
import re
import shutil
import tarfile
import zipfile


log = logging.getLogger(__name__)


def prepare_dcm2niix_input(infile, rec_infile, work_dir):
    """Prepare dcm2niix input directory.

        The input can be a zip archive (.zip), a compressed tar archive (.tgz), or a
        par/rec file pair. Input contents are placed in a single directory. The path to
        this directory is the output of this function.

    Args:
        infile (str): The absolute path to the input file.
        rec_infile (str): The absolute path to the rec file for a par/rec file pair;
            note, the infile input must be a valid par file.
        work_dir (str): The absolute path to the working directory where the output
            directory is created.

    Returns:
        dcm2niix_input_dir (str): The absolute path to the output directory containing
            the files from the input(s).

    """
    log.info("Arrange dcm2niix input.")

    if zipfile.is_zipfile(infile):

        try:

            with zipfile.ZipFile(infile, "r") as zip_obj:
                log.info(f"Establishing input as zip file: {infile}")
                exit_if_archive_empty(zip_obj)
                dcm2niix_input_dir = extract_archive_contents(zip_obj, work_dir)

        except zipfile.BadZipFile:
            log.exception(
                (
                    "Incorrect gear input. "
                    "File is not a zip archive file (.zip). Exiting."
                )
            )
            os.sys.exit(1)

    elif tarfile.is_tarfile(infile):

        try:
            with tarfile.open(infile, "r") as tar_obj:
                log.info(f"Establishing input as tar file: {infile}")
                exit_if_archive_empty(tar_obj)
                dcm2niix_input_dir = extract_archive_contents(tar_obj, work_dir)

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

        # If a REC file input was provided, check infile for a valid PAR file
        if infile.lower().endswith("par") and rec_infile.lower().endswith("rec"):

            dcm2niix_input_dir, dirname = setup_dcm2niix_input_dir(infile, work_dir)
            shutil.copy2(rec_infile, dcm2niix_input_dir)
            shutil.copy2(infile, dcm2niix_input_dir)
            adjust_parrec_filenames(dcm2niix_input_dir, dirname)

        else:
            log.error(
                (
                    "Incorrect gear input. If rec_file_input provided, "
                    "dcm2niix_input must be a valid PAR file. "
                    "rec_infile must be a valid REC file. Exiting."
                )
            )
            os.sys.exit(1)

    else:
        # Assume all other inputs will function downstream
        dcm2niix_input_dir, dirname = setup_dcm2niix_input_dir(infile, work_dir)
        shutil.copy2(infile, dcm2niix_input_dir)

    log.info("Input for dcm2niix prepared successfully.")

    return dcm2niix_input_dir


def exit_if_archive_empty(archive_obj):
    """If the archive contents are empty, log an error and exit."""
    if type(archive_obj) == zipfile.ZipFile:
        size_contents = sum([zipinfo.file_size for zipinfo in archive_obj.filelist])

    elif type(archive_obj) == tarfile.TarFile:
        size_contents = sum([tarinfo.size for tarinfo in archive_obj.getmembers()])

    else:
        log.info(
            "Unsupported archive format. Unable to establish size of input archive. Exiting."
        )
        os.sys.exit(1)

    if size_contents == 0:
        log.error("Incorrect gear input. Input archive is empty. Exiting.")
        os.sys.exit(1)


def tally_files(dir_loc, print_out=False):
    """Function to profile directory. Note current exclusion of {'\.DS_Store.*', '^\._.*'}
    from file_set and file_tree. # TODO move this exclusion?

    Args:
        dir_loc (str): path to directory to profile
        print_out (bool): log output (Default: False)
    Returns:
        file_set (set): set of file leaves that pass the regex criteria
        file_tree (list): list showing full filepaths of all files
        file_name_path_dict (dict): dict mapping from filenames that pass
         the regex criteria to full filepath
    """

    file_set = set()
    file_name_path_dict = {}
    file_tree = []
    gen = os.walk(dir_loc, topdown=True)
    next_gen = next(gen)
    # want to exclude files matching certain patterns str_to_exclude
    strs_to_exclude = ["\.DS_Store.*", "^\._.*"]
    excludes = [re.compile(s) for s in strs_to_exclude]
    while True:

        # info on current folder and contents
        (loc_i, dirs_i, files_i) = next_gen

        for file_ij in files_i:

            # if filename doesn't match any of the exclude patterns:
            if not any([exclude.search(file_ij) for exclude in excludes]):

                # avoid collisions from collapsing filepaths
                if file_ij in file_name_path_dict.keys():
                    print(f"more than one file with name of {file_ij} in directory tree, exiting.")
                    os.sys.exit(1)

                # set of files (short paths or leaves) found in directory
                file_set = file_set | set([file_ij])

                # dictionary to look up full file paths
                file_name_path_dict[file_ij] = os.path.join(loc_i, file_ij)

            # directory structure in list form, no filter on files
            file_tree.append(os.path.join(loc_i, file_ij))

        # info for debugging log
        log.debug(
            f"file_set: {file_set}"
            f"file_tree: {file_tree}"
            f"file_name_path_dict: {file_name_path_dict}"
        )

        # next folder:
        try:
            next_gen = next(gen)
        except StopIteration:
            break

    return \
        file_set, \
        file_tree, \
        file_name_path_dict


def flatten_directory(dir_source, dir_target, overwrite=False):
    """Takes input directory and creates corresponding output directory
     with relevant files all at one level.

    Args:
        dir_source (str): possibly nested source
        dir_target (str): place to create flat file structure
        overwrite (bool): if True overwrite files if they already exist

    Returns:
        info on source directory:
            file_set_source (set): set of file leaves that pass the regex criteria
            file_tree_source (list): list showing full filepaths of all files
            file_name_path_dict_source (dict): dict mapping from filenames that pass
             the regex criteria to full filepath

        info on target directory
            file_set_target (set): set of file leaves that pass the regex criteria
            file_tree_target (list): list showing full filepaths of all files
            file_name_path_dict_target (dict): dict mapping from filenames that pass
             the regex criteria to full filepath
    """
    # TODO maybe write test for overwriting

    # source directory tally
    file_set_source, file_tree_source, file_name_path_dict_source = \
        tally_files(dir_source)

    # check for already existing/clear way for target directory
    if os.path.exists(dir_target):
        if overwrite is True:
            shutil.rmtree(dir_target)
        else:
            print(f"file {dir_target} already exists, exiting.")
            os.sys.exit(1)
    os.mkdir(dir_target)

    # the main part, move the files from the possibly hierarchical structure
    # to the flat structure
    for file in file_name_path_dict_source.keys():
        shutil.move(file_name_path_dict_source[file], dir_target)

    # target directory tally
    file_set_target, file_tree_target, file_name_path_dict_target = \
        tally_files(dir_target)

    # log before/after
    file_tree_source_str = '\n'.join(file_tree_source)
    file_tree_target_str = '\n'.join(file_tree_target)
    log.info(
        f"\n\nfile_tree_source:\n{file_tree_source_str}\n"
        f"\nfile_tree_target:\n{file_tree_target_str}\n\n"
    )


def extract_archive_contents(archive_obj, work_dir):
    """Extract archive contents to a directory created from the input filename."""
    # 1. Get the stage for zip or tar archive
    if type(archive_obj) == zipfile.ZipFile:
        subdirs = [info.filename for info in archive_obj.infolist() if info.is_dir()]
        filename = archive_obj.filename
        filelist = archive_obj.namelist()

    elif type(archive_obj) == tarfile.TarFile:
        subdirs = [info.name for info in archive_obj.getmembers() if info.isdir()]
        filename = archive_obj.name
        filelist = archive_obj.getnames()

    # 2. Extract archive contents to directory
    if len(subdirs) == 0:

        # Input filename will be used as the dcm2niix input directory name
        dcm2niix_input_dir, dirname = setup_dcm2niix_input_dir(filename, work_dir)
        archive_obj.extractall(dcm2niix_input_dir)

    elif len(subdirs) >= 1:

        # Subdirectory name will be used as the dcm2niix input directory name
        print(f"subdirs: {subdirs}")
        dcm2niix_input_dir, dirname = setup_dcm2niix_input_dir(subdirs[0], work_dir)
        print(f"dcm2niix_input_dir: {dcm2niix_input_dir}")

        # set temp directory to extract to, before flattening output contents
        dcm2niix_input_dir_o = dcm2niix_input_dir + "_o"

        # clean slate
        if os.path.exists(dcm2niix_input_dir):
            shutil.rmtree(dcm2niix_input_dir)
        if os.path.exists(dcm2niix_input_dir_o):
            shutil.rmtree(dcm2niix_input_dir_o)

        # site for initial extraction
        os.mkdir(dcm2niix_input_dir_o)

        # extract
        if type(archive_obj) == zipfile.ZipFile:
            for subdir in subdirs:
                archive_obj.extractall(
                    dcm2niix_input_dir_o, strip_prefix_ziparchive(archive_obj, subdir)
                )
        elif type(archive_obj) == tarfile.TarFile:
            for subdir in subdirs:
                archive_obj.extractall(
                    dcm2niix_input_dir_o, strip_prefix_tararchive(archive_obj, subdir)
                )

        # flattening: take file leaves in dcm2niix_input_dir_o and move them dcm2niix_input_dir
        flatten_directory(dcm2niix_input_dir_o, dcm2niix_input_dir)

        # clean up
        shutil.rmtree(dcm2niix_input_dir_o)

    else:

        # if input packaging falls into none of above categories, not supported, exit
        log.error(
            (
                "Incorrect gear input. Input archive packaging is not supported. "
                f"Detected subdirs in archive: {subdirs}. Exiting."
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
    dcm2niix_input_dir = os.path.join(work_dir, dirname)
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

    # if no alphanumerics are present in the filename, set the filename to inputs
    if len(filename) == 0:
        filename = "inputs"

    return filename


def strip_prefix_ziparchive(zip_obj, prefix):
    """Modify a filepath in a zip archive without the prefix."""
    for zipinfo in zip_obj.infolist():

        if (
            zipinfo.filename.startswith(prefix)
            and os.path.splitext(zipinfo.filename)[0] != prefix
        ):

            zipinfo.filename = zipinfo.filename[len(prefix) :]

        # Only return files
        if not zipinfo.is_dir():

            yield zipinfo


def strip_prefix_tararchive(tar_obj, prefix):
    """Modify a filepath in a tar archive without the prefix."""
    for tarinfo in tar_obj.getmembers():

        if (
            tarinfo.path.startswith(prefix)
            and os.path.splitext(tarinfo.path)[0] != prefix
        ):

            tarinfo.path = tarinfo.path[len(prefix) + 1 :]

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
        renamed = os.path.join(filepath, filename) + extension.lower()
        os.rename(file, renamed)
