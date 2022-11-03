"""The interfaces module
Temporary resolution to fix bug with dcm2niix not escaping metacharacters in filename.
"""
import glob
import os
import re

from nipype.interfaces.dcm2nii import Dcm2niix


class Dcm2niixEnhanced(Dcm2niix):
    def _parse_stdout(self, stdout):
        filenames = []
        for line in stdout.split("\n"):
            if line.startswith("Convert "):  # output
                fname = str(re.search(r"\S+/\S+", line).group(0))
                # Temporary fix - MR on nipype to fix this issue https://github.com/nipy/nipype/pull/3417
                fname = glob.escape(fname)
                filenames.append(os.path.abspath(fname))
        return filenames
