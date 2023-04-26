#!/bin/bash
export PATH=~/CaPTk/1.8.1/squashfs-root/usr/bin:$PATH
export LD_LIBRARY_PATH=~/CaPTk/1.8.1/squashfs-root/usr/lib:$LD_LIBRARY_PATH

main_folder="/mnt/c/Users/Santiago/Documents/DICOM"
atlas_image="/mnt/c/CaPTk_Full/1.8.1/data/sri24/atlastImage.nii.gz"
deep_medic_model="/mnt/c/CaPTk_Full/1.8.1/data/deepMedic/saved_models/brainTumorSegmentation"

for subject_id in $(ls -d "$main_folder"/*); do
    for time_point in 0 1 2; do
        time_point_folder="$subject_id/$time_point"
        if [ ! -d "$time_point_folder" ]; then
            continue
        fi

        for mri_seq in t1 t1ce t2 flair adc; do
            mri_seq_folder="$time_point_folder/$mri_seq"

            # Task 1: DICOM to Nifti conversion
            dcm2niix -z y -o "$time_point_folder" -f "$mri_seq" "$mri_seq_folder"

            # Task 2: Register t1ce.nii.gz file to the atlas image
            if [ "$mri_seq" == "t1ce" ]; then
                flirt -in "$time_point_folder/$mri_seq.nii.gz" -ref "$atlas_image" -out "$time_point_folder/${mri_seq}_reg.nii.gz" -bins 256 -cost corratio -searchrx -180 180 -searchry -180 180 -searchrz -180 180 -dof 12  -interp trilinear
            fi
        done

        # Task 3: Coregister the other files to the transformed t1ce.nii.gz
        for mri_seq in t1 t2 flair; do
            flirt -in "$time_point_folder/$mri_seq.nii.gz" -ref "$time_point_folder/t1ce_reg.nii.gz" -out "$time_point_folder/${mri_seq}_reg.nii.gz" -bins 256 -cost corratio -searchrx -180 180 -searchry -180 180 -searchrz -180 180 -dof 12  -interp trilinear
        done

        # Task 4: Apply skull stripping
        for mri_seq in t1 t1ce t2 flair; do
            mri_synthstrip -i "$time_point_folder/${mri_seq}_reg.nii.gz" -o "$time_point_folder/${mri_seq}_reg_sk.nii.gz" -m "$time_point_folder/${mri_seq}_mask.nii.gz"
        done

        # Task 5: Apply z-score intensity normalization and create normalized files
        for mri_seq in t1 t1ce t2 flair; do
            Preprocessing -i "$time_point_folder/${mri_seq}_reg_sk.nii.gz" -m "$time_point_folder/${mri_seq}_mask.nii.gz" -o "$time_point_folder/${mri_seq}_norm.nii.gz" -zn 1 -zq 5,95 -zc 3,3
        done

        # ADC processing: Skull strip, register to t1ce_reg_sk.nii.gz, and intensity normalization
        mri_synthstrip -i "$time_point_folder/adc.nii.gz" -o "$time_point_folder/adc_sk.nii.gz" -m "$time_point_folder/adc_mask.nii.gz"
        flirt -in "$time_point_folder/adc_sk.nii.gz" -ref "$time_point_folder/t1ce_reg_sk.nii.gz" -out "$time_point_folder/adc_reg.nii.gz" -bins 256 -cost corratio -searchrx -180 180 -searchry -180 180 -searchrz -180 180 -dof 12  -interp trilinear
        Preprocessing -i "$time_point_folder/adc_reg.nii.gz" -m "$time_point_folder/t1ce_mask.nii.gz" -o "$time_point_folder/adc_norm.nii.gz" -zn 1 -zq 5,95 -zc 3,3

        # Task 5.5: Rename normalized files and overwrite if necessary
        for mri_seq in t1 t1ce t2 flair; do
            if [ "$mri_seq" == "flair" ]; then
                mv "$time_point_folder/${mri_seq}_norm.nii.gz" "$time_point_folder/fl.nii.gz"
            else
                mv "$time_point_folder/${mri_seq}_norm.nii.gz" "$time_point_folder/${mri_seq}.nii.gz"
            fi
        done
        mv "$time_point_folder/adc_norm.nii.gz" "$time_point_folder/adc.nii.gz"

        # Task 6: Run segmentation with the renamed files in the specified order
        input_files="$time_point_folder/t1.nii.gz,$time_point_folder/t1ce.nii.gz,$time_point_folder/t2.nii.gz,$time_point_folder/fl.nii.gz"
        DeepMedic -md "$deep_medic_model" -i $input_files -o "$time_point_folder/segmentations.nii.gz" -zn 0

        # Cleanup: Remove unnecessary files
        for mri_seq in t1 t1ce t2 flair adc; do
            rm -f "$time_point_folder/${mri_seq}_reg.nii.gz" "$time_point_folder/${mri_seq}_sk.nii.gz" "$time_point_folder/${mri_seq}_reg_sk.nii.gz" "$time_point_folder/${mri_seq}_mask.nii.gz" "$time_point_folder/${mri_seq}_norm.nii.gz"
        done
        rm -f "$time_point_folder"/*.bval "$time_point_folder"/*.bvec "$time_point_folder"/*.json "$time_point_folder"/*_normalized.nii.gz
    	rm -rf "$time_point_folder/logs" "$time_point_folder/predictions"

        # Rename fl.nii.gz to flair.nii.gzz
        mv "$time_point_folder/fl.nii.gz" "$time_point_folder/flair.nii.gz"

    done
done
