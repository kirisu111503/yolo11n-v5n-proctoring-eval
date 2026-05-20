import os
import shutil
import random
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

# ==========================================
# ⚙️ ULTIMATE STRESS SETTINGS
# ==========================================
BRIGHT_FACTOR = 1.6      # 60% brighter
BLUR_RADIUS = 2.0      # Moderate blur
OCCLUSION_RATIOS = [0.30, 0.45, 0.60]
OCC_COLOR = (40, 40, 40) # Dark grey to match the low light
IMG_EXTS = (".jpg", ".jpeg", ".png")

def yolo_to_pixels(yolo_box, img_width, img_height):
    cls, x_c, y_c, w, h = yolo_box
    bw, bh = w * img_width, h * img_height
    x_min = int((x_c * img_width) - (bw / 2))
    y_min = int((y_c * img_height) - (bh / 2))
    return max(0, x_min), max(0, y_min), min(img_width, int(x_min + bw)), min(img_height, int(y_min + bh))

def apply_triple_threat(img, boxes):
    # 1. Apply Occlusion FIRST
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
    
    # 2. Apply Darkness SECOND
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(BRIGHT_FACTOR)
    
    # 3. Apply Blur LAST (smears the occlusion and the darkened pixels)
    img = img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
    
    return img

def generate_triple_threat_set(src_root, dst_root):
    src_img_dir = os.path.join(src_root, "images")
    src_lbl_dir = os.path.join(src_root, "labels")
    dst_img_dir = os.path.join(dst_root, "images")
    dst_lbl_dir = os.path.join(dst_root, "labels")

    os.makedirs(dst_img_dir, exist_ok=True)
    os.makedirs(dst_lbl_dir, exist_ok=True)

    files = [f for f in os.listdir(src_img_dir) if f.lower().endswith(IMG_EXTS)]
    print(f"💀 Generating TRIPLE THREAT Set (Dark+Blur+Occ) into '{dst_root}'...")

    for f in files:
        img_p = os.path.join(src_img_dir, f)
        lbl_p = os.path.join(src_lbl_dir, f.rsplit('.', 1)[0] + ".txt")
        if not os.path.exists(lbl_p): continue

        boxes = []
        with open(lbl_p, 'r') as file:
            for line in file:
                p = line.strip().split()
                if len(p) >= 5:
                    boxes.append([int(p[0])] + [float(x) for x in p[1:5]])

        with Image.open(img_p).convert("RGB") as img:
            img = apply_triple_threat(img, boxes)
            img.save(os.path.join(dst_img_dir, f), quality=95)

        shutil.copy2(lbl_p, os.path.join(dst_lbl_dir, os.path.basename(lbl_p)))

    print(f"✅ Created {len(files)} samples in {dst_root}")

if __name__ == "__main__":
    generate_triple_threat_set("test", "test_bright_triple_threat")