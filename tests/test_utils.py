"""Testing takes less than 1 minute."""

import pytest

from dcm2niix import dcm2niix_utils


def test_CoilCombine_ListNiftis_CatchError():

    with pytest.raises(SystemExit) as exception:
        nifti_files = ["assets/test_coil_combined.nii.gz"]
        dcm2niix_utils.coil_combine(nifti_files)

    assert exception.type == SystemExit
