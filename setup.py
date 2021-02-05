"""
    fw-gear-dcm2niix
"""
import json
import setuptools


with open("manifest.json", "r") as f:
    manifest = json.load(f)
    VERSION = manifest["version"]

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name="fw-gear-dcm2niix",
    version=VERSION,
    description="A Flywheel Gear for implementing Chris Rorden's dcm2niix for converting DICOM (or PAR/REC) to NIfTI (or NRRD), with an optional implementation of Poldrack Lab's PyDeface to remove facial structures from NIfTI.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    project_urls={"Source Code": "https://github.com/flywheel-apps/dcm2niix"},
    author="Flywheel",
    author_email="support@flywheel.io",
    url="https://github.com/flywheel-apps/dcm2niix",
    python_requires=">=3.6",
    install_requires=[
        "flywheel-gear-toolkit>=0.1.1",
        "nibabel~=3.1.0",
        "nipype~=1.5.0",
        "numpy~=1.18.5",
        "pydeface~=2.0.0",
        "pydicom~=2.0.0",
    ],
    packages=setuptools.find_packages(),
)
