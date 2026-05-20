import os
import shutil

# Configuration
ROOT_FOLDER = ""
SPLIT = "test"  # Change to 'val' or 'test' to check those folders
IMAGE_DIR = f"{ROOT_FOLDER}{SPLIT}/images"
LABEL_DIR = f"{ROOT_FOLDER}{SPLIT}/labels"

IMG_EXTS = {".jpg", ".jpeg", ".png"}
TXT_EXT = ".txt"

def get_file_map(directory, extensions):
    """
    Scans a directory and returns a dictionary: {basename: full_filename}
    Example: {'image_01': 'image_01.jpg'}
    """
    file_map = {}
    if not os.path.exists(directory):
        return file_map
        
    for file in os.listdir(directory):
        base, ext = os.path.splitext(file)
        if ext.lower() in extensions:
            file_map[base] = file
            
    return file_map

def main():
    if not os.path.exists(IMAGE_DIR) or not os.path.exists(LABEL_DIR):
        print("❌ Directories not found. Check your paths.")
        print(f"   Images: {IMAGE_DIR}")
        print(f"   Labels: {LABEL_DIR}")
        return

    print("=" * 70)
    print(f"🧹 DATASET INTEGRITY CHECK: {SPLIT.upper()}")
    print("=" * 70)
    print(f"📂 Scanning images in: {IMAGE_DIR}")
    print(f"📂 Scanning labels in: {LABEL_DIR}")
    print()

    # 1. Map all files
    img_map = get_file_map(IMAGE_DIR, IMG_EXTS)
    lbl_map = get_file_map(LABEL_DIR, {TXT_EXT})

    img_bases = set(img_map.keys())
    lbl_bases = set(lbl_map.keys())

    # 2. Identify Mismatches
    # Images without labels
    orphan_images = img_bases - lbl_bases
    # Labels without images
    orphan_labels = lbl_bases - img_bases
    
    # Valid pairs (Intersection)
    valid_pairs = img_bases & lbl_bases

    print("-" * 70)
    print(f"📊 REPORT:")
    print(f"   ✅ Valid Pairs:      {len(valid_pairs)}")
    print(f"   ⚠️  Orphan Images:    {len(orphan_images)} (Image exists, No label)")
    print(f"   ⚠️  Orphan Labels:    {len(orphan_labels)} (Label exists, No image)")
    print("-" * 70)

    if not orphan_images and not orphan_labels:
        print("✅ INTEGRITY CHECK PASSED! No issues found.")
        return

    # 3. List Mismatches (first 5 examples)
    if orphan_images:
        print("\n🔍 Example Orphan Images (No .txt found):")
        for base in list(orphan_images)[:5]:
            print(f"   - {img_map[base]}")
        if len(orphan_images) > 5: print(f"   ...and {len(orphan_images) - 5} others")

    if orphan_labels:
        print("\n🔍 Example Orphan Labels (No image found):")
        for base in list(orphan_labels)[:5]:
            print(f"   - {lbl_map[base]}")
        if len(orphan_labels) > 5: print(f"   ...and {len(orphan_labels) - 5} others")

    # 4. Action Menu
    print("\n🛠️  FIX ACTIONS:")
    print("   1. [Dry Run] Do nothing, just exit")
    print("   2. DELETE Orphan Images (Keep labels clean)")
    print("   3. DELETE Orphan Labels (Clean up garbage txt files)")
    print("   4. DELETE ALL Orphans (Recommended for clean training)")

    try:
        choice = input("\nSelect action (1-4): ")
        if choice == '1':
            print("👋 Exiting without changes.")
            return
        elif choice == '2':
            mode = 'img_only'
        elif choice == '3':
            mode = 'lbl_only'
        elif choice == '4':
            mode = 'all'
        else:
            print("❌ Invalid input.")
            return
    except:
        return

    print("\n" + "=" * 70)
    print("🗑️  CLEANING IN PROGRESS...")
    print("=" * 70)

    deleted_count = 0

    # Delete Orphan Images
    if mode in ['img_only', 'all'] and orphan_images:
        for base in orphan_images:
            file_name = img_map[base]
            file_path = os.path.join(IMAGE_DIR, file_name)
            try:
                os.remove(file_path)
                print(f"   ❌ Deleted Image: {file_name}")
                deleted_count += 1
            except OSError as e:
                print(f"   ⚠️  Failed to delete {file_name}: {e}")

    # Delete Orphan Labels
    if mode in ['lbl_only', 'all'] and orphan_labels:
        for base in orphan_labels:
            file_name = lbl_map[base]
            file_path = os.path.join(LABEL_DIR, file_name)
            try:
                os.remove(file_path)
                print(f"   ❌ Deleted Label: {file_name}")
                deleted_count += 1
            except OSError as e:
                print(f"   ⚠️  Failed to delete {file_name}: {e}")

    print("-" * 70)
    print(f"✨ CLEANUP COMPLETE. Removed {deleted_count} files.")
    print("=" * 70)

if __name__ == "__main__":
    main()