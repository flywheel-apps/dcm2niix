# dcm2niix gear - DICOM to NIfTI conversion using dcm2niix with optional implementation of PyDeface.

A [Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) for implementing [Chris Rorden's dcm2niix](https://github.com/rordenlab/dcm2niix) for converting DICOM to NIfTI, with optional implementation of [Poldrack Lab's PyDeface](https://github.com/poldracklab/pydeface) to remove facial structures from NIfTI.

## Description

[Chris Rorden's dcm2niix](https://github.com/rordenlab/dcm2niix) is a popular tool for converting images from the complicated formats used by scanner manufacturers (DICOM, PAR/REC) to the NIfTI format used by many scientific tools. dcm2niix works for all modalities (CT, MRI, PET, SPECT) and sequence types. The [Poldrack Lab's PyDeface](https://github.com/poldracklab/pydeface) is a popular tool for removing facial structures from NIfTI.

### Gear Inputs

#### Required
* **dcm2niix_input**: Input file for dcm2niix. This can be either a DICOM archive (.dicom.zip), a PAR/REC archive (.parrec.zip), or a single PAR file (image.PAR).

#### Optional
* **rec_file_input**: If dcm2niix_input is a single PAR file, the corresponding REC file ('image.REC') for one par/rec file pair as inputs to dcm2niix.
* **pydeface_template**: If implementing PyDeface, optional template image that will be used as the registration target instead of the default.
* **pydeface_facemask**: If implementing PyDeface, optional face mask image that will be used instead of the default.

### Config Settings

#### dcm2niix
* **anonymize_bids**: Anonymize BIDS. Options: true (default), false. 'bids_sidecar' config option must be enabled (i.e., 'y' or 'o' options).
* **bids_sidecar**: Output BIDS sidecar in JSON format. Options are 'y'=yes, 'n'=no (default), 'o'=only (whereby no NIfTI file will be generated).
* **compress_nifti**: Compress output NIfTI file. Options: 'y'=yes (default), 'n'=no, '3'=no,3D. If option '3' is chosen, the filename flag will be set to '-f %p_%s' to prevent overwriting files.
* **compression_level**: Set the gz compression level. Options: 1 (fastest) to 9 (smallest), 6 (default).
* **convert_only_series**: Selectively convert by series number - can be used up to 16 times. Options: 'all' (default), space-separated list of series numbers (e.g., '2 12 20'). WARNING: Expert Option. We trust that if you have selcted this option you know what you are asking for.
* **crop**: Crop 3D T1 images. Options: true, false (default).
* **filename**: Output filename template (%a=antenna (coil) number, %c=comments, %d=description, %e=echo number, %f=folder name, %i=ID of patient, %j=seriesInstanceUID, %k=studyInstanceUID, %m=manufacturer, %n=name of patient, %p=protocol, %s=series number, %t=time, %u=acquisition number, %v=vendor, %x=study ID; %z=sequence name). '%f' (default).
* **ignore_derived**: Ignore derived, localizer, and 2D images. Options: true, false (default).
* **ignore_errors**: Ignore dcm2niix errors and exit status, and preserve outputs. Options: true, false (default). By default, when dcm2niix exits non-zero, outputs are not preserved.
* **lossless_scaling**: Losslessly scale 16-bit integers to use dynamic range. Options: true, false (default).
* **merge2d**: Merge 2D slices from same series regardless of study time, echo, coil, orientation, etc. Options: true, false (default).
* **philips_scaling**: Philips precise float (not display) scaling. Options: true (default), false.
* **single_file_mode**: Single file mode, do not convert other images in folder. Options: true, false (default).
* **text_notes_private**: Text notes including private patient details. Options: true, false (default).

#### PyDeface
* **pydeface**: Implement PyDeface to remove facial structures from NIfTI. Only defaced NIfTIs will be included in the output. Options: true, false (default).
* **pydeface_cost**: If implementing PyDeface, the FSL-Flirt cost function. Options: 'mutualinfo' (default), 'corratio', 'normcorr', 'normal', 'leastsq', 'labeldiff', 'bbr'.
* **pydeface_nocleanup**: If implementing PyDeface, do not clean up temporary files. Options: true, false (default).
* **pydeface_verbose**: If implementing PyDeface, show additional status prints. Options: true, false (default).

#### Other
* **coil_combine**: For sequences with individual coil data, saved as individual volumes, this option will save a NIfTI file with ONLY the combined coil data (i.e., the last volume). Options: true, false (default). WARNING: Expert Option. We make no effort to check for independent coil data, we simply trust that if you have selcted this option you know what you are asking for.
* **decompress_dicoms**: Decompress DICOM files prior to conversion. This will perform decompression using gdcmconv and then perform conversion using dcm2niix. Options: true, false (default).
* **remove_incomplete_volumes**: Remove incomplete trailing volumes for 4D scans aborted mid-acquisition before dcm2niix conversion. Options: true, false (default).
* **vol3D**: Output 3D uncompressed volumes. Options: true, false (default). If true, the filename flag will be set to '-f %p_%s' to prevent overwriting files.
