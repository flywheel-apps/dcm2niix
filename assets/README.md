### Data Sources
Data to test arrange.py captured from nibabel package
Data to test pydeface.py captured from pydeface package
Data to test dcm2niix captured from https://www.aliza-dicom-viewer.com/download/datasets

### Valid Dataset Comparisons
The valid_dataset subdirectory contains four sets of valid output directories. Note the first subdirectory in each of these would be the dcm2niix_input_dir for the gear. Therefore, dicom_single has a subdirectory of dicom_single because that is what we are testing in comparison. The first subdirectory inside the valid_dataset (i.e., dicom_single) indicates which directory to be comparing to for pytest.
