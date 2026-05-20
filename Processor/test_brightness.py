import os
import shutil
from PIL import Image, ImageEnhance

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
# For a thesis, testing extreme lighting is best:
BRIGHT_FACTOR = 1.5  # 50% brighter
DARK_FACTOR = 0.5    # 50% darker
IMG_EXTS = (".jpg", ".jpeg", ".png")

def generate_brightness_test_set(src_root, brightness_factor, folder_suffix):
    """
    Creates a new folder (e.g., 'test_bright') with adjusted versions of 'test' images.
    """
    dst_root = f"{src_root}_{folder_suffix}"
    src_img_dir = os.path.join(src_root, "images")
    src_lbl_dir = os.path.join(src_root, "labels")
    
    dst_img_dir = os.path.join(dst_root, "images")
    dst_lbl_dir = os.path.join(dst_root, "labels")

    # Create new directories
    os.makedirs(dst_img_dir, exist_ok=True)
    os.makedirs(dst_lbl_dir, exist_ok=True)

    image_files = [f for f in os.listdir(src_img_dir) if f.lower().endswith(IMG_EXTS)]
    
    print("=" * 70)
    print(f"💡 GENERATING LIGHTING TEST SET: {dst_root}")
    print(f"🌟 Factor: {brightness_factor}x")
    print("=" * 70)

    success_count = 0

    for filename in image_files:
        img_path = os.path.join(src_img_dir, filename)
        lbl_path = os.path.join(src_lbl_dir, filename.rsplit('.', 1)[0] + ".txt")

        if not os.path.exists(lbl_path):
            continue

        try:
            # 1. Apply Brightness/Darkness
            with Image.open(img_path).convert("RGB") as img:
                enhancer = ImageEnhance.Brightness(img)
                adjusted_img = enhancer.enhance(brightness_factor)
                adjusted_img.save(os.path.join(dst_img_dir, filename), quality=95)

            # 2. Copy Label (Brightness does not change object position)
            shutil.copy2(lbl_path, os.path.join(dst_lbl_dir, os.path.basename(lbl_path)))
            
            success_count += 1
            if success_count % 100 == 0:
                print(f"✅ Processed {success_count}/{len(image_files)}...")

        except Exception as e:
            print(f"❌ Error on {filename}: {e}")

    print(f"🎉 Successfully created {success_count} samples in '{dst_root}'\n")

if __name__ == "__main__":
    # 1. Create the Bright Version
    generate_brightness_test_set("test", BRIGHT_FACTOR, "bright")
    
    # 2. Create the Dark Version
    generate_brightness_test_set("test", DARK_FACTOR, "dark")