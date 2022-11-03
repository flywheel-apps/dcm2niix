"""Testing for functions within arrange.py script."""

import filecmp
import os
import shutil
import tarfile
import zipfile
from pathlib import Path

import pytest

from fw_gear_dcm2niix.dcm2niix import arrange

ASSETS_DIR = Path(__file__).parent / "assets"


def test_IsArchiveEmpty_EmptyZipArchive_CatchEmptyArchiveError():
    """Assertion to test whether exit_if_archive_empty() catches
    case of empty input zip file."""
    with pytest.raises(SystemExit) as exception:
        archiveObj = zipfile.ZipFile(f"{ASSETS_DIR}/empty_archive.zip", "r")
        arrange.exit_if_archive_empty(archiveObj)

    assert exception.type == SystemExit


def test_IsArchiveEmpty_EmptyTarArchive_CatchEmptyArchiveError():
    """Assertion to test whether exit_if_archive_empty() catches
    case of empty input tarfile."""
    with pytest.raises(SystemExit) as exception:
        archiveObj = tarfile.open(f"{ASSETS_DIR}/empty_archive.tgz", "r")
        arrange.exit_if_archive_empty(archiveObj)

    assert exception.type == SystemExit


def test_CleanInfilepath_Extensions_Match():
    """Assertions on test cases to check file path extension cleaning
    transformation."""
    assert arrange.clean_filename("dicom.dicom.zip") == "dicom"
    assert arrange.clean_filename("dicom.dcm.tgz") == "dicom"
    assert arrange.clean_filename("parrec.parrec.zip") == "parrec"
    assert arrange.clean_filename("parrec.PAR") == "parrec"
    assert arrange.clean_filename("parrec") == "parrec"


def test_CleanInfilepath_Alphanumerics_Match():
    """Assertions on test cases to check underscore transformation."""
    assert arrange.clean_filename("dicom.@1.2.D.tgz") == "dicom_1_2_D"
    assert arrange.clean_filename("dicom__#!.zip") == "dicom"
    assert arrange.clean_filename("1#.files.parrec.zip") == "1_files"


def test_CleanInfilepath_Underscores_Match():
    """Assertions on test cases to check underscore transformation."""
    assert arrange.clean_filename("parrec__files.parrec.tgz") == "parrec_files"
    assert arrange.clean_filename("dicom__.zip") == "dicom"


@pytest.mark.parametrize(
    "version",
    [
        ("dicom_nested_one_level"),
        ("dicom_nested_two_levels"),
        ("dicom_nested_uneven"),
        ("dicom_single"),
        ("parrec_single"),
    ],
)
def test_tally_files_ReturnsCorrectValues(version):
    """Compares output of arrange.tally_files() on zip/tar input
    with known answer, valid output.

    Args:
        version (str): input file name

    Returns:
        N/A, assertions are main point

    """

    file_dir = f"{ASSETS_DIR}/valid_dataset/{version}"

    # valid answers to check output against
    valid_answer = {
        "dicom_nested_one_level": {
            "file_set": {"image_1.dcm", "image_3.dcm"},
            "file_tree": [
                f"{ASSETS_DIR}/valid_dataset/dicom_nested_one_level/subdir_0/image_1.dcm",
                f"{ASSETS_DIR}/valid_dataset/dicom_nested_one_level/subdir_0/image_3.dcm",
            ],
            "file_name_path_dict": {
                "image_1.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_nested_one_level/subdir_0/image_1.dcm",
                "image_3.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_nested_one_level/subdir_0/image_3.dcm",
            },
        },
        "dicom_nested_two_levels": {
            "file_set": {"image_1.dcm", "image_3.dcm"},
            "file_tree": [
                f"{ASSETS_DIR}/valid_dataset/dicom_nested_two_levels/subdir_0/subdir_00/image_1.dcm",
                f"{ASSETS_DIR}/valid_dataset/dicom_nested_two_levels/subdir_0/subdir_01/image_3.dcm",
            ],
            "file_name_path_dict": {
                "image_1.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_nested_two_levels/subdir_0/subdir_00/image_1.dcm",
                "image_3.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_nested_two_levels/subdir_0/subdir_01/image_3.dcm",
            },
        },
        "dicom_nested_uneven": {
            "file_set": {"image_1.dcm", "image_3.dcm"},
            "file_tree": [
                f"{ASSETS_DIR}/valid_dataset/dicom_nested_uneven/subdir_0/image_1.dcm",
                f"{ASSETS_DIR}/valid_dataset/dicom_nested_uneven/subdir_0/subdir_00/image_3.dcm",
            ],
            "file_name_path_dict": {
                "image_1.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_nested_uneven/subdir_0/image_1.dcm",
                "image_3.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_nested_uneven/subdir_0/subdir_00/image_3.dcm",
            },
        },
        "dicom_single": {
            "file_set": {
                "image_1.dcm",
                "image_2.dcm",
                "image_3.dcm",
                "image_4.dcm",
                "image_5.dcm",
                "image_6.dcm",
            },
            "file_tree": [
                f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_1.dcm",
                f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_2.dcm",
                f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_3.dcm",
                f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_4.dcm",
                f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_5.dcm",
                f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_6.dcm",
            ],
            "file_name_path_dict": {
                "image_1.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_1.dcm",
                "image_2.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_2.dcm",
                "image_3.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_3.dcm",
                "image_4.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_4.dcm",
                "image_5.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_5.dcm",
                "image_6.dcm": f"{ASSETS_DIR}/valid_dataset/dicom_single/dicom_single/image_6.dcm",
            },
        },
        "parrec_single": {
            "file_set": {"parrec_single.par", "parrec_single.rec"},
            "file_tree": [
                f"{ASSETS_DIR}/valid_dataset/parrec_single/parrec_single/parrec_single.rec",
                f"{ASSETS_DIR}/valid_dataset/parrec_single/parrec_single/parrec_single.par",
            ],
            "file_name_path_dict": {
                "parrec_single.rec": f"{ASSETS_DIR}/valid_dataset/parrec_single/parrec_single/parrec_single.rec",
                "parrec_single.par": f"{ASSETS_DIR}/valid_dataset/parrec_single/parrec_single/parrec_single.par",
            },
        },
    }

    # get info on file directory
    file_set, file_tree, file_name_path_dict = arrange.tally_files(file_dir)

    assert file_set == valid_answer[version]["file_set"]

    file_tree.sort()
    valid_answer[version]["file_tree"].sort()
    assert file_tree == valid_answer[version]["file_tree"]

    assert file_name_path_dict == valid_answer[version]["file_name_path_dict"]


