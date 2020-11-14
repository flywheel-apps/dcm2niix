"""Function to parse gear config into gear args."""

import logging
import pprint
import os
from pathlib import Path

log = logging.getLogger(__name__)


def generate_gear_args(gear_context, FLAG):
    """Generate gear arguments for different stages indicated by the FLAG."""
    log.info(f"{100*'-'}")
    log.info(f"Preparing arguments for gear stage >> {FLAG}.")

    if FLAG == "prepare":

        infile = gear_context.get_input_path("dcm2niix_input")
        try:
            with open(infile, "r") as f:
                log.debug(f"{infile} opened from dcm2niix_input.")
        except FileNotFoundError:

            # Path separation in filename may cause downloaded filename to be altered
            filename = (
                gear_context.config_json.get("inputs", {})
                .get("dcm2niix_input", {})
                .get("location", {})
                .get("name")
            )
            if len(filename.split("/")) > 1:
                infile = f"/flywheel/v0/input/dcm2niix_input/{filename.split('/')[-1]}"

                try:
                    with open(infile, "r") as f:
                        log.debug(
                            f"{infile} opened from path separated dcm2niix_input."
                        )
                except FileNotFoundError:
                    log.error("Unable to open dcm2niix_input. Exiting.")
                    os.sys.exit(1)

        gear_args = {
            "infile": infile,
            "work_dir": gear_context.work_dir,
            "remove_incomplete_volumes": gear_context.config[
                "remove_incomplete_volumes"
            ],
            "decompress_dicoms": gear_context.config["decompress_dicoms"],
            "rec_infile": None,
        }

        if gear_context.get_input_path("rec_file_input"):

            rec_infile = Path(gear_context.get_input_path("rec_file_input"))
            if rec_infile.is_file():
                gear_args["rec_infile"] = rec_infile
            else:
                log.error(
                    "Configuration for rec_infile_input is not a valid path. Exiting."
                )
                os.sys.exit(1)

    elif FLAG == "dcm2niix":

        # Notice the explicit 'y' for bids_sidecar, in order to capture metadata; the
        # user-defined config option setting wil be considered during the gear resolve stage.
        filename = gear_context.config["filename"]
        filename = filename.replace(" ", "_")

        comment = gear_context.config["comment"]
        if len(comment) > 24:
            log.error(
                f"The comment configuration option must be less than 25 characters. You have entered {len(comment)} characters. Please edit and resubmit Gear. Exiting."
            )
            os.sys.exit(1)

        gear_args = {
            "anonymize_bids": gear_context.config["anonymize_bids"],
            "bids_sidecar": "y",
            "comment": comment,
            "compress_nifti": gear_context.config["compress_nifti"],
            "compression_level": gear_context.config["compression_level"],
            "convert_only_series": gear_context.config["convert_only_series"],
            "crop": gear_context.config["crop"],
            "filename": filename,
            "ignore_derived": gear_context.config["ignore_derived"],
            "ignore_errors": gear_context.config["ignore_errors"],
            "lossless_scaling": gear_context.config["lossless_scaling"],
            "merge2d": gear_context.config["merge2d"],
            "output_nrrd": gear_context.config["output_nrrd"],
            "philips_scaling": gear_context.config["philips_scaling"],
            "single_file_mode": gear_context.config["single_file_mode"],
            "text_notes_private": gear_context.config["text_notes_private"],
            "verbose": gear_context.config["dcm2niix_verbose"],
        }

        # Anonymization cascade
        if gear_context.config["pydeface"]:
            gear_args["anonymize_bids"] = True
            gear_args["text_notes_private"] = False

    elif FLAG == "pydeface":

        gear_args = {
            "pydeface_cost": gear_context.config["pydeface_cost"],
            "template": None,
            "facemask": None,
            "pydeface_nocleanup": gear_context.config["pydeface_nocleanup"],
            "pydeface_verbose": gear_context.config["pydeface_verbose"],
        }

        if gear_context.get_input_path("pydeface_template"):
            pydeface_template = Path(gear_context.get_input_path("pydeface_template"))
            if pydeface_template.is_file():
                gear_args["template"] = pydeface_template
                log.info(f"Found input template for pydeface: {gear_args['template']}")
            else:
                log.error(
                    "Configuration for pydeface_template is not a valid path. Exiting."
                )
                os.sys.exit(1)
        else:
            log.info("No input template provided for pydeface. Defaults assumed.")

        if gear_context.get_input_path("pydeface_facemask"):
            pydeface_facemask = Path(gear_context.get_input_path("pydeface_facemask"))
            if pydeface_facemask.is_file():
                gear_args["facemask"] = pydeface_facemask
                log.info(f"Found input facemask for pydeface: {gear_args['facemask']}")
            else:
                log.error(
                    "Configuration for pydeface_facemask is not a valid path. Exiting."
                )
                os.sys.exit(1)
        else:
            log.info("No input facemask provided for pydeface. Defaults assumed.")

    elif FLAG == "resolve":

        gear_args = {
            "ignore_errors": gear_context.config["ignore_errors"],
            "retain_sidecar": True,
            "retain_nifti": True,
            "output_nrrd": gear_context.config["output_nrrd"],
            "pydeface_intermediaries": False,
            "classification": None,
            "modality": None,
        }

        if gear_context.config["bids_sidecar"] == "n":
            gear_args["retain_sidecar"] = False

        if gear_context.config["bids_sidecar"] == "o":
            gear_args["retain_nifti"] = False

        if gear_context.config["pydeface_nocleanup"]:
            gear_args["pydeface_intermediaries"] = True

        if gear_context.config["output_nrrd"]:
            gear_args["retain_nifti"] = False

        try:
            classification = (
                gear_context.config_json.get("inputs", {})
                .get("dcm2niix_input", {})
                .get("object", {})
                .get("classification")
            )
            # If modality is set and classification is not set, classification returned as {'Custom':[]}
            # If modality and classification are not set, classification returned as {}
            if classification != {} and classification != {"Custom": []}:
                gear_args["classification"] = classification
        except KeyError:
            log.info("Cannot determine classification from configuration.")

        try:
            gear_args["modality"] = (
                gear_context.config_json.get("inputs", {})
                .get("dcm2niix_input", {})
                .get("object", {})
                .get("modality")
            )
        except KeyError:
            log.info("Cannot determine modality from configuration.")

    gear_args_formatted = pprint.pformat(gear_args)
    log.info(f"Prepared gear stage arguments: \n\n{gear_args_formatted}\n")

    return gear_args
