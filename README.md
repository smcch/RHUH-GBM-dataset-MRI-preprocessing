RHUH-GBM MRI Preprocessing Repository 🧠

This repository contains the code for preprocessing MRI scans of glioblastomas, as described in the paper "The Río Hortega University Hospital Glioblastoma Dataset: A Comprehensive Collection of Preoperative, Early Postoperative, and Recurrence MRI Scans (RHUH-GBM)" by Santiago Cepeda et al. The goal of this code is to preprocess the scans to prepare them for downstream analysis, such as brain tumor subregions segmentation.
Expected Folder Structure

The expected folder structure should follow the format shown below:

lua
Main_folder
|-- Subject_001
|   |-- 0
|   |   |-- adc
|   |   |-- t1
|   |   |-- t1ce
|   |   |-- t2
|   |   `-- flair
|   |-- 1
|   |   |-- adc
|   |   |-- t1
|   |   |-- t1ce
|   |   |-- t2
|   |   `-- flair
|   `-- 2
|       |-- adc
|       |-- t1
|       |-- t1ce
|       |-- t2
|       `-- flair
|-- Subject_002
|-- Subject_003
`-- ...

In this structure, each subject has a folder with subfolders named 0, 1, and 2. Subfolder 0 represents the preoperative scan, 1 represents the early postoperative scan, and 2 represents the follow-up scan. However, the presence of all three time-points is not mandatory. The subfolders adc, t1, t1ce, t2, and flair should contain the DICOM files.
Pipeline Overview

The preprocessing pipeline consists of the following steps:

    DICOM to NiFTI conversion using dcm2niix
    Register t1ce.nii.gz to SRI atlas image using FLIRT
    Coregister t1.nii, t2.nii.gz, flair.nii.gz, and adc.nii.gz to the transformed t1ce.nii.gz using FLIRT
    Perform skull stripping on the coregistered volumes using MRI Synthstrip from Freesurfer
    Normalize the intensity of the volumes by z-score using CaPTK

License

This project is licensed under the MIT License. Please refer to the LICENSE file for more details.

Lastly, this preprocessing code is a useful tool for preparing the MRI scans of glioblastomas for downstream analysis, such as brain tumor subregions segmentation using DeepMedic. The resulting labels include necrosis, peritumor (edema + non-enhancing tumor), and enhancing tumor.
