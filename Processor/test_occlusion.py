import os
import shutil
import random
import math
from PIL import Image, ImageDraw

# ==========================================
# ⚙️ SETTINGS
# ==========================================
# These ratios determine how much of the object is covered (30% to 60%)
OCCLUSION_RATIOS = [0.30, 0.40, 0.50, 0.60]
OCC_COLOR = (128, 128, 128)  # Neutral Grey
IMG_EXTS = (".jpg", ".jpeg", ".png")

def yolo_to_pixels(yolo_box, img_width, img_height):
    cls, x_c, y_c, w, h = yolo_box
    bw, bh = w * img_width, h * img_height
    x_min = int((x_c * img_width) - (bw / 2))
    y_min = int((y_c * img_height) - (bh / 2))
    return max(0, x_min), max(0, y_min), min(img_width, int(x_min + bw)), min(img_height, int(y_min + bh))

def apply_occlusion(img, boxes):
    draw = ImageDraw.Draw(img)
    w, h = img.size
    for box in boxes:
        x1, y1, x2, y2 = yolo_to_pixels(box, w, h)
        obj_w, obj_h = x2 - x1, y2 - y1
        if obj_w <= 5 or obj_h <= 5: continue # Skip tiny boxes

        # Pick a random ratio for this specific object
        ratio = random.choice(OCCLUSION_RATIOS)
        target_area = (obj_w * obj_h) * ratio
        
        # Create a rectangular occlusion block
        aspect = random.uniform(0.7, 1.4) # Keep it somewhat square-ish
        occ_w = int(math.sqrt(target_area * aspect))
        occ_h = int(math.sqrt(target_area / aspect))
        
        # Ensure block isn't bigger than the object itself
        occ_w, occ_h = min(occ_w, obj_w), min(occ_h, obj_h)
        
        # Randomly place the block inside the bounding box
        offset_x = random.randint(0, obj_w - occ_w)
        offset_y = random.randint(0, obj_h - occ_h)
        
        draw.rectangle([x1 + offset_x, y1 + offset_y, x1 + offset_x + occ_w, y1 + offset_y + occ_h], fill=OCC_COLOR)
    return img

def generate_occ_test_set(source_folder, output_folder):
    """Generates the test_occ folder with images and original labels."""
    src_images = os.path.join(source_folder, "images")
    src_labels = os.path.join(source_folder, "labels")
    
    out_images = os.path.join(output_folder, "images")
    out_labels = os.path.join(output_folder, "labels")

    os.makedirs(out_images, exist_ok=True)
    os.makedirs(out_labels, exist_ok=True)

    files = [f for f in os.listdir(src_images) if f.lower().endswith(IMG_EXTS)]
    print(f"🚀 Generating {len(files)} occluded images into '{output_folder}'...")

    for f in files:
        img_p = os.path.join(src_images, f)
        lbl_p = os.path.join(src_labels, f.rsplit('.', 1)[0] + ".txt")

        if not os.path.exists(lbl_p): continue

        # 1. Read multi-class labels
        boxes = []
        with open(lbl_p, 'r') as file:
            for line in file:
                p = line.strip().split()
                if len(p) >= 5:
                    boxes.append([int(p[0])] + [float(x) for x in p[1:5]])

        # 2. Occlude and Save
        with Image.open(img_p).convert("RGB") as img:
            img = apply_occlusion(img, boxes)
            img.save(os.path.join(out_images, f), quality=95)

        # 3. Copy labels (YOLO coordinates stay the same)
        shutil.copy2(lbl_p, os.path.join(out_labels, os.path.basename(lbl_p)))

    print(f"✅ Done! You can now test the model on {output_folder}")

if __name__ == "__main__":
    # Point this to your original 'test' folder
    generate_occ_test_set("test", "test_occ")