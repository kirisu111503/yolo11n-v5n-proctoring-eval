import os
import random
from PIL import Image, ImageEnhance

# Default Configuration
DEFAULT_CONFIG = {
    "image_dir": "phone_dataset/train/images",
    "label_dir": "phone_dataset/train/labels",
    "brightness_range": (0.7, 1.3),
    "brightness_steps": [0.7, 0.85, 1.0, 1.15, 1.3],
    "img_extensions": (".jpg", ".jpeg", ".png"),
    "skip_augmented": True  # Skip files with "_bright" in name
}


def apply_brightness(image, factor):
    """Apply brightness adjustment to image."""
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def generate_brightness_augmentation(img_name, brightness_factor, aug_num, image_dir, label_dir):
    """Generate a brightness-adjusted image."""
    base = os.path.splitext(img_name)[0]
    img_path = os.path.join(image_dir, img_name)
    lbl_path = os.path.join(label_dir, base + ".txt")

    if not os.path.exists(img_path):
        return False
    
    if not os.path.exists(lbl_path):
        print(f"⚠️  No label for {img_name}, skipping")
        return False

    # Load image
    img = Image.open(img_path).convert("RGB")
    
    # Apply brightness
    bright_img = apply_brightness(img, brightness_factor)
    
    # Create unique filename
    brightness_label = f"{brightness_factor:.2f}".replace(".", "_")
    img_out = os.path.join(image_dir, f"{base}_bright{brightness_label}_aug{aug_num}.jpg")
    lbl_out = os.path.join(label_dir, f"{base}_bright{brightness_label}_aug{aug_num}.txt")
    
    # Save augmented image
    bright_img.save(img_out, quality=95)
    
    # Copy label (brightness doesn't affect bounding boxes)
    with open(lbl_path, 'r') as src:
        with open(lbl_out, 'w') as dst:
            dst.write(src.read())
    
    return True


def count_images(image_dir, img_extensions):
    """Count total images in directory."""
    count = 0
    for file in os.listdir(image_dir):
        if file.lower().endswith(img_extensions):
            count += 1
    return count


def get_all_images(image_dir, img_extensions, skip_augmented=True):
    """Get list of all image files."""
    images = []
    for file in os.listdir(image_dir):
        if file.lower().endswith(img_extensions):
            # Skip already augmented images if requested
            if skip_augmented and "_bright" in file.lower():
                continue
            images.append(file)
    return images


