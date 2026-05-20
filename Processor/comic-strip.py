import os
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# ⚙️ SETTINGS
# ==========================================
# Update this path if your folder structure is different
SOURCE_FOLDER = r"test\step-by-step-augmentation" 
OUTPUT_FILENAME = "Figure_A1_Sequential_Pipeline.jpg"
TEXT_COLOR = (0, 0, 0)       # Black Text
BG_COLOR = (255, 255, 255)   # White Background
FONT_SIZE = 40               # Large font for readability

# Labels for each step
LABELS = [
    "Step 1:\nClean Input",
    "Step 2:\nOcclusion",
    "Step 3:\nIllumination",
    "Step 4:\nBlur"
]

def create_sequential_strip():
    # 1. Find a valid set of images
    if not os.path.exists(SOURCE_FOLDER):
        print(f"❌ Error: Folder not found at: {SOURCE_FOLDER}")
        return

    # Look for files ending in "_0_clean.jpg" (or .png)
    candidates = [f for f in os.listdir(SOURCE_FOLDER) if "_0_clean" in f]
    
    if not candidates:
        print(f"❌ No valid file sets found in {SOURCE_FOLDER}")
        return

    # Pick the first one found
    base_file = candidates[0]
    base_name = base_file.split("_0_clean")[0]
    ext = base_file.split(".")[-1]

    print(f"Processing set: {base_name}...")

    # 2. Construct paths for all 4 steps
    paths = [
        os.path.join(SOURCE_FOLDER, f"{base_name}_0_clean.{ext}"),
        os.path.join(SOURCE_FOLDER, f"{base_name}_1_occluded.{ext}"),
        os.path.join(SOURCE_FOLDER, f"{base_name}_2_brightened.{ext}"),
        os.path.join(SOURCE_FOLDER, f"{base_name}_3_blurred_final.{ext}")
    ]

    images = []
    for p in paths:
        if os.path.exists(p):
            images.append(Image.open(p))
        else:
            print(f"❌ Missing file: {p}")
            return

    # 3. Calculate Dimensions
    w, h = images[0].size
    gap = 20           
    top_margin = 100   
    
    total_width = (w * 4) + (gap * 3)
    total_height = h + top_margin

    # 4. Create the Canvas
    new_img = Image.new('RGB', (total_width, total_height), color=BG_COLOR)
    draw = ImageDraw.Draw(new_img)

    # 5. Load Font (Windows/Local friendly)
    try:
        # Try standard Windows font
        font = ImageFont.truetype("arial.ttf", FONT_SIZE)
    except IOError:
        try:
            # Try standard Linux font
            font = ImageFont.truetype("LiberationSans-Regular.ttf", FONT_SIZE)
        except IOError:
            # Fallback to default (might be small, but works)
            print("⚠️ Warning: Custom fonts not found. Using default.")
            font = ImageFont.load_default()

    # 6. Paste Images and Draw Text
    current_x = 0
    for i, img in enumerate(images):
        # Paste Image
        new_img.paste(img, (current_x, top_margin))
        
        # Draw Text Centered
        label = LABELS[i]
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        text_x = current_x + (w - text_w) // 2
        text_y = (top_margin - text_h) // 2 
        
        draw.text((text_x, text_y), label, fill=TEXT_COLOR, font=font, align="center")
        
        # Move X
        current_x += w + gap

    # 7. Save
    new_img.save(OUTPUT_FILENAME, quality=95)
    print(f"✅ Successfully created: {OUTPUT_FILENAME}")
    print(f"   Located in current directory.")

if __name__ == "__main__":
    create_sequential_strip()