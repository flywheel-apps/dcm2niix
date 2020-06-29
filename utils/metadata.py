"""Generate file metadata from dcm2niix output."""

import json
import logging
import os
import pprint
import re
from pathlib import Path

import pydicom
from pydicom.filereader import InvalidDicomError


log = logging.getLogger(__name__)


def generate(
    nifti_files,
    work_dir,
    dcm2niix_input_dir=None,
    retain_sidecar=True,
    retain_nifti=True,
    pydeface_intermediaries=False,
    classification=None,
    modality=None,
):
    """Generate file metadata from dcm2niix output.

        Using the BIDS json sidecar output from dcm2niix, generate file metadata
        (file.info) and set the classification (file.measurements) from the input
        configuration settings.

    Args:
        nifti_files (list): The absolute paths to nifti files to resolve.
        work_dir (str): The absolute path to the output directory of dcm2niix and where
            the metadata file generated is written to.
        dcm2niix_input_dir (str): The absolute path to a set of dicoms as input
            to dcm2niix.
        retain_sidecar (bool): If true, sidecar is retained in final output.
        retain_nifti (bool): If true, nifti is retained in final output.
        pydeface_intermediaries (bool): If True, pydeface intermediary files are
            retained. The files created when --nocleanup flag is applied to the
            pydeface command.
        classification (dict): File classification, typically from gear config.
        modality (str): File modality, typically from gear config.

    Returns:
        metadata_file (str): The absolute path to the metadata file generated.

    """
    log.info("Generating metadata.")

    capture_metadata = []

    # fmt: off
    # Append metadata from dicom header and from the associated bids sidecar
    for file in nifti_files:

        # Capture the path to associated sidecar
        sidecar = os.path.join(
                               work_dir, re.sub(
                                                r"(\.nii\.gz|\.nii)",
                                                ".json",
                                                os.path.basename(file))
        )

        with open(sidecar) as sidecar_file:
            sidecar_info = json.load(sidecar_file, strict=False)

            # Capture the fields required to select a single DICOM for metadata
            series_description = sidecar_info["SeriesDescription"]
            series_number = str(sidecar_info["SeriesNumber"])

            # Retain the modality set in the config; otherwise, replace with sidecar
            # captured modality determined via dcm2niix and if neither modality set
            # in the config or sidecar, then set modality to MR.
            if modality is None:
                if "Modality" in sidecar_info:
                    modality = sidecar_info["Modality"]
                else:
                    modality = "MR"

        # Set proper empty classification dictionary if not provided as input
        if classification is None:
            classification = {
                              "Intent": [],
                              "Measurement": []
            }

        # Using the unique set of SeriesDescription and SeriesNumber from the DICOM
        # header, capture additional metadata.
        if dcm2niix_input_dir:
            log.info("Capturing additional metadata from DICOMs.")

            dicoms = [
                path
                for path in Path(dcm2niix_input_dir).rglob("*")
                if not path.is_dir()
            ]

            for dicom in dicoms:

                try:
                    dicom_header = pydicom.read_file(dicom)

                    dicom_series_description = dicom_header.SeriesDescription.replace(
                        " ", "_"
                    )
                    dicom_series_number = str(dicom_header.SeriesNumber)

                    if (dicom_series_description == series_description) and (
                        dicom_series_number == series_number
                    ):

                        dicom_data = dicom_metadata_extraction(dicom_header)

                        count_metadata = len(
                            [v for v in dicom_data.values() if v is not None]
                        )
                        if count_metadata < 1:
                            # No dicom header metadata found, go to next dicom file
                            continue
                        else:
                            # Dicom header metadata found, leave loop
                            break

                except InvalidDicomError:
                    dicom_data = {}
                    continue

        else:
            log.info("Unable to capture additional metadata from DICOMs.")
            dicom_data = {}

        # Remove metadata with None value
        dicom_data = {k: v for k, v in dicom_data.items() if v is not None}

        # Collate metadata from dicom header and dcm2niix sidecar into one dictionary
        metadata = {**sidecar_info, **dicom_data}

        # Apply collated metadata to all associated files
        if retain_sidecar:
            filedata = create_file_metadata(
                                            sidecar,
                                            "source code",
                                            classification,
                                            metadata,
                                            modality
            )
            capture_metadata.append(filedata)

        if retain_nifti:
            filedata = create_file_metadata(
                                            file,
                                            "nifti",
                                            classification,
                                            metadata,
                                            modality
            )
            capture_metadata.append(filedata)

            bval = os.path.join(
                                work_dir, re.sub(
                                                 r"(\.nii\.gz|\.nii)",
                                                 ".bval",
                                                 os.path.basename(file))
            )

            if os.path.isfile(bval):
                filedata = create_file_metadata(
                                                bval,
                                                "bval",
                                                classification,
                                                metadata,
                                                modality
                )
                capture_metadata.append(filedata)

            bvec = os.path.join(
                                work_dir, re.sub(
                                                 r"(\.nii\.gz|\.nii)",
                                                 ".bvec",
                                                 os.path.basename(file))
            )

            if os.path.isfile(bvec):
                filedata = create_file_metadata(
                                                bvec,
                                                "bvec",
                                                classification,
                                                metadata,
                                                modality
                )
                capture_metadata.append(filedata)

            if pydeface_intermediaries:

                # The output mask of PyDeface is a compressed nifti, even if .nii input
                pydeface_mask = os.path.join(
                                             work_dir, re.sub(
                                                              r"(\.nii\.gz|\.nii)",
                                                              "_pydeface_mask.nii.gz",
                                                              os.path.basename(file))
                )

                if os.path.isfile(pydeface_mask):
                    filedata = create_file_metadata(
                                                    pydeface_mask,
                                                    "nifti",
                                                    classification,
                                                    metadata,
                                                    modality
                    )
                    capture_metadata.append(filedata)

                pydeface_matlab = os.path.join(
                                               work_dir, re.sub(
                                                                r"(\.nii\.gz|\.nii)",
                                                                "_pydeface.mat",
                                                                os.path.basename(file))
                )

                if os.path.isfile(pydeface_matlab):
                    filedata = create_file_metadata(
                                                    pydeface_matlab,
                                                    "MATLAB data",
                                                    classification,
                                                    metadata,
                                                    modality,
                    )
                    capture_metadata.append(filedata)

    # fmt: on
    # Collate the metadata and write to file
    metadata = {}
    metadata["acquisition"] = {}
    metadata["acquisition"]["files"] = capture_metadata
    metadata_file = os.path.join(work_dir, ".metadata.json")
    with open(metadata_file, "w") as fObj:
        json.dump(metadata, fObj)

    log.info("Metadata generation completed successfully.")
    metadata_formatted = pprint.pformat(metadata)
    log.info(f"Metadata contents: \n\n{metadata_formatted}\n")

    return metadata_file


