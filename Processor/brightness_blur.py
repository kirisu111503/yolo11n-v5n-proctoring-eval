import os
import shutil
from PIL import Image, ImageFilter, ImageEnhance

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
# We will create a "Dark + Blurry" scenario (the hardest to detect)
BRIGHTNESS_FACTOR = 0.5  # 50% darker
BLUR_RADIUS = 2.5       # Moderate motion blur
IMG_EXTS = (".jpg", ".jpeg", ".png")

def apply_blur_brightness(img):
    # 1. Apply Darkness first
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(BRIGHTNESS_FACTOR)
    
    # 2. Apply Gaussian Blur
    img = img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
    
    return img

def generate_blur_bright_test_set(src_root, dst_root):
    """
    Creates a new folder 'test_blur_bright' with dark and blurry versions.
    """
    src_img_dir = os.path.join(src_root, "images")
    src_lbl_dir = os.path.join(src_root, "labels")
    
    dst_img_dir = os.path.join(dst_root, "images")
    dst_lbl_dir = os.path.join(dst_root, "labels")

    # Create directories
    os.makedirs(dst_img_dir, exist_ok=True)
    os.makedirs(dst_lbl_dir, exist_ok=True)

    image_files = [f for f in os.listdir(src_img_dir) if f.lower().endswith(IMG_EXTS)]
    
    print("=" * 70)
    print(f"🌫️💡 GENERATING BLUR + BRIGHTNESS TEST SET")
    print(f"📂 Destination: {dst_root}")
    print(f"📉 Factors: {BRIGHTNESS_FACTOR}x Brightness, {BLUR_RADIUS}px Blur")
    print("=" * 70)

    success_count = 0

    for filename in image_files:
        img_path = os.path.join(src_img_dir, filename)
        lbl_path = os.path.join(src_lbl_dir, filename.rsplit('.', 1)[0] + ".txt")

        if not os.path.exists(lbl_path):
            continue

        try:
            # Apply combined effects
            with Image.open(img_path).convert("RGB") as img:
                processed_img = apply_blur_brightness(img)
                processed_img.save(os.path.join(dst_img_dir, filename), quality=95)

            # Copy original label
            shutil.copy2(lbl_path, os.path.join(dst_lbl_dir, os.path.basename(lbl_path)))
            
            success_count += 1
            if success_count % 100 == 0:
                print(f"✅ Processed {success_count}/{len(image_files)}...")

        except Exception as e:
            print(f"❌ Error on {filename}: {e}")

    print(f"🎉 Successfully created {success_count} compound samples in '{dst_root}'")

if __name__ == "__main__":
    # Takes your original test folder and creates a new one
    generate_blur_bright_test_set("test", "test_blur_bright")