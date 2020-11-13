"""Function to implement dcm2niix."""

import logging
import os
from distutils import util

from nipype.interfaces.dcm2nii import Dcm2niix


logging.getLogger("nipype.interface").setLevel("CRITICAL")
log = logging.getLogger(__name__)


def convert_directory(
    source_dir,
    output_dir,
    anonymize_bids=True,
    bids_sidecar="y",
    comment="",
    compress_nifti="y",
    compression_level=6,
    convert_only_series="all",
    crop=False,
    filename="%f_%p_%t_%s",
    ignore_derived=False,
    ignore_errors=False,
    lossless_scaling=False,
    merge2d=False,
    output_nrrd=False,
    philips_scaling=True,
    single_file_mode=False,
    text_notes_private=False,
    verbose=False,
):
    """Run dcm2niix.

    Args:
        source_dir (str): The absolute path to the output directory containing
            the files from the input(s).
        output_dir (str): The absolute path to the output directory to place the
            converted results.
        anonymize_bids (bool): If true, anonymize sidecar.
        bids_sidecar (str): Output sidecar; 'y'=yes, 'n'=no, 'o'=only
            (whereby no NIfTI file will be generated).
        comment (str): If non-empty, store comment as NIfTI aux_file
            (up to 24 characters).
        compress_nifti (str): Compress output NIfTI file; 'y'=yes, 'i'=internal,
            'n'=no, '3'=no,3D. If option '3' is chosen, the filename flag will
            be set to '-f %p_%s' to prevent overwriting files.
        compression_level (int): Set the gz compression level: 1 (fastest) to
            9 (smallest).
        convert_only_series (str): Space-separated list of series numbers to convert or
            default 'all'. WARNING: Expert Option.
        crop (bool): If true, crop 3D T1 images.
        filename (str): Output filename template for dcm2niix command.
        ignore_derived (bool): If true, ignore derived, localizer, and 2D images.
        ignore_errors (bool): If true, ignore dcm2niix errors and exit status,
            and preserve outputs.
        lossless_scaling (str): Losslessly scale 16-bit integers to use dynamic
            range. Options: 'y'=scale, 'n'=no, but unit16->int16 (default),
            'o'=original.",
        merge2d (bool): If true, merge 2D slices from same series
            regardless of echo, exposure, etc.
        output_nrrd (bool): If true, export as NRRD instead of NIfTI.
        philips_scaling (bool): If true, Philips precise float (not display) scaling.
        single_file_mode (bool): If true, single file mode, do not convert other
            images in folder.
        text_notes_private (bool): If true, retain text notes including
            private patient details.
        verbose (bool): If true, verbose output from dcm2niix call.

    Returns:
        output (nipype.interfaces.base.support.InterfaceResult): The dcm2niix
            output results.

    """
    try:

        converter = Dcm2niix()
        log.info(f"Starting dcm2niix {converter.version}")
        log.info(f"Submitting {len(os.listdir(source_dir))} DICOMs.")

        converter.inputs.source_dir = source_dir
        converter.inputs.output_dir = output_dir

        # dcm2niix command configurations for: anonymize_bids, bids_sidecar
        if bids_sidecar == "o":
            converter.inputs.bids_format = True
            converter.inputs.anon_bids = anonymize_bids
        elif bool(util.strtobool(bids_sidecar)):
            converter.inputs.bids_format = True
            converter.inputs.anon_bids = anonymize_bids
        else:
            log.info("The BIDS sidecar file will not be generated.")
            converter.inputs.bids_format = False

        # dcm2niix command configurations for: comment
        if comment and (len(comment) < 25):
            converter.inputs.comment = comment

        # dcm2niix command configurations for: compress nifti
        if str(compress_nifti) == "3":
            log.info(
                "Outputs will be saved as uncompressed 3D volumes. \
                       \nFilename will be set to %p_%s to prevent overwritting files."
            )
            filename = "%p_%s"

        if str(compress_nifti) in ["y", "i", "n", "3"]:
            converter.inputs.compress = str(compress_nifti)

        # dcm2niix command configurations for: compression_level
        if (
            (compression_level > 0)
            and (compression_level < 10)
            and isinstance(compression_level, int)
        ):
            converter.inputs.compression = compression_level
        else:
            log.error(
                "Configuration option error: compression_level must be between 1 and 9. Exiting."
            )
            os.sys.exit(1)

        # dcm2niix command configurations for: convert_only_series
        if convert_only_series != "all":
            log.warning(
                "Expert Option (convert_only_series). "
                "We trust that since you have selected this option "
                "you know what you are asking for. "
                "Continuing."
            )

            # See: https://www.nitrc.org/forum/forum.php?thread_id=11134&forum_id=4703
            converter.inputs.series_numbers = convert_only_series

        # dcm2niix command configurations for: crop
        converter.inputs.crop = crop

        # dcm2niix command configurations for: filename
        converter.inputs.out_filename = filename.replace(" ", "_")

        # dcm2niix command configurations for: ignore_derived
        converter.inputs.ignore_deriv = ignore_derived

        # dcm2niix command configurations for: lossless_scaling
        if lossless_scaling in ["y", "n", "o"]:
            converter.inputs.args = f"-l {lossless_scaling}"

        # dcm2niix command configurations for: merge2d
        converter.inputs.merge_imgs = merge2d

        # dcm2niix command configurations for: output_nrrd
        converter.inputs.to_nrrd = output_nrrd

        # dcm2niix command configurations for: philips_scaling
        converter.inputs.philips_float = philips_scaling

        # dcm2niix command configurations for: single_file_mode
        converter.inputs.single_file = single_file_mode

        # dcm2niix command configurations for: text_notes_private
        converter.inputs.has_private = text_notes_private

        # dcm2niix command configurations for: verbose
        converter.inputs.verbose = verbose

        # Log the dcm2niix command configuration and run
        log.info(f"Command to be executed: \n\n{converter.cmdline}\n")
        output = converter.run()

        log.info(f"Output from dcm2niix: \n\n{output.runtime.stdout }\n")

        # If error from dcm2niix software, then raise exception
        if int(output.runtime.returncode) == 1:
            raise Exception("The dcm2niix software pacakage returned an error.")
        else:
            log.info("Finished dcm2niix conversion.")

    except Exception as e:

        log.error("Did not complete dcm2niix conversion. Exiting.")
        log.exception(e, exc_info=False)
        output = None

        # dcm2niix command configurations for: ignore_errors
        if not ignore_errors:
            os.sys.exit(1)

    return output
