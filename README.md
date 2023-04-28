# RHUH-GBM dataset MRI Preprocessing Pipepline

This repository contains the code for preprocessing magnetic resonance imaging (MRI) scans of glioblastomas as described in the following paper:

> The Río Hortega University Hospital Glioblastoma Dataset: A Comprehensive Collection of Preoperative, Early Postoperative, and Recurrence MRI Scans (RHUH-GBM)
> Santiago Cepeda, Sergio García-García, Ignacio Arrese, Francisco Herrero, Trinidad Escudero, Tomás Zamora, Rosario Sarabia. (2023)
> Preprint available at [arXiv](https://arxiv.org/).

![readme](https://user-images.githubusercontent.com/87584415/235226079-a62138a8-bd02-4c4c-b35d-8ff026588802.jpg)
The code is designed for use on Ubuntu systems and assumes that certain dependencies are already installed and added to the system path.

## Expected Folder Structure

The expected folder structure should be as follows:

I apologize for the confusion. Here's the complete content in a single Markdown block:

markdown

# RHUH-GBM MRI Preprocessing Repository

This repository contains the code for preprocessing magnetic resonance imaging (MRI) scans of glioblastomas as described in the following paper:

> The Río Hortega University Hospital Glioblastoma Dataset: A Comprehensive Collection of Preoperative, Early Postoperative, and Recurrence MRI Scans (RHUH-GBM)
> Santiago Cepeda, Sergio García-García, Ignacio Arrese, Francisco Herrero, Trinidad Escudero, Tomás Zamora, Rosario Sarabia. (2023)
> Preprint available at [arXiv](https://arxiv.org/).

The code is designed for use on Ubuntu systems and assumes that certain dependencies are already installed and added to the system path.

## Expected Folder Structure
```
The expected folder structure should be as follows:
Main_folder
├─ Subject_001
│ ├─ 0
│ │ ├─ adc
│ │ ├─ t1
│ │ ├─ t1ce
│ │ ├─ t2
│ │ └─ flair
│ ├─ 1
│ │ ├─ adc
│ │ ├─ t1
│ │ ├─ t1ce
│ │ ├─ t2
│ │ └─ flair
│ └─ 2
│ ├─ adc
│ ├─ t1
│ ├─ t1ce
│ ├─ t2
│ └─ flair
├─ Subject_002
├─ Subject_003
└─ ...
```
In the structure above, subfolder `0` represents the preoperative scan, `1` represents the early postoperative scan, and `2` represents the follow-up scan. The presence of all three time-points is not mandatory.

Subfolders `adc`, `t1`, `t1ce`, `t2`, and `flair` should contain the DICOM files.

## Pipeline Overview

The preprocessing pipeline consists of the following steps:

1. DICOM to NiFTI conversion using `dcm2niix`
2. Register `t1ce.nii.gz` to SRI atlas image using `FLIRT`
3. Coregister `t1.nii`, `t2.nii.gz`, `flair.nii.gz`, and `adc.nii.gz` to the transformed `t1ce.nii.gz` using `FLIRT`
4. Perform skull stripping on the coregistered volumes using MRI Synthstrip from Freesurfer
5. Normalize the intensity of the volumes by z-score using CaPTK