def dicom_metadata_extraction(dicom_header):
    """Extract metadata from a dicom file header.

    Args:
        dicom_header (pydicom.dataset.FileDataset): A PyDicom header of a DICOM file.

    Returns:
        dicom_data (dict): Extracted dicom headers with their values.

    """
    dicom_data = {}

    # The time in seconds needed to run the prescribed pulse sequence
    try:
        dicom_data["AcquisitionDuration"] = dicom_header.AcquisitionDuration
    except AttributeError:
        dicom_data["AcquisitionDuration"] = None

    if dicom_data["AcquisitionDuration"] is None:

        try:
            dicom_data["AcquisitionDuration"] = dicom_header[0x0018, 0x9073].value
        except (AttributeError, KeyError):
            dicom_data["AcquisitionDuration"] = None

    # Number of dynamics is the number of temporal positions
    try:
        dicom_data["NumberOfDynamics"] = dicom_header.NumberOfTemporalPositions
    except AttributeError:
        dicom_data["NumberOfDynamics"] = None

    # Calculate field of view
    try:
        fov_x = round(dicom_header.PixelSpacing[0] * dicom_header.Columns)
        fov_y = round(dicom_header.PixelSpacing[1] * dicom_header.Rows)
        dicom_data["FOV"] = [fov_x, fov_y]
    except (AttributeError, IndexError):
        dicom_data["FOV"] = None

    try:
        dicom_data["SpacingBetweenSlices"] = float(dicom_header.SpacingBetweenSlices)
    except AttributeError:
        dicom_data["SpacingBetweenSlices"] = None

    try:
        dicom_data["PixelSpacing"] = [
            float(dicom_header.PixelSpacing[0]),
            float(dicom_header.PixelSpacing[1]),
        ]
    except AttributeError:
        dicom_data["PixelSpacing"] = None

    try:
        dicom_data["Resolution"] = calculate_resolution(dicom_header)
    except AttributeError:
        dicom_data["Resolution"] = None

    try:
        dicom_data["AcquisitionMatrix"] = dicom_header.AcquisitionMatrix
    except AttributeError:
        dicom_data["AcquisitionMatrix"] = None

    try:
        dicom_data["NumberOfEchos"] = dicom_header[0x2001, 0x1014].value
    except (AttributeError, KeyError):
        dicom_data["NumberOfEchos"] = None

    try:
        dicom_data["NumberOfSlices"] = dicom_header[0x2001, 0x1018].value
    except (AttributeError, KeyError):
        dicom_data["NumberOfSlices"] = None

    try:
        dicom_data["PrepulseDelay"] = dicom_header[0x2001, 0x101B].value
    except (AttributeError, KeyError):
        dicom_data["PrepulseDelay"] = None

    try:
        dicom_data["PrepulseType"] = dicom_header[0x2001, 0x101C].value
    except (AttributeError, KeyError):
        dicom_data["PrepulseType"] = None

    try:
        dicom_data["SliceOrientation"] = dicom_header[0x2001, 0x100B].value
    except (AttributeError, KeyError):
        dicom_data["SliceOrientation"] = None

    try:
        dicom_data["ScanningTechnique"] = dicom_header[0x2001, 0x1020].value
    except (AttributeError, KeyError):
        dicom_data["ScanningTechnique"] = None

    try:
        dicom_data["ScanType"] = dicom_header[0x2005, 0x10A1].value
    except (AttributeError, KeyError):
        dicom_data["ScanType"] = None

    return dicom_data


