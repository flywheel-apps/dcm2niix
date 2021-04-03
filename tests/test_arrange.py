"""Testing for functions within arrange.py script."""

import filecmp
import pytest
import os
import shutil
import tarfile
import zipfile
from pathlib import Path

from dcm2niix_gear.dcm2niix import arrange

ASSETS_DIR = Path(__file__).parent / "assets"



def test_IsArchiveEmpty_EmptyZipArchive_CatchEmptyArchiveError():

    with pytest.raises(SystemExit) as exception:
        archiveObj = zipfile.ZipFile(f"{ASSETS_DIR}/empty_archive.zip", "r")
        arrange.exit_if_archive_empty(archiveObj)

    assert exception.type == SystemExit


def test_IsArchiveEmpty_EmptyTarArchive_CatchEmptyArchiveError():

    with pytest.raises(SystemExit) as exception:
        archiveObj = tarfile.open(f"{ASSETS_DIR}/empty_archive.tgz", "r")
        arrange.exit_if_archive_empty(archiveObj)

    assert exception.type == SystemExit


def test_CleanInfilepath_Extensions_Match():
    assert arrange.clean_filename("dicom.dicom.zip") == "dicom"
    assert arrange.clean_filename("dicom.dcm.tgz") == "dicom"
    assert arrange.clean_filename("parrec.parrec.zip") == "parrec"
    assert arrange.clean_filename("parrec.PAR") == "parrec"
    assert arrange.clean_filename("parrec") == "parrec"


def test_CleanInfilepath_Alphanumerics_Match():
    assert arrange.clean_filename("dicom.@1.2.D.tgz") == "dicom_1_2_D"
    assert arrange.clean_filename("dicom__#!.zip") == "dicom"
    assert arrange.clean_filename("1#.files.parrec.zip") == "1_files"


def test_CleanInfilepath_Underscores_Match():
    assert arrange.clean_filename("parrec__files.parrec.tgz") == "parrec_files"
    assert arrange.clean_filename("dicom__.zip") == "dicom"


@pytest.mark.parametrize("version, ext", [
    ("dicom_nested_one_level", "zip"),
    ("dicom_nested_two_levels", "zip"),
    ("dicom_nested_uneven", "zip"),

    ("dicom_single", "tgz"),
    ("parrec_single", "tgz")
])
def test_PrepareDcm2niixInput_Zip_Tar_Archive_MatchValidDataset(tmpdir, version, ext):

    # define input file, define and populate new_dir
    infile = f"{ASSETS_DIR}/{version}.{ext}" #

    # define old dir
    old_dir = f"{ASSETS_DIR}/valid_dataset/{version}" # corresponding unzipped dir

    # define and populate new dir
    if os.path.exists(f"{ASSETS_DIR}/tmp"):
        shutil.rmtree(f"{ASSETS_DIR}/tmp")
    os.mkdir(f'{ASSETS_DIR}/tmp')
    new_dir = arrange.prepare_dcm2niix_input(infile, False, f"{ASSETS_DIR}/tmp")

    # get info on two directories: old and new
    file_set_old, file_tree_old, file_name_path_dict_old = arrange.tally_files(old_dir)
    file_set_new, file_tree_new, file_name_path_dict_new = arrange.tally_files(new_dir)

    # check that the two sets of filenames (leaves, not considering nesting level) match
    assert len(file_set_new - file_set_old) == 0
    assert len(file_set_old - file_set_new) == 0

    # file-level
    for file in [file_ for file_ in file_name_path_dict_new.keys() if ((file_ != '.DS_Store') & (file_[0:2] != '._'))]:

        # compare old and new file paths, check new one has expected form
        old_file_path = file_name_path_dict_old[file]
        new_file_path_1 = os.path.join(new_dir, file)
        new_file_path_2 = file_name_path_dict_new[file]
        print(f"old_file_path: {old_file_path}")
        print(f"new_file_path_1: {new_file_path_1}")
        print(f"new_file_path_2: {new_file_path_2}")
        assert new_file_path_2 == new_file_path_1

        # check analogous files match
        out = filecmp.cmp(old_file_path, new_file_path_2, shallow=True)
        assert out


@pytest.mark.parametrize("version, ext", [
    ("dicom_nested_one_level_collision", "zip"),
    ("dicom_nested_two_levels_collision", "zip"),
    ("dicom_nested_uneven_collision", "zip")
])
def test_PrepareDcm2niixInput_Archive_CatchCollisionError(version, ext):

    # source
    infile = f"{ASSETS_DIR}/{version}.{ext}"

    # target
    tmp_dir = f"{ASSETS_DIR}/tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    shutil.os.mkdir(tmp_dir)

    # store any exception, to check after cleanup
    with pytest.raises(SystemExit) as exception:
        arrange.prepare_dcm2niix_input(infile, False, tmp_dir)

    # clean up
    shutil.rmtree(tmp_dir)

    # was exception raised?
    assert exception.type == SystemExit


def test_PrepareDcm2niixInput_ParRecSolo_MatchValidDataset():

    tmp_dir = f"{ASSETS_DIR}/tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    shutil.os.mkdir(tmp_dir)
    infile = f"{ASSETS_DIR}/parrec_solo.PAR"
    rec_infile = f"{ASSETS_DIR}/parrec_solo.REC"

    arrange.prepare_dcm2niix_input(infile, rec_infile, tmp_dir)
    valid_dir = f"{ASSETS_DIR}/valid_dataset/parrec_solo"
    out = filecmp.dircmp(tmp_dir, valid_dir)

    assert out.left_only == []
    assert out.right_only == []

    shutil.rmtree(tmp_dir)
