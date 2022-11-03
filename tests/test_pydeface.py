"""Testing for functions within pydeface_run.py script."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import nibabel as nb
import numpy as np
import pytest

from fw_gear_dcm2niix.pydeface import pydeface_run

ASSETS_DIR = Path(__file__).parent / "assets"
print(f"ASSETS_DIR: {ASSETS_DIR}")


"""Testing for functions within pydeface_run.py script."""


@pytest.mark.parametrize(
    "with_template, with_facemask, valid_file",
    [
        (False, False, f"{ASSETS_DIR}/pydeface_T1_infile.nii.gz"),
        (True, False, f"{ASSETS_DIR}/pydeface_T1_template.nii.gz"),
        (False, True, f"{ASSETS_DIR}/pydeface_T1_facemask.nii.gz"),
        (True, True, f"{ASSETS_DIR}/pydeface_T1_alloptions.nii.gz"),
    ],
)
def test_RunPydeface_Mocking_Outer(mocker, with_template, with_facemask, valid_file):

    # Input files not already specified
    infile = f"{ASSETS_DIR}/pydeface_T1.nii.gz"
    test_file = shutil.copyfile(infile, f"{ASSETS_DIR}/pydeface_T1_test.nii.gz")
    if with_template:
        template_file = f"{ASSETS_DIR}/pydeface_template.nii.gz"
    else:
        template_file = None
    if with_facemask:
        facemask_file = f"{ASSETS_DIR}/pydeface_facemask.nii.gz"
    else:
        facemask_file = None

    # Deface
    run_pydeface_run_construct_log_command = mocker.patch(
        "fw_gear_dcm2niix.pydeface.pydeface_run.construct_log_command"
    )
    run_pydeface_run_deface_multiple_niftis = mocker.patch(
        "fw_gear_dcm2niix.pydeface.pydeface_run.deface_multiple_niftis"
    )
    run_pydeface_run_deface_single_nifti = mocker.patch(
        "fw_gear_dcm2niix.pydeface.pydeface_run.deface_single_nifti"
    )
    pydeface_run.construct_log_command(
        infile,
        pydeface_cost="mutualinfo",
        template=None,
        facemask=None,
        pydeface_nocleanup=False,
        pydeface_verbose=False,
    )
    pydeface_run.deface_multiple_niftis(
        [test_file],
        template=template_file,
        facemask=facemask_file,
        pydeface_nocleanup=True,
        pydeface_verbose=True,
    )

    # Checks
    run_pydeface_run_construct_log_command.assert_called_once()
    run_pydeface_run_deface_multiple_niftis.assert_called_once()


"""Testing for functions within pydeface_run.py script."""


@pytest.mark.parametrize(
    "with_template, with_facemask, valid_file",
    [
        (False, False, f"{ASSETS_DIR}/pydeface_T1_infile.nii.gz"),
        (True, False, f"{ASSETS_DIR}/pydeface_T1_template.nii.gz"),
        (False, True, f"{ASSETS_DIR}/pydeface_T1_facemask.nii.gz"),
        (True, True, f"{ASSETS_DIR}/pydeface_T1_alloptions.nii.gz"),
    ],
)
def test_RunPydeface_Mocking_Inner(mocker, with_template, with_facemask, valid_file):

    # Input files not already specified
    infile = f"{ASSETS_DIR}/pydeface_T1.nii.gz"
    test_file = shutil.copyfile(infile, f"{ASSETS_DIR}/pydeface_T1_test.nii.gz")
    if with_template:
        template_file = f"{ASSETS_DIR}/pydeface_template.nii.gz"
    else:
        template_file = None

    if with_facemask:
        facemask_file = f"{ASSETS_DIR}/pydeface_facemask.nii.gz"
    else:
        facemask_file = None

    # Deface
    run_pydeface_run_construct_log_command = mocker.patch(
        "fw_gear_dcm2niix.pydeface.pydeface_run.construct_log_command"
    )
    run_pydeface_run_deface_single_nifti = mocker.patch(
        "fw_gear_dcm2niix.pydeface.pydeface_run.deface_single_nifti"
    )
    pydeface_run.construct_log_command(
        infile,
        pydeface_cost="mutualinfo",
        template=None,
        facemask=None,
        pydeface_nocleanup=False,
        pydeface_verbose=False,
    )
    pydeface_run.deface_multiple_niftis(
        [test_file],
        template=template_file,
        facemask=facemask_file,
        pydeface_nocleanup=True,
        pydeface_verbose=True,
    )

    # Checks
    run_pydeface_run_construct_log_command.assert_called_once()
    run_pydeface_run_deface_single_nifti.assert_called_once()


"""Testing for functions within pydeface_run.py script."""


@pytest.mark.parametrize(
    "with_template, with_facemask, valid_file",
    [
        (False, False, f"{ASSETS_DIR}/pydeface_T1_infile.nii.gz"),
        (True, False, f"{ASSETS_DIR}/pydeface_T1_template.nii.gz"),
        (False, True, f"{ASSETS_DIR}/pydeface_T1_facemask.nii.gz"),
        (True, True, f"{ASSETS_DIR}/pydeface_T1_alloptions.nii.gz"),
    ],
)
def test_RunPydeface_Log_Command_Check(with_template, with_facemask, valid_file):
    infile = f"{ASSETS_DIR}/pydeface_T1.nii.gz"
    command, log_command = pydeface_run.construct_log_command(
        infile,
        pydeface_cost="mutualinfo",
        template=None,
        facemask=None,
        pydeface_nocleanup=True,
        pydeface_verbose=True,
    )
    print(f"log_command: {log_command}")
    log_command_a = f"log_command_: pydeface --outfile {str(infile)} --force --cost mutualinfo --nocleanup --verbose {str(infile)}"
    print(log_command_a)
    assert (
        log_command
        == f"pydeface --outfile {str(infile)} --force --cost mutualinfo --nocleanup --verbose {str(infile)}"
    )


# """Testing for functions within pydeface_run.py script."""
# @pytest.mark.parametrize(
#     'with_template, with_facemask, valid_file', [
#         (False, False, f"{ASSETS_DIR}/pydeface_T1_infile.nii.gz"),
#         (True, False, f"{ASSETS_DIR}/pydeface_T1_template.nii.gz"),
#         (False, True, f"{ASSETS_DIR}/pydeface_T1_facemask.nii.gz"),
#         (True, True, f"{ASSETS_DIR}/pydeface_T1_alloptions.nii.gz")
#     ])
# def test_RunPydeface_WithInfile_Match(with_template, with_facemask, valid_file):
#
#     # Input files not already specified
#     infile = f"{ASSETS_DIR}/pydeface_T1.nii.gz"
#     test_file = shutil.copyfile(infile, f"{ASSETS_DIR}/pydeface_T1_test.nii.gz")
#     if(with_template):
#         template_file = f"{ASSETS_DIR}/pydeface_template.nii.gz"
#     else:
#         template_file = None
#     print(f"with_template: {with_template}")
#     print(f"template_file: {template_file}")
#
#     if(with_facemask):
#         facemask_file = f"{ASSETS_DIR}/pydeface_facemask.nii.gz"
#     else:
#         facemask_file = None
#     print(f"with_facemask: {with_facemask}")
#     print(f"facemask_file: {facemask_file}")
#
#     print(f"test_file: {test_file}")
#     print(f"valid_file: {valid_file}")
#
#     # Deface
#     pydeface_run.deface_multiple_niftis(
#         [test_file],
#         template=template_file,
#         facemask=facemask_file,
#         pydeface_nocleanup=True,
#         pydeface_verbose=True,
#     )
#
#     # Check result
#     valid_image = nb.load(valid_file).get_fdata()
#     test_image = nb.load(test_file).get_fdata()
#     print(f"valid_image:{valid_image}")
#     print(f"test_image:{test_image}")
#     print(f"valid_image.sum():{valid_image.sum()}")
#     print(f"test_image.sum():{test_image.sum()}")
#
#     outcome = np.array_equal(valid_image, test_image)
#     print(f"outcome: {outcome}")
#     assert outcome is True
#
#     # Clean up
#     os.remove(test_file)
#     # if (with_facemask):
#     #     os.remove(f"{ASSETS_DIR}/pydeface_T1_test_pydeface_mask.nii.gz")
#     # os.remove(f"{ASSETS_DIR}/pydeface_T1_test_pydeface.mat")


# test_RunPydeface_CompletesWithChange
# def test_RunPydeface_WithInfile_Disc():
#
#     infile = f"{ASSETS_DIR}/pydeface_T1.nii.gz"
#     test_file_i = shutil.copyfile(infile, f"{ASSETS_DIR}/pydeface_T1_test_i.nii.gz")
#     test_file_f = shutil.copyfile(infile, f"{ASSETS_DIR}/pydeface_T1_test_f.nii.gz")
#     valid_file = f"{ASSETS_DIR}/pydeface_T1_infile.nii.gz"
#
#     pydeface_run.deface_multiple_niftis([test_file_f])
#
#     valid_image = nb.load(valid_file).get_fdata()
#     test_image_i = nb.load(test_file_i).get_fdata()
#     test_image_f = nb.load(test_file_f).get_fdata()
#     image_discrep = test_image_f - valid_image
#     rel_disc = (test_image_f - test_image_i).sum() / (test_image_i.sum())
#     assert not rel_disc >= 0.001
#     # outcome = np.array_equal(valid_image, test_image_f)
#     os.remove(test_file_i)
#     os.remove(test_file_f)
#     assert image_discrep.sum() > 0
#     return \
#         infile, \
#         valid_image, \
#         test_image_i, \
#         test_image_f, \
#         image_discrep
