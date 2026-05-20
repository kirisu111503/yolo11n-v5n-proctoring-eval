import os
import shutil
import random
import math
from PIL import Image, ImageDraw, ImageEnhance

# ==========================================
# ⚙️ COMPOUND SETTINGS
# ==========================================
BRIGHTNESS_FACTOR = 0.6  # Making it darker (stressful for the model)
OCCLUSION_RATIOS = [0.30, 0.45, 0.60]
OCC_COLOR = (80, 80, 80) # Darker grey to match low light
IMG_EXTS = (".jpg", ".jpeg", ".png")

def yolo_to_pixels(yolo_box, img_width, img_height):
    cls, x_c, y_c, w, h = yolo_box
    bw, bh = w * img_width, h * img_height
    x_min = int((x_c * img_width) - (bw / 2))
    y_min = int((y_c * img_height) - (bh / 2))
    return max(0, x_min), max(0, y_min), min(img_width, int(x_min + bw)), min(img_height, int(y_min + bh))

def apply_compound_effects(img, boxes):
    # 1. Apply Brightness first
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(BRIGHTNESS_FACTOR)
    
    # 2. Apply Occlusion on the adjusted image
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
    return img

def generate_compound_test_set(src_root, dst_root):
    src_img_dir = os.path.join(src_root, "images")
    src_lbl_dir = os.path.join(src_root, "labels")
    dst_img_dir = os.path.join(dst_root, "images")
    dst_lbl_dir = os.path.join(dst_root, "labels")

    os.makedirs(dst_img_dir, exist_ok=True)
    os.makedirs(dst_lbl_dir, exist_ok=True)

    files = [f for f in os.listdir(src_img_dir) if f.lower().endswith(IMG_EXTS)]
    print(f"🌀 Generating Compound Stress Test (Dark + Occluded) into '{dst_root}'...")

    for f in files:
        img_p = os.path.join(src_images := src_img_dir, f)
        lbl_p = os.path.join(src_labels := src_lbl_dir, f.rsplit('.', 1)[0] + ".txt")

        if not os.path.exists(lbl_p): continue

        # Read labels
        boxes = []
        with open(lbl_p, 'r') as file:
            for line in file:
                p = line.strip().split()
                if len(p) >= 5:
                    boxes.append([int(p[0])] + [float(x) for x in p[1:5]])

        # Process
        with Image.open(img_p).convert("RGB") as img:
            img = apply_compound_effects(img, boxes)
            img.save(os.path.join(dst_img_dir, f), quality=95)

        shutil.copy2(lbl_p, os.path.join(dst_lbl_dir, os.path.basename(lbl_p)))

    print(f"✅ Success! Created {len(files)} compound samples.")

if __name__ == "__main__":
    generate_compound_test_set("test", "test_brightness_occlusion")