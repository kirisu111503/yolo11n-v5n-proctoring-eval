'''
    NOTE: This script applies a series of image augmentations (occlusion, brightness adjustment, and blur)
    and saves each step of the process as a separate image file for better visualization of the effects

    This is different from applying all effects at once; instead, it saves the intermediate results.
    
    Important: Ensure you have the Pillow library installed:
    pip install Pillow
    
    For applying this augmentation to the training, test, and val sets of your dataset, use the head.py.
'''


import os
import shutil
import random
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

# ==========================================
# ⚙️ ULTIMATE STRESS SETTINGS
# ==========================================
BRIGHT_FACTOR = 0.6      # 60% brighter/darker
BLUR_RADIUS = 2.0      # Moderate blur
OCCLUSION_RATIOS = [0.30, 0.45, 0.60]
OCC_COLOR = (40, 40, 40) # Dark grey
IMG_EXTS = (".jpg", ".jpeg", ".png")

def yolo_to_pixels(yolo_box, img_width, img_height):
    cls, x_c, y_c, w, h = yolo_box
    bw, bh = w * img_width, h * img_height
    x_min = int((x_c * img_width) - (bw / 2))
    y_min = int((y_c * img_height) - (bh / 2))
    return max(0, x_min), max(0, y_min), min(img_width, int(x_min + bw)), min(img_height, int(y_min + bh))

def process_and_save_steps(img, boxes, filename, output_dir):
    """
    Applies effects step-by-step and saves each stage individually.
    """
    base_name = filename.rsplit('.', 1)[0]
    ext = filename.rsplit('.', 1)[1]

    # --- STEP 0: ORIGINAL ---
    # Save the clean original first
    step0_path = os.path.join(output_dir, f"{base_name}_0_clean.{ext}")
    img.save(step0_path, quality=95)

    # --- STEP 1: APPLY OCCLUSION ---
    draw = ImageDraw.Draw(img)
    w, h = img.size
    for box in boxes:
        x1, y1, x2, y2 = yolo_to_pixels(box, w, h)
        obj_w, obj_h = x2 - x1, y2 - y1
        if obj_w <= 5 or obj_h <= 5: continue 

        ratio = random.choice(OCCLUSION_RATIOS)
        target_area = (obj_w * obj_h) * ratio
        aspect = random.uniform(0.7, 1.4)
        occ_w = int(math.sqrt(target_area * aspect))
        occ_h = int(math.sqrt(target_area / aspect))
        
        occ_w, occ_h = min(occ_w, obj_w), min(occ_h, obj_h)
        offset_x = random.randint(0, obj_w - occ_w)
        offset_y = random.randint(0, obj_h - occ_h)
        draw.rectangle([x1 + offset_x, y1 + offset_y, x1 + offset_x + occ_w, y1 + offset_y + occ_h], fill=OCC_COLOR)
    
    # Save Step 1 (Occluded)
    step1_path = os.path.join(output_dir, f"{base_name}_1_occluded.{ext}")
    img.save(step1_path, quality=95)

    # --- STEP 2: APPLY BRIGHTNESS ---
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(BRIGHT_FACTOR)
    
    # Save Step 2 (Brightened)
    step2_path = os.path.join(output_dir, f"{base_name}_2_brightened.{ext}")
    img.save(step2_path, quality=95)
    
    # --- STEP 3: APPLY BLUR ---
    img = img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
    
    # Save Step 3 (Blurred / Final)
    step3_path = os.path.join(output_dir, f"{base_name}_3_blurred_final.{ext}")
    img.save(step3_path, quality=95)

def generate_step_by_step_set(src_root, dst_folder_name):
    src_img_dir = os.path.join(src_root, "images")
    src_lbl_dir = os.path.join(src_root, "labels")
    
    # Create the single destination folder for all step images
    dst_dir = os.path.join(src_root, dst_folder_name)
    os.makedirs(dst_dir, exist_ok=True)

    files = [f for f in os.listdir(src_img_dir) if f.lower().endswith(IMG_EXTS)]
    print(f"Generating STEP-BY-STEP Augmentation into '{dst_dir}'...")

    for f in files:
        img_p = os.path.join(src_img_dir, f)
        lbl_p = os.path.join(src_lbl_dir, f.rsplit('.', 1)[0] + ".txt")
        
        # We need the labels to calculate occlusion, so skip if no label exists
        if not os.path.exists(lbl_p): continue

        boxes = []
        with open(lbl_p, 'r') as file:
            for line in file:
                p = line.strip().split()
                if len(p) >= 5:
                    boxes.append([int(p[0])] + [float(x) for x in p[1:5]])

        with Image.open(img_p).convert("RGB") as img:
            # Process and save all 4 stages for this image
            process_and_save_steps(img, boxes, f, dst_dir)

    print(f"✅ Processing complete. Check the folder '{dst_dir}' for your sequential images.")

if __name__ == "__main__":
    # Change "test" to whatever your source folder is
    generate_step_by_step_set("test", "step-by-step-augmentation")