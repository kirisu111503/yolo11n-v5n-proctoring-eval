import os
import shutil
from PIL import Image, ImageFilter, ImageEnhance

# ==========================================
# ⚙️ COMPOUND CONFIGURATION
# ==========================================
DARK_FACTOR = 0.5    # 50% darker (Simulates low light)
BLUR_RADIUS = 2.5    # Moderate blur (Simulates motion/shake)
IMG_EXTS = (".jpg", ".jpeg", ".png")

def generate_dark_blur_test_set(src_root, dst_root):
    """
    Creates a new folder 'test_dark_blur' by applying both 
    darkness and blur to the original test images.
    """
    src_img_dir = os.path.join(src_root, "images")
    src_lbl_dir = os.path.join(src_root, "labels")
    
    dst_img_dir = os.path.join(dst_root, "images")
    dst_lbl_dir = os.path.join(dst_root, "labels")

    # Create destination directories
    os.makedirs(dst_img_dir, exist_ok=True)
    os.makedirs(dst_lbl_dir, exist_ok=True)

    image_files = [f for f in os.listdir(src_img_dir) if f.lower().endswith(IMG_EXTS)]
    
    print("=" * 70)
    print(f"🌙🌫️  GENERATING COMPOUND TEST SET: {dst_root}")
    print(f"📉 Darkness: {DARK_FACTOR}x | Blur: {BLUR_RADIUS}px")
    print("=" * 70)

    success_count = 0

    for filename in image_files:
        img_path = os.path.join(src_img_dir, filename)
        lbl_path = os.path.join(src_lbl_dir, filename.rsplit('.', 1)[0] + ".txt")

        if not os.path.exists(lbl_path):
            continue

        try:
            # 1. Open Image
            with Image.open(img_path).convert("RGB") as img:
                # 2. Apply Darkness
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(DARK_FACTOR)
                
                # 3. Apply Blur
                img = img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
                
                # 4. Save to new folder
                img.save(os.path.join(dst_img_dir, filename), quality=95)

            # 5. Copy Label (Unchanged)
            shutil.copy2(lbl_path, os.path.join(dst_lbl_dir, os.path.basename(lbl_path)))
            
            success_count += 1
            if success_count % 100 == 0:
                print(f"✅ Processed {success_count}/{len(image_files)}...")

        except Exception as e:
            print(f"❌ Error on {filename}: {e}")

    print(f"\n🎉 Successfully created {success_count} dark_blur samples in '{dst_root}'")

if __name__ == "__main__":
    # Point to your 'test' folder to create 'test_dark_blur'
    generate_dark_blur_test_set("test", "test_dark_blur")