@pytest.mark.parametrize(
    "version, ext",
    [
        ("dicom_nested_one_level", "zip"),
        ("dicom_nested_two_levels", "zip"),
        ("dicom_nested_uneven", "zip"),
        ("dicom_single", "tgz"),
        ("parrec_single", "tgz"),
    ],
)
def test_PrepareDcm2niixInput_Zip_Tar_Archive_MatchValidDataset(version, ext, tmpdir):
    """Compares output of prepare_dcm2niix_input on zip/tar input
    with known answer, valid output.

    Args:
        version (str): input file name
        ext (str): input file extension
        tmpdir (py.path.local): temporary directory path for prepare_dcm2niix_input

    Returns:
        N/A, assertions are main point

    """

    # define input file, define and populate new_dir
    infile = f"{ASSETS_DIR}/{version}.{ext}"  #

    # define old dir
    old_dir = f"{ASSETS_DIR}/valid_dataset/{version}"  # corresponding unzipped dir

    # populate new dir
    new_dir = arrange.prepare_dcm2niix_input(infile, False, tmpdir)

    # get info on two directories: old and new
    file_set_old, file_tree_old, file_name_path_dict_old = arrange.tally_files(old_dir)
    file_set_new, file_tree_new, file_name_path_dict_new = arrange.tally_files(new_dir)

    # check that the two sets of filenames (leaves, not considering nesting level) match
    assert len(file_set_new - file_set_old) == 0
    assert len(file_set_old - file_set_new) == 0

    # file-level
    for file in [
        file_
        for file_ in file_name_path_dict_new.keys()
        if ((file_ != ".DS_Store") & (file_[0:2] != "._"))
    ]:

        # compare old and new file paths, check new one has expected form
        old_file_path = file_name_path_dict_old[file]
        new_file_path_1 = os.path.join(new_dir, file)
        new_file_path_2 = file_name_path_dict_new[file]
        assert new_file_path_2 == new_file_path_1

        # check analogous files match
        out = filecmp.cmp(old_file_path, new_file_path_2, shallow=True)
        assert out


@pytest.mark.parametrize(
    "version, ext",
    [
        ("dicom_nested_one_level_collision", "zip"),
        ("dicom_nested_two_levels_collision", "zip"),
        ("dicom_nested_uneven_collision", "zip"),
    ],
)
def test_PrepareDcm2niixInput_Archive_CatchCollisionError(version, ext, tmpdir):
    """Tests ability to catch collisions, where there are files with the same name
    (presumably at different levels) in the input that will be mapped to the same
    level in the output.

    Args:
        version (str): input file name
        ext (str): input file extension
        tmpdir (py.path.local): temporary directory path for prepare_dcm2niix_input

    Returns:
        N/A, assertion is main point
    """

    # source
    infile = f"{ASSETS_DIR}/{version}.{ext}"

    # store any exception, to check after cleanup
    with pytest.raises(SystemExit) as exception:
        arrange.prepare_dcm2niix_input(infile, False, tmpdir)

    # was exception raised?
    assert exception.type == SystemExit


def test_PrepareDcm2niixInput_ParRecSolo_MatchValidDataset(tmpdir):
    """Compares output of prepare_dcm2niix_input on parrec_solo input
    with known answer, valid output.

    Args:
        tmpdir (py.path.local): temporary directory path for prepare_dcm2niix_input

    Returns:
        N/A, makes assertions though
    """

    infile = f"{ASSETS_DIR}/parrec_solo.PAR"
    rec_infile = f"{ASSETS_DIR}/parrec_solo.REC"

    arrange.prepare_dcm2niix_input(infile, rec_infile, tmpdir)
    valid_dir = f"{ASSETS_DIR}/valid_dataset/parrec_solo"
    out = filecmp.dircmp(tmpdir, valid_dir)

    assert out.left_only == []
    assert out.right_only == []
