#==============================================================================#
#  Author:       Santiago Cepeda                                               #
#  Copyright:    Río Hortega University Hospital in Valladolid, Spain          #
#                                                                              #
#  This program is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation, either version 3 of the License, or           #
#  (at your option) any later version.                                         #
#                                                                              #
#  This program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#==============================================================================#

# Import libraries
import os
import subprocess
import shutil
import argparse
import nibabel as nib
import numpy as np
import SimpleITK as sitk

# Define the argument parser
parser = argparse.ArgumentParser(description='MRI preprocessing and segmentation.')
parser.add_argument('-i', '--input_dir', help='Input directory containing the MRI data.', required=True)
parser.add_argument('-o', '--output_dir', help='Output directory for the results.', required=True)
args = parser.parse_args()

# Define the paths
main_folder = args.input_dir
atlas_image = '/mnt/c/Users/Santiago/PycharmProjects/MRI/atlastImage.nii.gz'
deep_medic_model='/mnt/c/CaPTk_Full/1.8.1/data/deepMedic/saved_models/brainTumorSegmentation'
output_dir = args.output_dir

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def normalize_intensity(image_path, output_path):
    # Load the image
    img = nib.load(image_path)
    data = img.get_fdata()

    # Compute the mean and standard deviation of the image's intensity
    mean_intensity = np.mean(data)
    std_intensity = np.std(data)

    # Perform the z-score normalization
    data_norm = (data - mean_intensity) / std_intensity

    # Save the normalized image
    img_norm = nib.Nifti1Image(data_norm, img.affine)
    nib.save(img_norm, output_path)

def run_elastix(in_file, reference, out_file):
    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetFixedImage(sitk.ReadImage(reference))
    elastixImageFilter.SetMovingImage(sitk.ReadImage(in_file))
    parameterMapVector = sitk.VectorOfParameterMap()
    parameterMapVector.append(sitk.GetDefaultParameterMap("translation"))
    parameterMapVector.append(sitk.GetDefaultParameterMap("rigid"))
    parameterMapVector.append(sitk.GetDefaultParameterMap("affine"))
    elastixImageFilter.SetParameterMap(parameterMapVector)
    elastixImageFilter.Execute()
    sitk.WriteImage(elastixImageFilter.GetResultImage(), out_file)

def create_tumor_peritumor(segmentations_path, output_dir):
    # Load the segmentations image
    segmentations_img = nib.load(segmentations_path)
    segmentations_data = segmentations_img.get_fdata()

    # Create the tumor mask (excluding label 2 and merging labels 1 and 4)
    tumor_mask = np.logical_or(segmentations_data == 1, segmentations_data == 4).astype(np.uint8)

    # Create the peritumor mask (label 2 only)
    peritumor_mask = (segmentations_data == 2).astype(np.uint8)

    # Save the tumor and peritumor masks as Nifti files
    tumor_img = nib.Nifti1Image(tumor_mask, segmentations_img.affine)
    tumor_path = os.path.join(output_dir, 'tumor.nii.gz')
    nib.save(tumor_img, tumor_path)

    peritumor_img = nib.Nifti1Image(peritumor_mask, segmentations_img.affine)
    peritumor_path = os.path.join(output_dir, 'peritumor.nii.gz')
    nib.save(peritumor_img, peritumor_path)

def compute_adc_dipy(dwiPath, bvalPath, adcPath, rescale_factor=1000):
    # Load bvals
    with open(bvalPath, 'r') as f:
        bvals = np.array([float(bval) for bval in f.read().split()])

    # Load dwi data
    dwi_img = nib.load(dwiPath)
    dwi_data = dwi_img.get_fdata()

    # Split b0 and bX images
    b0_image = dwi_data[..., np.argmin(bvals)]
    bX_image = dwi_data[..., np.argmax(bvals)]
    b = np.max(bvals)

    # Compute ADC
    mask = b0_image > 0
    adc_data = np.zeros_like(b0_image)
    adc_data[mask] = -np.log(bX_image[mask] / b0_image[mask]) / b

    # Handle any numerical issues
    adc_data[np.isinf(adc_data)] = 0
    adc_data[np.isnan(adc_data)] = 0

    # Rescale the ADC values
    adc_data = adc_data * rescale_factor

    # Save ADC data to a Nifti file
    adc_img = nib.Nifti1Image(adc_data, dwi_img.affine)
    nib.save(adc_img, adcPath)

