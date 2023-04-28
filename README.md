RHUH-GBM MRI Preprocessing Repository

This repository contains the code for preprocessing magnetic resonance imaging (MRI) scans of glioblastomas as described in the following paper:

The Río Hortega University Hospital Glioblastoma Dataset: A Comprehensive Collection of Preoperative, Early Postoperative, and Recurrence MRI Scans (RHUH-GBM)
Santiago Cepeda, Sergio García-García, Ignacio Arrese, Francisco Herrero, Trinidad Escudero, Tomás Zamora, Rosario Sarabia. (2023)
Preprint available at arXiv.

The code is designed for use on Ubuntu systems and assumes that certain dependencies are already installed and added to the system path.
Expected Folder Structure

The expected folder structure should be as follows:

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

In the structure above, subfolder 0 represents the preoperative scan, 1 represents the early postoperative scan, and 2 represents the follow-up scan. The presence of all three time-points is not mandatory.

Subfolders adc, t1, t1ce, t2, and flair should contain the DICOM files.
Pipeline Overview

The preprocessing pipeline consists of the following steps:

    DICOM to NiFTI conversion using dcm2niix
    Register t1ce.nii.gz to SRI atlas image using FLIRT
    Coregister t1.nii, t2.nii.gz, flair.nii.gz, and adc.nii.gz to the transformed t1ce.nii.gz using FLIRT
    Perform skull stripping on the coregistered volumes using MRI Synthstrip from Freesurfer
    Normalize the intensity of the volumes by z-score using CaPTK

Installation and Usage

    Clone the repository:

bash

git clone https://github.com/your_username/RHUH-GBM-MRI-Preprocessing.git
cd RHUH-GBM-MRI-Preprocessing

    Install the dependencies:
        dcm2niix
        FSL
        FreeSurfer
        CaPTK

    Follow the folder structure as described above.

    Run the preprocessing pipeline using the following command:

bash

bash preprocess.sh path_to_subject_folder

Replace path_to_subject_folder with the path to the subject folder as per the expected folder structure.

Note: The pipeline assumes that you have a multi-core machine. If not, modify the -omp flag in MRI_SynthStrip and `mri