def calculate_resolution(dicom_header):
    """Calculate the voxel resolution from a dicom file header."""
    # See: https://neurostars.org/t/calculating-voxel-resolution-from-dicom-headers/7091
    try:

        fov_frequency = round(dicom_header.PixelSpacing[0] * dicom_header.Columns)

        # FOV_phase = FOV * percent phase FOV
        # Percent phase FOV (also known as RFOV) is the ratio of FOV dimension in phase
        # direction to the FOV dimension in the frequency direction.
        rfov = dicom_header.PercentPhaseFieldOfView / 100
        fov_phase = round(dicom_header.PixelSpacing[1] * dicom_header.Rows * rfov)

        # Percent sampling is the fraction of acquisition matrix lines acquired.
        percent_sampling = dicom_header.PercentSampling / 100

        if (
            dicom_header.InPlanePhaseEncodingDirection == "ROW"
            or dicom_header.InPlanePhaseEncodingDirection == "OTHER"
        ):

            acquisition_matrix_frequency = dicom_header.AcquisitionMatrix[1]
            acquisition_matrix_phase = round(
                dicom_header.AcquisitionMatrix[2] * rfov * percent_sampling
            )

        elif dicom_header.InPlanePhaseEncodingDirection == "COL":

            acquisition_matrix_frequency = dicom_header.AcquisitionMatrix[0]
            acquisition_matrix_phase = round(
                dicom_header.AcquisitionMatrix[3] * rfov * percent_sampling
            )

        pixel_size_frequency = fov_frequency / acquisition_matrix_frequency
        pixel_size_phase = fov_phase / acquisition_matrix_phase

        voxel_x = f"{pixel_size_frequency:3.3f}"
        voxel_y = f"{pixel_size_phase:3.3f}"
        voxel_z = f"{dicom_header.SliceThickness:3.3f}"

        resolution = [voxel_x, voxel_y, voxel_z]

    except AttributeError:
        resolution = None

    except ZeroDivisionError:
        resolution = None

    return resolution


def create_file_metadata(filename, filetype, classification, bids_info, modality):
    """Create a dictionary storing the file metadata."""
    filedata = {}
    filedata["name"] = Path(filename).name
    filedata["type"] = filetype
    filedata["classification"] = classification
    filedata["info"] = bids_info
    filedata["modality"] = modality

    return filedata
