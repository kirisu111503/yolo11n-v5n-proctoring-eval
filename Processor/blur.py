import os
import shutil
from PIL import Image, ImageFilter

# Default Configuration
DEFAULT_CONFIG = {
    "root_folder": "phone_dataset",
    "image_dir": None,  # Will be constructed if None
    "label_dir": None,  # Will be constructed if None
    "blur_radius": 0.5,
    "suffix": "_blur",
    "img_extensions": (".jpg", ".jpeg", ".png")
}


def apply_blur(image, blur_radius):
    """Apply fixed Gaussian Blur to image."""
    return image.filter(ImageFilter.GaussianBlur(blur_radius))


def get_label_path(img_path, image_dir, label_dir):
    """
    Calculates the corresponding label path.
    """
    rel_path = os.path.relpath(img_path, image_dir)
    base_rel = os.path.splitext(rel_path)[0]
    lbl_rel = base_rel + ".txt"
    return os.path.join(label_dir, lbl_rel)


def process_image(img_path, image_dir, label_dir, blur_radius, suffix):
    """Generate a blurred copy of ANY image provided."""
    try:
        # 1. Check Label Existence
        lbl_path = get_label_path(img_path, image_dir, label_dir)
        if not os.path.exists(lbl_path):
            print(f"⚠️  Skipping (No label): {os.path.basename(img_path)}")
            return False

        # 2. Construct Output Filename
        directory, filename = os.path.split(img_path)
        name, ext = os.path.splitext(filename)
        
        new_filename = f"{name}{suffix}{ext}"
        new_img_path = os.path.join(directory, new_filename)
        
        # Label path construction
        lbl_dir, lbl_filename = os.path.split(lbl_path)
        lbl_name, lbl_ext = os.path.splitext(lbl_filename)
        new_lbl_filename = f"{lbl_name}{suffix}{lbl_ext}"
        new_lbl_path = os.path.join(lbl_dir, new_lbl_filename)

        # 3. Augment Image (Blur)
        with Image.open(img_path).convert("RGB") as img:
            blurred_img = apply_blur(img, blur_radius)
            blurred_img.save(new_img_path, quality=95)

        # 4. Augment Label (Copy)
        shutil.copy2(lbl_path, new_lbl_path)

        return True

    except Exception as e:
        print(f"❌ Error processing {os.path.basename(img_path)}: {e}")
        return False


def get_all_current_images(image_dir, img_extensions):
    """
    Snapshot the directory: Get ALL images currently present.
    No filtering for augmentations.
    """
    all_files = []
    print("📸 Taking snapshot of current file list...")
    
    for root, _, files in os.walk(image_dir):
        for file in files:
            if file.lower().endswith(img_extensions):
                full_path = os.path.join(root, file)
                all_files.append(full_path)
    
    return all_files


def blur_dataset(config=None, interactive=True):
    """
    Apply blur augmentation to all images in dataset.
    
    Args:
        config (dict): Configuration dictionary with keys matching DEFAULT_CONFIG
        interactive (bool): Whether to prompt for user confirmation
    
    Returns:
        dict: Results with keys 'success', 'processed', 'failed', 'total_files'
    """
    # Merge with defaults
    cfg = DEFAULT_CONFIG.copy()
    if config:
        cfg.update(config)
    
    # Extract config values
    root_folder = cfg["root_folder"]
    image_dir = cfg["image_dir"] or f"{root_folder}/train/images"
    label_dir = cfg["label_dir"] or f"{root_folder}/train/labels"
    blur_radius = cfg["blur_radius"]
    suffix = cfg["suffix"]
    img_extensions = cfg["img_extensions"]
    
    if not os.path.exists(image_dir):
        print(f"❌ Image directory not found: {image_dir}")
        return {"success": False, "error": f"Image directory not found: {image_dir}"}

    print("=" * 70)
    print(f"🚀 TOTAL DATASET BLUR ({blur_radius}px)")
    print("=" * 70)
    print("📋 Logic: Apply blur to EVERY image found in the folder.")
    print("⚠️  Warning: If run multiple times, files will be blurred repeatedly.")
    print()

    # 1. Snapshot the list BEFORE processing
    files_to_process = get_all_current_images(image_dir, img_extensions)
    
    if not files_to_process:
        print("✅ No images found to process.")
        return {"success": True, "processed": 0, "failed": 0, "total_files": 0}

    print(f"📂 Snapshot contains {len(files_to_process)} images.")
    
    if interactive:
        proceed = input("⚡ Start batch processing? (y/n): ")
        if proceed.lower() != 'y':
            print("❌ Cancelled.")
            return {"success": False, "error": "User cancelled"}
    
    print("⚡ Starting batch processing...")
    print("-" * 70)

    # 2. Process the snapshot list
    success_count = 0
    fail_count = 0

    for i, img_path in enumerate(files_to_process, 1):
        if process_image(img_path, image_dir, label_dir, blur_radius, suffix):
            success_count += 1
            if i % 100 == 0:
                print(f"   ✅ Processed {i}/{len(files_to_process)}...")
        else:
            fail_count += 1

    print("-" * 70)
    print("✅ BATCH COMPLETED")
    print("=" * 70)
    print(f"📊 Input Count:      {len(files_to_process)}")
    print(f"🎉 Created New:      {success_count}")
    print(f"📁 Total Files Now:  {len(files_to_process) + success_count}")
    print("=" * 70)
    
    return {
        "success": True,
        "processed": success_count,
        "failed": fail_count,
        "total_files": len(files_to_process) + success_count,
        "input_count": len(files_to_process)
    }


def main():
    """CLI entry point."""
    blur_dataset(interactive=True)


if __name__ == "__main__":
    main()