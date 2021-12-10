"""Testing for functions within dcm2niix_utils.py script."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import nibabel as nb
import numpy as np
import pytest

from fw_gear_dcm2niix.dcm2niix import dcm2niix_utils

ASSETS_DIR = Path(__file__).parent / "assets"


def test_CoilCombine_ListNiftis_CatchError():

    with pytest.raises(SystemExit) as exception:
        nifti_files = [f"{ASSETS_DIR}/test_coil_combined.nii.gz"]
        dcm2niix_utils.coil_combine(nifti_files)

    assert exception.type == SystemExit
