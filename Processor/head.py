
'''
    This is the master pipeline script that orchestrates the dataset processing
    including splitting, brightness adjustment, blurring, and occlusion.
    
    NOTE: This script process per class or folder, so ensure your dataset is
    organized accordingly (e.g., "book", "phone", "calculator" folders).
    Which then contain "images" and "labels" subfolders.
    
    Make sure before you merge your dataset the id's of each class are unique.
    
    Use match.py to verify label consistency if needed.
    If the dataset has no errors, you can then proceed and run the merge.py script.
    
    Expected folder structure:
    ├── book
    │   ├── images
    │   └── labels
    ├── phone
    │   ├── images
    │   └── labels
    └── calculator
        ├── images
        └── labels
        
    Output folders structure:
    ├── book_dataset
    │   ├── train
    │   │   ├── images
    │   │   └── labels
    │   ├── val
    │   │   ├── images
    │   │   └── labels
    │   └── test
    │       ├── images
    │       └── labels
    ├── phone_dataset
    │   ├── train
    │   │   ├── images
    │   │   └── labels
    │   ├── val
    │   │   ├── images
    │   │   └── labels
    │   └── test
    │       ├── images
    │       └── labels
    └── calculator_dataset
        ├── train
        │   ├── images
        │   └── labels
        ├── val
        │   ├── images
        │   └── labels
        └── test
            ├── images
            └── labels
    Each augmentation step is applied only to the training set.
    
    The respective augmentations applied to the training set.
    Important: Ensure you have the required libraries installed:
    pip install Pillow
'''


import os
# Importing your modules (Note: ensuring spelling matches your provided filenames)
from split import split_dataset
from brightness import brightness_augment  # sic: brigthness.py
from blur import blur_dataset
import occlusion

# ==========================================
# ⚙️  PIPELINE CONFIGURATION
# ==========================================
CATEGORIES = ["book", "phone", "calculator"]

# Standard Split Ratios
SPLIT_CONFIG_TEMPLATE = {
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,
    "max_total": 1786,  # Cap dataset size
    "img_extensions": (".jpg", ".jpeg", ".png")
}

def run_pipeline():
    print("🚀 STARTING MASTER PIPELINE")
    print(f"🎯 Categories to process: {CATEGORIES}")

    for category in CATEGORIES:
        print("\n" + "#" * 50)
        print(f"📦 PROCESSING CATEGORY: {category.upper()}")
        print("#" * 50)

        # Defined Paths
        # Assumes source folders are ./book/images and ./book/labels
        source_img = os.path.join(category, "images") 
        source_lbl = os.path.join(category, "labels")
        output_dataset = f"{category}_dataset"
        
        # -------------------------------------------------
        # 1. SPLIT DATASET
        # -------------------------------------------------
        print(f"\n[Step 1] Splitting {category}...")
        
        current_split_config = SPLIT_CONFIG_TEMPLATE.copy()
        current_split_config.update({
            "source_image_dir": source_img,
            "source_label_dir": source_lbl,
            "output_root": output_dataset
        })

        # Check if source exists before running
        if not os.path.exists(source_img):
            print(f"❌ Skipping {category}: Source folder '{source_img}' not found.")
            continue

        split_res = split_dataset(config=current_split_config, interactive=False)
        
        if not split_res['success']:
            print(f"❌ Split failed for {category}. Skipping augmentations.")
            continue

        # -------------------------------------------------
        # 2. BRIGHTNESS AUGMENTATION (Train Only)
        # -------------------------------------------------
        print(f"\n[Step 2] Applying Brightness to {category} (Train)...")
        
        bright_config = {
            "image_dir": f"{output_dataset}/train/images",
            "label_dir": f"{output_dataset}/train/labels",
            "brightness_steps": [0.7, 1.3], # Adding a dark and a bright variant
            "skip_augmented": True
        }
        
        # Using 'fixed' mode to generate specific variations deterministicly
        brightness_augment(config=bright_config, mode="fixed", interactive=False)

        # -------------------------------------------------
        # 3. BLUR AUGMENTATION (Train Only)
        # -------------------------------------------------
        print(f"\n[Step 3] Applying Blur to {category} (Train)...")
        
        # Note: This will blur the Originals AND the Brightness versions generated above
        blur_config = {
            "root_folder": output_dataset,
            "image_dir": f"{output_dataset}/train/images",
            "label_dir": f"{output_dataset}/train/labels",
            "blur_radius": 1.0, 
            "suffix": "_blur"
        }
        
        blur_dataset(config=blur_config, interactive=False)

        # -------------------------------------------------
        # 4. OCCLUSION AUGMENTATION (Train Only)
        # -------------------------------------------------
        print(f"\n[Step 4] Applying Occlusion to {category} (Train)...")
        
        # Note: This will occlude Originals, Brights, and Blurs
        occlusion.run_augmentation(output_dataset, "train")
        
        print(f"\n✅ FINISHED PROCESSING: {category}")

    print("\n" + "=" * 50)
    print("🎉 PIPELINE COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    run_pipeline()