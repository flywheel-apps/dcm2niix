"""Testing takes approximately 17 minutes."""

import os
import shutil

import nibabel as nb
import numpy as np

from pydeface import pydeface_run


def test_RunPydeface_WithInfile_Match():

    infile = "assets/pydeface_T1.nii.gz"
    test_file = shutil.copyfile(infile, "assets/pydeface_T1_test.nii.gz")
    valid_file = "assets/pydeface_T1_infile.nii.gz"

    pydeface_run.deface_multiple_niftis([test_file])

    valid_image = nb.load(valid_file).get_data()
    test_image = nb.load(test_file).get_data()
    outcome = np.array_equal(valid_image, test_image)

    assert outcome is True

    os.remove(test_file)


def test_RunPydeface_WithTemplate_Match():

    infile = "assets/pydeface_T1.nii.gz"
    test_file = shutil.copyfile(infile, "assets/pydeface_T1_test.nii.gz")
    template_file = "assets/pydeface_template.nii.gz"
    valid_file = "assets/pydeface_T1_template.nii.gz"

    pydeface_run.deface_multiple_niftis([test_file], template=template_file)

    valid_image = nb.load(valid_file).get_data()
    test_image = nb.load(test_file).get_data()
    outcome = np.array_equal(valid_image, test_image)

    assert outcome is True

    os.remove(test_file)


def test_RunPydeface_WithFacemask_Match():

    infile = "assets/pydeface_T1.nii.gz"
    test_file = shutil.copyfile(infile, "assets/pydeface_T1_test.nii.gz")
    facemask_file = "assets/pydeface_facemask.nii.gz"
    valid_file = "assets/pydeface_T1_facemask.nii.gz"

    pydeface_run.deface_multiple_niftis([test_file], facemask=facemask_file)

    valid_image = nb.load(valid_file).get_data()
    test_image = nb.load(test_file).get_data()
    outcome = np.array_equal(valid_image, test_image)

    assert outcome is True

    os.remove(test_file)


def test_RunPydeface_WithAllOptions_Match():

    infile = "assets/pydeface_T1.nii.gz"
    test_file = shutil.copyfile(infile, "assets/pydeface_T1_test.nii.gz")
    template_file = "assets/pydeface_template.nii.gz"
    facemask_file = "assets/pydeface_facemask.nii.gz"
    valid_file = "assets/pydeface_T1_alloptions.nii.gz"

    pydeface_run.deface_multiple_niftis(
        [test_file],
        template=template_file,
        facemask=facemask_file,
        pydeface_nocleanup=True,
        pydeface_verbose=True,
    )

    valid_image = nb.load(valid_file).get_data()
    test_image = nb.load(test_file).get_data()

    outcome = np.array_equal(valid_image, test_image)

    assert outcome is True

    os.remove(test_file)
    os.remove("assets/pydeface_T1_test_pydeface_mask.nii.gz")
    os.remove("assets/pydeface_T1_test_pydeface.mat")
