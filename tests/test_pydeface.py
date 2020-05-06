import json
import os
import shutil

import nibabel as nb
import numpy as np

from dcm2niix import pydeface


def test_RunPydeface_InfileOnly_Match():

    configuration = json.load(open('assets/pydeface_config.json'))
    infile = 'assets/pydeface_T1.nii.gz'
    test_file = shutil.copyfile(infile, 'assets/pydeface_T1_test.nii.gz')
    valid_file = 'assets/pydeface_T1_infile.nii.gz'

    pydeface.run_pydeface(configuration['config'], test_file)

    valid_image = nb.load(valid_file).get_data()
    test_image = nb.load(test_file).get_data()
    outcome = np.array_equal(valid_image, test_image)

    assert outcome == True

    os.remove(test_file)


def test_RunPydeface_WithTemplate_Match():

    configuration = json.load(open('assets/pydeface_config.json'))
    infile = 'assets/pydeface_T1.nii.gz'
    test_file = shutil.copyfile(infile, 'assets/pydeface_T1_test.nii.gz')
    template_file = 'assets/pydeface_template.nii.gz'
    valid_file = 'assets/pydeface_T1_template.nii.gz'

    pydeface.run_pydeface(configuration['config'], test_file, template=template_file)

    valid_image = nb.load(valid_file).get_data()
    test_image = nb.load(test_file).get_data()
    outcome = np.array_equal(valid_image, test_image)

    assert outcome == True

    os.remove(test_file)


def test_RunPydeface_WithFacemask_Match():

    configuration = json.load(open('assets/pydeface_config.json'))
    infile = 'assets/pydeface_T1.nii.gz'
    test_file = shutil.copyfile(infile, 'assets/pydeface_T1_test.nii.gz')
    facemask_file = 'assets/pydeface_facemask.nii.gz'
    valid_file = 'assets/pydeface_T1_facemask.nii.gz'

    pydeface.run_pydeface(configuration['config'], test_file, facemask=facemask_file)

    valid_image = nb.load(valid_file).get_data()
    test_image = nb.load(test_file).get_data()
    outcome = np.array_equal(valid_image, test_image)

    assert outcome == True

    os.remove(test_file)