def brightness_augment(config=None, mode="fixed", num_per_image=None, target_total=None, interactive=True):
    """
    Apply brightness augmentation to dataset.
    
    Args:
        config (dict): Configuration dictionary with keys matching DEFAULT_CONFIG
        mode (str): Augmentation mode - "fixed", "random", or "target"
        num_per_image (int): For "random" mode - how many variations per image
        target_total (int): For "target" mode - target total number of images
        interactive (bool): Whether to prompt for user confirmation
    
    Returns:
        dict: Results with keys 'success', 'generated', 'total_images'
    """
    # Merge with defaults
    cfg = DEFAULT_CONFIG.copy()
    if config:
        cfg.update(config)
    
    # Extract config values
    image_dir = cfg["image_dir"]
    label_dir = cfg["label_dir"]
    brightness_range = cfg["brightness_range"]
    brightness_steps = cfg["brightness_steps"]
    img_extensions = cfg["img_extensions"]
    skip_augmented = cfg["skip_augmented"]
    
    if not os.path.exists(image_dir):
        print(f"❌ Image directory not found: {image_dir}")
        return {"success": False, "error": f"Image directory not found: {image_dir}"}
    
    if not os.path.exists(label_dir):
        print(f"❌ Label directory not found: {label_dir}")
        return {"success": False, "error": f"Label directory not found: {label_dir}"}

    print("=" * 70)
    print("💡 BRIGHTNESS AUGMENTATION")
    print("=" * 70)
    print(f"📊 Brightness range: {brightness_range[0]} to {brightness_range[1]}")
    print(f"   • 0.7 = Darker")
    print(f"   • 1.0 = Original")
    print(f"   • 1.3 = Brighter")
    print()

    # Get original images (exclude already augmented ones)
    original_images = get_all_images(image_dir, img_extensions, skip_augmented)
    total_current = count_images(image_dir, img_extensions)
    
    print(f"📂 Found {len(original_images)} original images")
    print(f"📂 Total images (including augmented): {total_current}")
    print()

    generated = 0
    aug_num = 1
    
    # Mode 1: Fixed brightness levels
    if mode == "fixed":
        brightness_levels = [b for b in brightness_steps if b != 1.0]  # Skip 1.0 (original)
        total_to_generate = len(original_images) * len(brightness_levels)
        
        print(f"📊 Mode: Fixed brightness levels")
        print(f"📊 Will generate {len(brightness_levels)} variations per image")
        print(f"📊 Total new images: {total_to_generate:,}")
        print(f"📊 Brightness levels: {brightness_levels}")
        
        if interactive:
            proceed = input("\n🚀 Proceed? (y/n): ")
            if proceed.lower() != 'y':
                print("❌ Cancelled.")
                return {"success": False, "error": "User cancelled"}
        
        print("\n" + "=" * 70)
        print("🔄 Generating brightness augmentations...")
        print("=" * 70)
        
        for img_name in original_images:
            for brightness in brightness_levels:
                success = generate_brightness_augmentation(img_name, brightness, aug_num, image_dir, label_dir)
                if success:
                    generated += 1
                    if generated % 100 == 0:
                        print(f"✅ Generated: {generated}/{total_to_generate} ({generated*100//total_to_generate}%)")
                aug_num += 1
    
    # Mode 2: Random brightness
    elif mode == "random":
        if num_per_image is None:
            if interactive:
                try:
                    num_per_image = int(input("\n🎲 How many random variations per image? "))
                except ValueError:
                    print("❌ Invalid input!")
                    return {"success": False, "error": "Invalid input"}
            else:
                print("❌ num_per_image required for random mode!")
                return {"success": False, "error": "num_per_image required"}
        
        total_to_generate = len(original_images) * num_per_image
        
        print(f"📊 Mode: Random brightness")
        print(f"📊 Will generate {num_per_image} random variations per image")
        print(f"📊 Total new images: {total_to_generate:,}")
        
        if interactive:
            proceed = input("\n🚀 Proceed? (y/n): ")
            if proceed.lower() != 'y':
                print("❌ Cancelled.")
                return {"success": False, "error": "User cancelled"}
        
        print("\n" + "=" * 70)
        print("🔄 Generating brightness augmentations...")
        print("=" * 70)
        
        for img_name in original_images:
            for _ in range(num_per_image):
                brightness = random.uniform(brightness_range[0], brightness_range[1])
                # Avoid very close to 1.0 (original)
                if 0.95 < brightness < 1.05:
                    brightness = random.choice([0.85, 1.15])
                
                success = generate_brightness_augmentation(img_name, brightness, aug_num, image_dir, label_dir)
                if success:
                    generated += 1
                    if generated % 100 == 0:
                        print(f"✅ Generated: {generated}/{total_to_generate} ({generated*100//total_to_generate}%)")
                aug_num += 1
    
    # Mode 3: Target total
    elif mode == "target":
        if target_total is None:
            if interactive:
                try:
                    target_total = int(input("\n🎯 Target total number of images (including current): "))
                except ValueError:
                    print("❌ Invalid input!")
                    return {"success": False, "error": "Invalid input"}
            else:
                print("❌ target_total required for target mode!")
                return {"success": False, "error": "target_total required"}
        
        needed = target_total - total_current
        
        if needed <= 0:
            print(f"\n✅ Already have {total_current} images (target: {target_total})")
            print("   No augmentation needed!")
            return {"success": True, "generated": 0, "total_images": total_current, "message": "Target already met"}
        
        print(f"📊 Mode: Target total")
        print(f"📊 Current images: {total_current:,}")
        print(f"📊 Target images:  {target_total:,}")
        print(f"📊 Need to generate: {needed:,} images")
        
        if interactive:
            proceed = input("\n🚀 Proceed? (y/n): ")
            if proceed.lower() != 'y':
                print("❌ Cancelled.")
                return {"success": False, "error": "User cancelled"}
        
        print("\n" + "=" * 70)
        print("🔄 Generating brightness augmentations...")
        print("=" * 70)
        
        while generated < needed:
            # Cycle through images
            for img_name in original_images:
                if generated >= needed:
                    break
                
                brightness = random.uniform(brightness_range[0], brightness_range[1])
                # Avoid very close to 1.0
                if 0.95 < brightness < 1.05:
                    brightness = random.choice([0.8, 1.2])
                
                success = generate_brightness_augmentation(img_name, brightness, aug_num, image_dir, label_dir)
                if success:
                    generated += 1
                    if generated % 100 == 0 or generated == needed:
                        print(f"✅ Generated: {generated}/{needed} ({generated*100//needed}%)")
                
                aug_num += 1
    
    else:
        print(f"❌ Invalid mode: {mode}")
        return {"success": False, "error": f"Invalid mode: {mode}"}

    final_total = count_images(image_dir, img_extensions)
    
    print("\n" + "=" * 70)
    print("✅ BRIGHTNESS AUGMENTATION COMPLETED!")
    print("=" * 70)
    print(f"📊 Generated: {generated:,} new images")
    print(f"📊 Total images now: {final_total:,}")
    print(f"📁 Saved to: {image_dir}")
    print("=" * 70)
    
    return {
        "success": True,
        "generated": generated,
        "total_images": final_total,
        "mode": mode
    }


def main():
    """CLI entry point with interactive mode selection."""
    config = DEFAULT_CONFIG.copy()
    
    print("🎯 Augmentation options:")
    print("   1. Fixed brightness levels (0.7, 0.85, 1.15, 1.3)")
    print("   2. Random brightness per image")
    print("   3. Generate specific number of augmentations")
    
    try:
        choice = int(input("\nSelect option (1-3): "))
    except ValueError:
        print("❌ Invalid input!")
        return
    
    if choice == 1:
        brightness_augment(config=config, mode="fixed", interactive=True)
    elif choice == 2:
        brightness_augment(config=config, mode="random", interactive=True)
    elif choice == 3:
        brightness_augment(config=config, mode="target", interactive=True)
    else:
        print("❌ Invalid option!")


if __name__ == "__main__":
    main()