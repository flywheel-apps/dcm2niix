"""Function to parse gear config into gear args."""

import logging


log = logging.getLogger(__name__)


def generate_gear_args(gear_context, FLAG):

    if FLAG == "prepare":

        gear_args = {
            "infile": gear_context.get_input_path("dcm2niix_input"),
            "work_dir": gear_context.work_dir,
            "remove_incomplete_volumes": gear_context.config[
                "remove_incomplete_volumes"
            ],
            "decompress_dicoms": gear_context.config["decompress_dicoms"],
            "rec_infile": None,
        }

        if gear_context.get_input_path("rec_file_input"):
            gear_args["rec_infile"] = gear_context.get_input_path("rec_file_input")

    elif FLAG == "dcm2niix":
        log.info("Establishing inputs for dcm2niix.")

        # ??? should the default filename include acquisition for BIDS purposes?
        # ??? e.g., %f_%d, which includes the input folder name and series description
        # notice, explicit 'y' for bids_sidecar for capturinge metadata
        # config option setting considered during gear resolve
        gear_args = {
            "anonymize_bids": gear_context.config["anonymize_bids"],
            "bids_sidecar": "y",
            "compress_nifti": gear_context.config["compress_nifti"],
            "compression_level": gear_context.config["compression_level"],
            "convert_only_series": gear_context.config["convert_only_series"],
            "crop": gear_context.config["crop"],
            "filename": gear_context.config["filename"],
            "ignore_derived": gear_context.config["ignore_derived"],
            "ignore_errors": gear_context.config["ignore_errors"],
            "lossless_scaling": gear_context.config["lossless_scaling"],
            "merge2d": gear_context.config["merge2d"],
            "philips_scaling": gear_context.config["philips_scaling"],
            "single_file_mode": gear_context.config["single_file_mode"],
            "text_notes_private": gear_context.config["text_notes_private"],
        }

        if gear_context.config["vol3D"]:
            gear_args["compress_nifti"] = "3"

        # anonymization cascade
        if gear_context.config["pydeface"]:
            gear_args["anonymize_bids"] = True
            gear_args["text_notes_private"] = False

    elif FLAG == "pydeface":
        log.info("Establishing inputs for pydeface.")

        gear_args = {
            "pydeface_cost": gear_context.config["pydeface_cost"],
            "template": None,
            "facemask": None,
            "pydeface_nocleanup": gear_context.config["pydeface_nocleanup"],
            "pydeface_verbose": gear_context.config["pydeface_verbose"],
        }

        if gear_context.get_input_path("pydeface_template"):
            gear_args["template"] = gear_context.get_input_path("pydeface_template")
            log.info(f"Found input template for pydeface: {gear_args['template']}")
        else:
            log.info("No input template provided for pydeface. Defaults assumed.")

        if gear_context.get_input_path("pydeface_facemask"):
            gear_args["facemask"] = gear_context.get_input_path("pydeface_facemask")
            log.info(f"Found input facemask for pydeface: gear_args['facemask']")
        else:
            log.info("No input facemask provided for pydeface. Defaults assumed.")

    elif FLAG == "resolve":
        log.info("Establishing inputs to resolve gear execution.")

        gear_args = {
            "ignore_errors": gear_context.config["ignore_errors"],
            "retain_sidecar": True,
            "retain_nifti": True,
            "pydeface_intermediaries": False,
            "classification": [],
            "modality": None,
        }

        if gear_context.config["bids_sidecar"] == "n":
            gear_args["retain_sidecar"] = False

        if gear_context.config["bids_sidecar"] == "o":
            gear_args["retain_niftis"] = False

        if gear_context.config["pydeface_nocleanup"]:
            gear_args["pydeface_intermediaries"] = True

        try:
            gear_args["classification"] = gear_context.config["inputs"][
                                             "dcm2niix_input"]["object"]["classification"]
        except:
            log.info("Cannot determine classification from configuration.")

        try:
            gear_args["modality"] = gear_context.config["inputs"][
                                       "dcm2niix_input"]["object"]["modality"]
        except:
            log.info("Cannot determine modality from config.json.")

    return gear_args
