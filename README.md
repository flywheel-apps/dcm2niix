
[![CircleCI](https://circleci.com/gh/flywheel-apps/dcm2niix.svg?style=shield)](https://app.circleci.com/pipelines/github/flywheel-apps/dcm2niix)
[![Docker Pulls](https://img.shields.io/docker/pulls/flywheel/dcm2niix.svg)](https://hub.docker.com/r/flywheel/dcm2niix/)


# dcm2niix Gear

A [Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) for implementing [Chris Rorden's dcm2niix](https://github.com/rordenlab/dcm2niix) for converting DICOM (or PAR/REC) to NIfTI (or NRRD), with an optional implementation of [Poldrack Lab's PyDeface](https://github.com/poldracklab/pydeface) to remove facial structures from NIfTI.

## Description

[Chris Rorden's dcm2niix](https://github.com/rordenlab/dcm2niix) is a popular tool for converting images from the complicated formats used by scanner manufacturers (DICOM, PAR/REC) to the NIfTI format used by many scientific tools. Alternatively, this tool also outputs the NRRD format. dcm2niix works for all modalities (CT, MRI, PET, SPECT) and sequence types.

The [Poldrack Lab's PyDeface](https://github.com/poldracklab/pydeface) is a popular tool for removing facial structures from NIfTI.

### Gear Inputs

#### Required
* **dcm2niix_input**: Main input file for the Gear. This can be either a DICOM archive ('<dicom>.zip'), a PAR/REC archive ('<parrec>.zip'), or a single PAR file ('image.PAR' or 'image.par').

#### Optional
* **rec_file_input**: If dcm2niix_input is a single PAR file, the corresponding REC file ('image.REC' or 'image.rec') for one PAR/REC file pair as inputs to the Gear.
* **pydeface_template**: If implementing PyDeface, optional template image that will be used as the registration target instead of the default.
* **pydeface_facemask**: If implementing PyDeface, optional face mask image that will be used instead of the default.

### Config Settings

#### dcm2niix
* **anonymize_bids**: Anonymize BIDS. Options: true (default), false. **bids_sidecar** config option must be enabled (i.e., 'y' or 'o' options).
* **bids_sidecar**: Output BIDS sidecar in JSON format. Options are 'y'=yes, 'n'=no (default), 'o'=only (whereby no NIfTI file will be generated).
        - Note: bids_sidecar is always invoked when running dcm2niix to be used as metadata. User configuration preference is handled after acquiring metadata.

* **comment**: If non-empty, store comment as NIfTI aux_file. Options: non-empty string, 24 characters maximum.
        - Note: The 24 character comment is placed in (1) all NIfTI output files in the aux_file variable. You can use fslhdr to access the NIfTI header data and see this comment; and (2) all JSON files (i.e., BIDS sidecars), which means the comment is stored as metadata for all associated output files and would be included in the **bids_sidecar** file, if invoked.

* **compress_images**: Gzip compress images. Options: 'y'=yes (default), 'i'=internal, 'n'=no, '3'=no,3D.
        - Note: If option '3' is chosen, the filename flag will be set to '-f %p_%s' to prevent overwriting files.
        - Tip: If desire .nrrd output, select 'n'.

* **compression_level**: Set the gz compression level. Options: 1 (fastest) to 9 (smallest), 6 (default).
* **convert_only_series**: Selectively convert by series number - can be used up to 16 times. Options: 'all' (default), space-separated list of series numbers (e.g., `2 12 20`). WARNING: Expert Option. We trust that if you have selected this option you know what you are asking for.
* **crop**: Crop 3D T1 images. Options: true, false (default).
* **dcm2niix_verbose**: Whether to include verbose output from dcm2niix call. Options: true, false (default).
* **filename**: Output filename template. Options: %a=antenna (coil) name, %b=basename, %c=comments, %d=series description, %e=echo number, %f=folder name, %i=ID of patient, %j=seriesInstanceUID, %k=studyInstanceUID, %m=manufacturer, %n=name of patient, %o=mediaObjectInstanceUID, %p=protocol, %r=instance number, %s=series number, %t=time, %u=acquisition number, %v=vendor, %x=study ID, %z=sequence name tag(0018,0024), %q sequence name tag(0018,1020). Defaults: dcm2niix tool `%f_%p_%t_%s` and dcm2niix Gear `%f`.
        - Tip: A more informative filename can be useful for downstream BIDS curation by simply accessing relevant information in the extracted filename. For example, including echo number or protocol.

* **ignore_derived**: Ignore derived, localizer, and 2D images. Options: true, false (default).
* **ignore_errors**: Ignore dcm2niix errors and exit status, and preserve outputs. Options: true, false (default). By default, when dcm2niix exits non-zero, outputs are not preserved. WARNING: Expert Option. We trust that if you have selected this option you know what you are asking for.
* **lossless_scaling**: Losslessly scale 16-bit integers to use dynamic range. Options: 'y'=scale, 'n'=no, but unit16->int16 (default), 'o'=original.
* **merge2d**: Merge 2D slices from same series regardless of study time, echo, coil, orientation, etc. Options: true, false (default).
* **output_nrrd** : Export as NRRD instead of NIfTI. Options: true, false (default).
        - Tip: To export .nrrd, change the **compress_images** config option to 'n'; otherwise, the output will split into two files (.raw.gz and .nhdr).

* **philips_scaling**: Philips precise float (not display) scaling. Options: true (default), false.
* **single_file_mode**: Single file mode, do not convert other images in folder. Options: true, false (default).
* **text_notes_private**: Text notes including private patient details. Options: true, false (default).

#### PyDeface
* **pydeface**: Implement PyDeface to remove facial structures from NIfTI. Only defaced NIfTIs will be included in the output. Options: true, false (default).
* **pydeface_cost**: If implementing PyDeface, the FSL-Flirt cost function. Options: 'mutualinfo' (default), 'corratio', 'normcorr', 'normal', 'leastsq', 'labeldiff', 'bbr'.
* **pydeface_nocleanup**: If implementing PyDeface, do not clean up temporary files. Options: true, false (default).
* **pydeface_verbose**: If implementing PyDeface, show additional status prints. Options: true, false (default).

#### Other
* **coil_combine**: For sequences with individual coil data, saved as individual volumes, this option will save a NIfTI file with ONLY the combined coil data (i.e., the last volume). Options: true, false (default). WARNING: Expert Option. We make no effort to check for independent coil data; we trust that you know what you are asking for if you have selected this option.
* **decompress_dicoms**: Decompress DICOM files before conversion. This will perform decompression using gdcmconv and then perform the conversion using dcm2niix. Options: true, false (default).
* **remove_incomplete_volumes**: Remove incomplete trailing volumes for 4D scans aborted mid-acquisition before dcm2niix conversion. Options: true, false (default).

#### Workflow

![](docs/gear_workflow.svg?raw=true)

#### Metadata

The dcm2niix tool extracts DICOM tags and collates these into a JSON file (i.e., the BIDS sidecar). What is extracted depends on the input data. If present, the following DICOM tags are extracted via the dcm2niix tool and applied as metadata to the output files of the dcm2niix Gear:

	AcquisitionMatrixPE
	AcquisitionNumber
	AcquisitionTime
	BaseResolution
	BodyPartExamined
	CoilString
	ConversionSoftware
	ConversionSoftwareVersion
	DeviceSerialNumber
	EchoTime
	EchoTrainLength
	EffectiveEchoSpacing
	EstimatedEffectiveEchoSpacing
	EstimatedTotalReadoutTime
	FlipAngle
	FrameTimesStart
	ImageComments
	ImageOrientationPatientDICOM
	ImageType
	ImagingFrequency
	InPlanePhaseEncodingDirectionDICOM
	InstitutionAddress
	InstitutionalDepartmentName
	InstitutionName
	InternalPulseSequenceName
	MagneticFieldStrength
	Manufacturer
	ManufacturersModelName
	Modality
	MRAcquisitionType
	ParallelReductionFactorInPlane
	ParallelReductionOutOfPlane
	PartialFourier
	PatientPosition
	PercentPhaseFOV
	PercentSampling
	PhaseEncodingAxis
	PhaseEncodingDirection
	PhaseEncodingPolarityGE
	PhaseEncodingSteps
	PhaseResolution
	PhilipsRescaleIntercept
	PhilipsRescaleSlope
	PhilipsRWVIntercept
	PhilipsRWVSlope
	PixelBandwidth
	ProcedureStepDescription
	ProtocolName
	PulseSequenceDetails
	ReceiveCoilName
	ReconMatrixPE
	RepetitionTime
	SAR
	ScanningSequence
	ScanOptions
	SequenceName
	SequenceVariant
	SeriesDescription
	SeriesNumber
	ShimSetting
	SliceThickness
	SliceTiming
	SoftwareVersions
	SpacingBetweenSlices
	StationName
	TotalReadoutTime
	TxRefAmp
	UsePhilipsFloatNotDisplayScaling
	WaterFatShift

If the Gear inputs are DICOMs, additional metadata is captured. If present, the following DICOM tags are extracted using [Pydicom](https://pydicom.github.io/) and applied as metadata to the output files of the dcm2niix Gear:

	AcquisitionDuration, tag(0018,9073)
	AcquisitionMatrix
	Columns
	InPlanePhaseEncodingDirection
	PercentPhaseFieldOfView
	PercentSampling
	PixelSpacing
	PrepulseDelay, tag(2001,101B)
	PrepulseType, tag(2001,101C)
	Rows
	ScanningTechnique, tag(2001,1020)
	ScanType, tag(2005,10A1)
	SliceOrientation, tag(2001,100B)
	SpacingBetweenSlices
	NumberOfEchos, tag(2001,1014)
	NumberOfSlices, tag(2001,1018)
	NumberOfTemporalPositions

All metadata applied to the output files from the dcm2niix Gear are extracted from the raw DICOM tags. As such, the units of measurement remain consistent with the DICOM standard. To find more information on DICOM, take a look at [NiBabel](https://nipy.org/nibabel/index.html)'s very useful [Introduction to DICOM](https://nipy.org/nibabel/dicom/dicom_intro.html).
