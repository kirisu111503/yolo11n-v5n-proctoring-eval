import os
import shutil
from PIL import Image, ImageFilter

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
# 0.5 is very light, 2.0 is moderate, 5.0 is heavy blur.
# For a thesis, 2.0 - 3.0 usually shows a good "challenge" for the model.
BLUR_RADIUS = 2.0 
IMG_EXTS = (".jpg", ".jpeg", ".png")

def generate_blur_test_set(src_root, dst_root):
    """
    Creates a new folder 'test_blur' with blurred versions of 'test' images.
    Labels are copied exactly as they are.
    """
    src_img_dir = os.path.join(src_root, "images")
    src_lbl_dir = os.path.join(src_root, "labels")
    
    dst_img_dir = os.path.join(dst_root, "images")
    dst_lbl_dir = os.path.join(dst_root, "labels")

    # Create new directories
    os.makedirs(dst_img_dir, exist_ok=True)
    os.makedirs(dst_lbl_dir, exist_ok=True)

    image_files = [f for f in os.listdir(src_img_dir) if f.lower().endswith(IMG_EXTS)]
    
    print("=" * 70)
    print(f"🌫️  GENERATING BLURRED TEST SET")
    print(f"📂 Source: {src_root}")
    print(f"📂 Destination: {dst_root}")
    print(f"🧪 Blur Radius: {BLUR_RADIUS}px")
    print("=" * 70)

    success_count = 0

    for filename in image_files:
        img_path = os.path.join(src_img_dir, filename)
        lbl_path = os.path.join(src_lbl_dir, filename.rsplit('.', 1)[0] + ".txt")

        # Only process if a label exists (ensures we only blur what we can test)
        if not os.path.exists(lbl_path):
            continue

        try:
            # 1. Apply Gaussian Blur
            with Image.open(img_path).convert("RGB") as img:
                blurred_img = img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
                blurred_img.save(os.path.join(dst_img_dir, filename), quality=95)

            # 2. Copy Label (Unchanged coordinates)
            shutil.copy2(lbl_path, os.path.join(dst_lbl_dir, os.path.basename(lbl_path)))
            
            success_count += 1
            if success_count % 100 == 0:
                print(f"✅ Processed {success_count}/{len(image_files)}...")

        except Exception as e:
            print(f"❌ Error on {filename}: {e}")

    print("-" * 70)
    print(f"🎉 Successfully created {success_count} blurred samples in '{dst_root}'")
    print("=" * 70)

if __name__ == "__main__":
    # Point this to your original 'test' folder
    # It will create 'test_blur'
    generate_blur_test_set("test", "test_blur")