for subject_id in os.listdir(main_folder):
    subject_folder = os.path.join(main_folder, subject_id)
    if not os.path.isdir(subject_folder):
        continue

    time_point_folders = [f for f in os.listdir(subject_folder) if os.path.isdir(os.path.join(subject_folder, f))]
    for time_point in time_point_folders:

        # Task 1: DICOM to Nifti conversion
        for mri_seq in ['t1', 't1ce', 't2', 'flair']:
            input_path = os.path.join(main_folder, subject_id, time_point, mri_seq)
            if not os.path.exists(input_path):
                continue
            output_path = os.path.join(output_dir, subject_id, time_point)
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            subprocess.run(["dcm2niix", "-z", "y", "-m", "n", "-b", "n", "-o", output_path, "-f", mri_seq, input_path])

        # Check for ADC folder
        adc_folder_exists = os.path.exists(os.path.join(main_folder, subject_id, time_point, 'adc'))
        dwi_folder_exists = os.path.exists(os.path.join(main_folder, subject_id, time_point, 'dwi'))

        if adc_folder_exists:
            mri_seq = 'adc'
            input_path = os.path.join(main_folder, subject_id, time_point, mri_seq)
            output_path = os.path.join(output_dir, subject_id, time_point)
            subprocess.run(["dcm2niix", "-z", "y", "-m", "n", "-b", "n", "-o", output_path, "-f", mri_seq, input_path])
        elif dwi_folder_exists:
            mri_seq = 'dwi'
            input_path = os.path.join(main_folder, subject_id, time_point, mri_seq)
            output_path = os.path.join(output_dir, subject_id, time_point)
            subprocess.run(["dcm2niix", "-z", "y", "-m", "n", "-b", "n", "-o", output_path, "-f", mri_seq, input_path])
            # Task 1.1: DWI to ADC
            compute_adc_dipy(
                dwiPath=os.path.join(output_dir, subject_id, time_point, 'dwi.nii.gz'),
                bvalPath=os.path.join(output_dir, subject_id, time_point, 'dwi.bval'),
                adcPath=os.path.join(output_dir, subject_id, time_point, 'adc.nii.gz')
            )

        # Tasks 2 and 3: Register t1ce.nii.gz file to the atlas image and coregister the other files to the transformed t1ce.nii.gz
        for mri_seq in ['t1ce', 't1', 't2', 'flair']:  # Excluding 'adc' here
            reference = atlas_image if mri_seq == 't1ce' else os.path.join(output_dir, subject_id, time_point, 't1ce_reg.nii.gz')
            run_elastix(
                in_file=os.path.join(output_dir, subject_id, time_point, mri_seq + '.nii.gz'),
                reference=reference,
                out_file=os.path.join(output_dir, subject_id, time_point, mri_seq + '_reg.nii.gz')
            )

        # Task 4: Apply skull stripping
        for mri_seq in ["t1", "t1ce", "t2", "flair"]:
            subprocess.run(
                ["mri_synthstrip", "-i", os.path.join(output_dir, subject_id, time_point, f"{mri_seq}_reg.nii.gz"),
                 "-o", os.path.join(output_dir, subject_id, time_point, f"{mri_seq}_reg_sk.nii.gz"),
                 "-m", os.path.join(output_dir, subject_id, time_point, f"{mri_seq}_mask.nii.gz")])

        # Apply skull stripping to the ADC image
        subprocess.run(["mri_synthstrip", "-i", os.path.join(output_dir, subject_id, time_point, "adc.nii.gz"),
                        "-o", os.path.join(output_dir, subject_id, time_point, "adc_sk.nii.gz"),
                        "-m", os.path.join(output_dir, subject_id, time_point, "adc_mask.nii.gz")])

        # Register the skull-stripped adc to t1ce_reg_sk.nii.gz
        run_elastix(
            in_file=os.path.join(output_dir, subject_id, time_point, 'adc_sk.nii.gz'),
            reference=os.path.join(output_dir, subject_id, time_point, 't1ce_reg_sk.nii.gz'),
            out_file=os.path.join(output_dir, subject_id, time_point, 'adc_reg_sk.nii.gz')
        )

        # Task 5: Apply z-score intensity normalization and create normalized files
        for mri_seq in ['t1', 't1ce', 't2', 'flair', 'adc']:
            input_path = os.path.join(output_dir, subject_id, time_point, f"{mri_seq}_reg_sk.nii.gz")
            output_path = os.path.join(output_dir, subject_id, time_point, f"{mri_seq}_norm.nii.gz")
            normalize_intensity(input_path, output_path)

        # Task 6: Run segmentation with the renamed files in the specified order
        time_point_folder = os.path.join(output_dir, subject_id, time_point)

        input_files = f"{time_point_folder}/t1_norm.nii.gz,{time_point_folder}/t1ce_norm.nii.gz,{time_point_folder}/t2_norm.nii.gz,{time_point_folder}/flair_norm.nii.gz"

        subprocess.run([
            "DeepMedic", "-md", deep_medic_model, "-i", input_files,
            "-o", f"{time_point_folder}/segmentations.nii.gz"
        ])

        # Rename normalized files
        os.rename(os.path.join(output_dir, subject_id, time_point, 't1_norm.nii.gz'),
                          os.path.join(output_dir, subject_id, time_point, 't1.nii.gz'))
        os.rename(os.path.join(output_dir, subject_id, time_point, 't2_norm.nii.gz'),
                          os.path.join(output_dir, subject_id, time_point, 't2.nii.gz'))
        os.rename(os.path.join(output_dir, subject_id, time_point, 'flair_norm.nii.gz'),
                          os.path.join(output_dir, subject_id, time_point, 'flair.nii.gz'))
        os.rename(os.path.join(output_dir, subject_id, time_point, 't1ce_norm.nii.gz'),
                          os.path.join(output_dir, subject_id, time_point, 't1ce.nii.gz'))
        os.rename(os.path.join(output_dir, subject_id, time_point, 'adc_norm.nii.gz'),
                          os.path.join(output_dir, subject_id, time_point, 'adc.nii.gz'))

        # Create tumor.nii.gz and peritumor.nii.gz from segmentations.nii.gz
        segmentations_path = os.path.join(output_dir, subject_id, time_point, 'segmentations.nii.gz')
        tumor_peritumor_output_dir = os.path.join(output_dir, subject_id, time_point)
        create_tumor_peritumor(segmentations_path, tumor_peritumor_output_dir)

        # Remove unnecessary subfolders
        shutil.rmtree(os.path.join(time_point_folder, 'logs'), ignore_errors=True)
        shutil.rmtree(os.path.join(time_point_folder, 'predictions'), ignore_errors=True)

        # Remove files unnecessary files ending with....
        file_extensions_to_remove = ['_reg_sk.nii.gz', '_mask.nii.gz', '_normalized.nii.gz', '_reg.nii.gz', '_sk.nii.gz', '.bval', '.bvec']
        for root, dirs, files in os.walk(time_point_folder):
            for file in files:
                if any(file.endswith(extension) for extension in file_extensions_to_remove):
                    os.remove(os.path.join(root, file))
