"""Testing for functions within arrange.py script."""

import filecmp
import pytest
import shutil
import tarfile
import zipfile

from dcm2niix import arrange


def test_IsArchiveEmpty_EmptyZipArchive_CatchEmptyArchiveError():

    with pytest.raises(SystemExit) as exception:
        archiveObj = zipfile.ZipFile("assets/empty_archive.zip", "r")
        arrange.is_archive_empty(archiveObj)

    assert exception.type == SystemExit


def test_IsArchiveEmpty_EmptyTarArchive_CatchEmptyArchiveError():

    with pytest.raises(SystemExit) as exception:
        archiveObj = tarfile.open("assets/empty_archive.tgz", "r")
        arrange.is_archive_empty(archiveObj)

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


def test_PrepareDcm2niixInput_ZipArchive_MatchValidDataset():

    versions = ["dicom_nested", "dicom_single", "parrec_single"]

    for version in versions:

        tmp_dir = "assets/tmp"
        shutil.os.mkdir(tmp_dir)
        infile = f"assets/{version}.zip"

        arrange.prepare_dcm2niix_input(infile, False, tmp_dir)
        valid_dir = f"assets/valid_dataset/{version}"
        out = filecmp.dircmp(tmp_dir, valid_dir)

        assert out.left_only == []
        assert out.right_only == []

        shutil.rmtree(tmp_dir)


def test_PrepareDcm2niixInput_ZipArchive_CatchNestedInputError():

    tmp_dir = "assets/tmp"
    shutil.os.mkdir(tmp_dir)
    infile = "assets/dicom_nested_error.zip"

    with pytest.raises(SystemExit) as exception:
        arrange.prepare_dcm2niix_input(infile, False, tmp_dir)

    shutil.rmtree(tmp_dir)

    assert exception.type == SystemExit


def test_PrepareDcm2niixInput_TarArchive_MatchValidDataset():

    versions = ["dicom_nested", "dicom_single", "parrec_single"]

    for version in versions:

        tmp_dir = "assets/tmp"
        shutil.os.mkdir(tmp_dir)
        infile = f"assets/{version}.tgz"

        arrange.prepare_dcm2niix_input(infile, False, tmp_dir)
        valid_dir = f"assets/valid_dataset/{version}"
        out = filecmp.dircmp(tmp_dir, valid_dir)

        assert out.left_only == []
        assert out.right_only == []

        shutil.rmtree(tmp_dir)


def test_PrepareDcm2niixInput_TarArchive_CatchNestedInputError():

    tmp_dir = "assets/tmp"
    shutil.os.mkdir(tmp_dir)
    infile = "assets/dicom_nested_error.tgz"

    with pytest.raises(SystemExit) as exception:
        arrange.prepare_dcm2niix_input(infile, False, tmp_dir)

    shutil.rmtree(tmp_dir)

    assert exception.type == SystemExit


def test_PrepareDcm2niixInput_ParRecSolo_MatchValidDataset():

    tmp_dir = "assets/tmp"
    shutil.os.mkdir(tmp_dir)
    infile = "assets/parrec_solo.PAR"
    rec_infile = "assets/parrec_solo.REC"

    arrange.prepare_dcm2niix_input(infile, rec_infile, tmp_dir)
    valid_dir = "assets/valid_dataset/parrec_solo"
    out = filecmp.dircmp(tmp_dir, valid_dir)

    assert out.left_only == []
    assert out.right_only == []

    shutil.rmtree(tmp_dir)


def test_PrepareDcm2niixInput_ParRecSolo_CatchParRecFileError():

    tmp_dir = "assets/tmp"
    shutil.os.mkdir(tmp_dir)
    infile = "assets/parrec_solo_error.PAR"
    rec_infile = "assets/parrec_solo_error.REC"

    with pytest.raises(SystemExit) as exception:
        arrange.prepare_dcm2niix_input(infile, rec_infile, tmp_dir)

    shutil.rmtree(tmp_dir)

    assert exception.type == SystemExit


def test_PrepareDcm2niixInput_ParRecSolo_CatchNoRecFileError():

    tmp_dir = "assets/tmp"
    shutil.os.mkdir(tmp_dir)
    infile = "assets/parrec_solo_error.PAR"

    with pytest.raises(SystemExit) as exception:
        arrange.prepare_dcm2niix_input(infile, False, tmp_dir)

    shutil.rmtree(tmp_dir)

    assert exception.type == SystemExit


def test_PrepareDcm2niixInput_ParRecSolo_CatchIncorrecteGearInputError():

    tmp_dir = "assets/tmp"
    shutil.os.mkdir(tmp_dir)
    infile = "assets/incorrect_input.txt"

    with pytest.raises(SystemExit) as exception:
        arrange.prepare_dcm2niix_input(infile, False, tmp_dir)

    shutil.rmtree(tmp_dir)

    assert exception.type == SystemExit
