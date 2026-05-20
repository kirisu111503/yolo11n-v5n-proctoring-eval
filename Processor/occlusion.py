import os
import shutil
import random
import math
from PIL import Image, ImageDraw

# ==========================================
# ⚙️  GLOBAL SETTINGS (Easy to Tweak)
# ==========================================
DEFAULT_OCCLUSION_RATIOS = [0.30, 0.40, 0.50, 0.60]
DEFAULT_OCCLUSION_COLOR = (128, 128, 128)  # Grey
SUFFIX = "_occ"
IMG_EXTS = (".jpg", ".jpeg", ".png")

def get_label_path(img_path, image_dir, label_dir):
    """Calculates the corresponding label path based on directory structure."""
    # Find path relative to the image source folder
    rel_path = os.path.relpath(img_path, image_dir)
    base_rel = os.path.splitext(rel_path)[0]
    
    # Construct corresponding label path
    lbl_rel = base_rel + ".txt"
    return os.path.join(label_dir, lbl_rel)

def yolo_to_pixels(yolo_box, img_width, img_height):
    """Convert YOLO normalized coordinates to absolute pixel coordinates."""
    cls, x_c, y_c, w, h = yolo_box
    
    box_w = w * img_width
    box_h = h * img_height
    box_x_center = x_c * img_width
    box_y_center = y_c * img_height
    
    x_min = int(box_x_center - (box_w / 2))
    y_min = int(box_y_center - (box_h / 2))
    x_max = int(box_x_center + (box_w / 2))
    y_max = int(box_y_center + (box_h / 2))
    
    return max(0, x_min), max(0, y_min), min(img_width, x_max), min(img_height, y_max)

def apply_occlusion(img, boxes, ratios=None, color=None):
    """Draws occlusion shapes on the image."""
    if ratios is None: ratios = DEFAULT_OCCLUSION_RATIOS
    if color is None: color = DEFAULT_OCCLUSION_COLOR

    draw = ImageDraw.Draw(img)
    img_w, img_h = img.size
    
    for box in boxes:
        x_min, y_min, x_max, y_max = yolo_to_pixels(box, img_w, img_h)
        
        obj_w = x_max - x_min
        obj_h = y_max - y_min
        obj_area = obj_w * obj_h
        
        if obj_area <= 0: continue

        # Determine Occlusion Size
        ratio = random.choice(ratios)
        target_occ_area = obj_area * ratio
        
        shape_type = random.choice(['rectangle', 'circle'])
        
        # Calculate Shape
        if shape_type == 'rectangle':
            aspect = random.uniform(0.5, 2.0)
            occ_w = int(math.sqrt(target_occ_area * aspect))
            occ_h = int(math.sqrt(target_occ_area / aspect))
            
            # Cap dimensions
            occ_w = min(occ_w, obj_w)
            occ_h = min(occ_h, obj_h)
            
            max_x = obj_w - occ_w
            max_y = obj_h - occ_h
            
            start_x = x_min + random.randint(0, max_x)
            start_y = y_min + random.randint(0, max_y)
            
            draw.rectangle([start_x, start_y, start_x + occ_w, start_y + occ_h], fill=color)
            
        else: # Circle
            radius = int(math.sqrt(target_occ_area / math.pi))
            min_dim = min(obj_w, obj_h)
            radius = min(radius, min_dim // 2)
            diameter = radius * 2
            
            max_x = obj_w - diameter
            max_y = obj_h - diameter
            
            start_x = x_min + random.randint(0, max_x)
            start_y = y_min + random.randint(0, max_y)
            
            draw.ellipse([start_x, start_y, start_x + diameter, start_y + diameter], fill=color)
            
    return img

def parse_label_file(lbl_path):
    """Reads YOLO label file and returns list of boxes."""
    boxes = []
    if not os.path.exists(lbl_path):
        return boxes
        
    with open(lbl_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    cls = int(parts[0])
                    coords = [float(x) for x in parts[1:5]]
                    boxes.append([cls] + coords)
                except ValueError: continue
    return boxes

def get_all_current_images(directory):
    """Snapshot current file list."""
    all_files = []
    print("📸 Taking snapshot of current file list...")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(IMG_EXTS):
                all_files.append(os.path.join(root, file))
    return all_files

def run_augmentation(dataset_root, split="train", img_subdir="images", lbl_subdir="labels"):
    """
    👉 MAIN FUNCTION TO CALL FROM OTHER SCRIPTS.
    
    Args:
        dataset_root (str): The main folder (e.g., "phone_dataset", "book_dataset")
        split (str): The subfolder (e.g., "train", "val", "test")
        img_subdir (str): Name of images folder (default "images")
        lbl_subdir (str): Name of labels folder (default "labels")
    """
    
    # Construct paths dynamically
    image_dir = os.path.join(dataset_root, split, img_subdir)
    label_dir = os.path.join(dataset_root, split, lbl_subdir)

    if not os.path.exists(image_dir):
        print(f"❌ Image directory not found: {image_dir}")
        return 0, 0

    print("=" * 70)
    print(f"🧱 OCCLUSION AUGMENTATION")
    print(f"📂 Dataset: {dataset_root}")
    print(f"📂 Split:   {split}")
    print("=" * 70)
    
    files_to_process = get_all_current_images(image_dir)
    
    if not files_to_process:
        print("✅ No images found.")
        return 0, 0

    print(f"⚡ Processing {len(files_to_process)} images...")
    print("-" * 70)

    success_count = 0
    fail_count = 0
    skip_count = 0

    for i, img_path in enumerate(files_to_process, 1):
        try:
            # 1. Find Label
            lbl_path = get_label_path(img_path, image_dir, label_dir)
            
            # 2. Get Object Boxes
            boxes = parse_label_file(lbl_path)
            
            if not boxes:
                skip_count += 1
                continue

            # 3. Setup New Paths
            directory, filename = os.path.split(img_path)
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}{SUFFIX}{ext}"
            new_img_path = os.path.join(directory, new_filename)
            
            lbl_dir_path, lbl_filename = os.path.split(lbl_path)
            lbl_name, lbl_ext = os.path.splitext(lbl_filename)
            new_lbl_filename = f"{lbl_name}{SUFFIX}{lbl_ext}"
            new_lbl_path = os.path.join(lbl_dir_path, new_lbl_filename)

            # 4. Process & Save
            with Image.open(img_path).convert("RGB") as img:
                aug_img = apply_occlusion(img, boxes)
                aug_img.save(new_img_path, quality=95)

            # 5. Copy Label
            shutil.copy2(lbl_path, new_lbl_path)
            
            success_count += 1
            if i % 100 == 0:
                print(f"   ✅ Processed {i}/{len(files_to_process)}...")

        except Exception as e:
            print(f"❌ Error on {os.path.basename(img_path)}: {e}")
            fail_count += 1

    print("-" * 70)
    print(f"✅ COMPLETED: {dataset_root} ({split})")
    print(f"🎉 Created: {success_count} | Skipped: {skip_count} | Failed: {fail_count}")
    print("=" * 70)
    
    return success_count, fail_count

# ==========================================
# 🚀 STANDALONE MODE
# ==========================================
if __name__ == "__main__":
    print("🛠️  Occlusion Tool Running Standalone")
    target_folder = input("📂 Enter dataset root folder name (e.g., 'book_dataset'): ").strip()
    target_split = input("📂 Enter split to process (default 'train'): ").strip() or "train"
    
    if target_folder:
        run_augmentation(target_folder, target_split)
    else:
        print("❌ No folder provided.")