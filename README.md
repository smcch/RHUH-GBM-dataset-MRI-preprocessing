# RHUH-GBM dataset MRI Preprocessing Pipepline

This repository contains the code for preprocessing magnetic resonance imaging (MRI) scans of glioblastomas as described in the following paper:

> The Río Hortega University Hospital Glioblastoma Dataset: A Comprehensive Collection of Preoperative, Early Postoperative, and Recurrence MRI Scans (RHUH-GBM)
> Santiago Cepeda, Sergio García-García, Ignacio Arrese, Francisco Herrero, Trinidad Escudero, Tomás Zamora, Rosario Sarabia. (2023)
> Preprint available at [arXiv](https://arxiv.org/abs/2305.00005).

![readme](https://user-images.githubusercontent.com/87584415/235226079-a62138a8-bd02-4c4c-b35d-8ff026588802.jpg)


The code is designed for use on Linux and Mac OS and assumes that certain dependencies are already installed and added to the system path.

## Expected Folder Structure
```
The expected folder structure should be as follows:
Input_folder
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
6. Tumor subregions segementation by DeepMedic

## Output Files

The pipeline produces the following output files in NiFTI format:

- `t1.nii.gz`: T1-weighted MRI volume.
- `t1ce.nii.gz`: T1-weighted MRI volume with contrast enhancement.
- `t2.nii.gz`: T2-weighted MRI volume.
- `flair.nii.gz`: Fluid-attenuated inversion recovery (FLAIR) MRI volume.
- `adc.nii.gz`: Apparent diffusion coefficient (ADC) MRI volume.

In addition, the pipeline generates a file named `segmentations.nii.gz`, which includes three labels:

- `1`: Necrosis.
- `2`: Peritumoral region.
- `4`: Enhancing tumor.

## How to Run and Clone the Pipeline

To run the pipeline, please follow these instructions:

1. Clone the repository to your local machine using the following command:
    ```
    git clone https://github.com/yourusername/rhuh-gbm-mri-preprocessing.git
    ```
    Replace `yourusername` with your GitHub username.

2. Install the necessary dependencies:
    - `dcm2niix`
    - `FSL`
    - `FreeSurfer v7.3.2`
    - `CaPTk v1.8.0`

    You can install these dependencies using your package manager or by following the instructions on their respective websites.

3. Edit the `final_pipeline.sh` script to include the correct paths for the `main_folder`, `atlas_image`, and `deep_medic_model` variables. Open the script using a text editor and change the paths accordingly:
    ```
    main_folder="insert_the_path"
    atlas_image="insert_the_path/atlasImage.nii.gz"
    deep_medic_model="insert_the_path/brainTumorSegmentation"
    ```

4. Save and close the file.

5. Navigate to the `rhuh-gbm-mri-preprocessing` directory and run the `final_pipeline.sh` script from the Ubuntu terminal:
    ```
    cd rhuh-gbm-mri-preprocessing
    ./final_pipeline.sh
    ```

Note: The pipeline assumes that your folder structure follows the expected structure mentioned in the README.

To clone the repository using the command line, you will need to have `git` installed on your system. If you do not have `git` installed, you can download it from https://git-scm.com/downloads.

Alternatively, you can also download the repository as a ZIP file by clicking on the green "Code" button on the repository's main page and selecting "Download ZIP". 

## Updated version

Alternatively, you have the option to utilize an updated version of the pipeline that incorporates SimpleElastix, a faster registration method, instead of FLIRT. Additionally, this version includes a function for calculating the apparent diffusion coefficient (ADC) if ADC images are not available, allowing you to use DWI raw files as input.

## Command Line Usage

Alternatively, you have the option to utilize an updated version of the pipeline that incorporates SimpleElastix for image coregistration instead of FLIRT.

1. To run DeepMedic via CapTK you should follow some instructions to solve FUSE errors https://cbica.github.io/CaPTk/gs_FAQ.html

```
#!/bin/bash
~/CaPTk/${version}/captk --appimage-extract
export PATH=~/CaPTk/1.8.1/squashfs-root/usr/bin:$PATH
export LD_LIBRARY_PATH=~/CaPTk/1.8.1/squashfs-root/usr/lib:$LD_LIBRARY_PATH
```

2. Navigate to the project directory.

```
cd your-repository
```

2. Run the pipeline using the following command:

```
python preprocess_mri.py -i /path_to_input -o /path_to_output
```
## GUI Usage

If you prefer a graphical user interface (GUI), you can use the following instructions:

1. Launch the GUI application by running the following command:

```
python gui.py
```


![Sin título](https://github.com/smcch/RHUH-GBM-dataset-MRI-preprocessing/assets/87584415/2a626cca-43e6-4df2-9846-b89dc15ced2c)


1. Use the provided graphical interface to configure the input and output directories.

2. Click the "Run" button to start the pipeline execution.

Please note that both the command line and GUI versions of the pipeline require proper installation and configuration of the dependencies before use.

## Expected output
```
Output_folder
├─ Subject_001
│ ├─ 0
│ │ ├─ adc.ni.gz
│ │ ├─ t1.nii.gz
│ │ ├─ t1ce.nii.gz
│ │ ├─ t2.nii.gz
│ │ └─ flair.nii.gz
│ │ └─ segmentations.nii.gz
│ │ └─ peritumor.nii.gz
│ │ └─ tumor.nii.gz
```

## Citations

If you find this pipeline useful for your academic purposes, please include the following citations:

- DICOM to NiFTI converter: `dcm2niix`, available at https://github.com/rordenlab/dcm2niix/releases/tag/v1.0.20220720
	- Li X, Morgan PS, Ashburner J, Smith J, Rorden C. The first step for neuroimaging data analysis: DICOM to NIfTI conversion. J Neurosci Methods. 2016;264:47-56. doi:10.1016/j.jneumeth.2016.03.001.

- Registration: `FLIRT` (FMRIB's Linear Image Registration Tool), available at https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSL
	- Jenkinson M, Smith S. A global optimisation method for robust affine registration of brain images. Med Image Anal. 2001;5(2):143-156. doi:10.1016/s1361-8415(01)00036-6.
	- Jenkinson M, Bannister P, Brady M, Smith S. Improved optimization for the robust and accurate linear registration and motion correction of brain images. Neuroimage. 2002;17(2):825-841. doi:10.1016/s1053-8119(02)91132-8.

- Resitration: `SimpleElastix`https://simpleelastix.github.io/
	- K. Marstal, F. Berendsen, M. Staring and S. Klein, "SimpleElastix: A user-friendly, multi-lingual library for medical image registration," International Workshop on Biomedical Image Registration (WBIR), IEEE Conference on Computer Vision and Pattern Recognition Workshops, pp. 574 - 582, July 2016.

- Skull stripping: `MRI Synthstrip`, included in FreeSurfer v7.3.0, available at https://github.com/freesurfer/freesurfer/tree/dev/mri_synthstrip
	- Hoopes A, Mora JS, Dalca A V, Fischl B, Hoffmann M. SynthStrip: skull-stripping for any brain image. Neuroimage. 2022;260:119474. doi:10.1016/j.neuroimage.2022.119474.

- Cancer Imaging Phenomics Toolkit (`CaPTk`) v1.9.0, available at https://www.nitrc.org/projects/captk/
	- Davatzikos C, Rathore S, Bakas S, et al. Cancer imaging phenomics toolkit: quantitative imaging analytics for precision diagnostics and predictive modeling of clinical outcome. J Med imaging (Bellingham, Wash). 2018;5(1):011018. doi:10.1117/1.JMI.5.1.011018.

- Segmentation: `DeepMedic`, available at https://github.com/deepmedic/deepmedic
	- Kamnitsas K, Ledig C, Newcombe VFJ, et al. Efficient multi-scale 3D CNN with fully connected CRF for accurate brain lesion segmentation. Med Image Anal. 2017;36:61-78. doi:10.1016/j.media.2016.10.004.

