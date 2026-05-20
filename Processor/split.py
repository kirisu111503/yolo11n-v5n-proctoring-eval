import os
import shutil
import random

# Default Configuration
DEFAULT_CONFIG = {
    "source_image_dir": "images",
    "source_label_dir": "labels",
    "output_root": "phone_dataset",
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,
    "max_total": 1786,
    "img_extensions": (".jpg", ".jpeg", ".png")
}


def get_image_label_pairs(source_image_dir, source_label_dir, img_extensions):
    """Get all valid image-label pairs."""
    pairs = []
    
    if not os.path.exists(source_image_dir):
        print(f"❌ Image directory not found: {source_image_dir}")
        return pairs
    
    if not os.path.exists(source_label_dir):
        print(f"❌ Label directory not found: {source_label_dir}")
        return pairs
    
    for file in os.listdir(source_image_dir):
        if file.lower().endswith(img_extensions):
            base = os.path.splitext(file)[0]
            
            # Check if corresponding label exists
            label_file = base + ".txt"
            label_path = os.path.join(source_label_dir, label_file)
            
            if os.path.exists(label_path):
                pairs.append((file, label_file))
    
    return pairs


def copy_files(pairs, source_image_dir, source_label_dir, dest_img_dir, dest_lbl_dir, split_name):
    """Copy image-label pairs to destination directories."""
    os.makedirs(dest_img_dir, exist_ok=True)
    os.makedirs(dest_lbl_dir, exist_ok=True)
    
    copied = 0
    failed = 0
    
    for img_file, lbl_file in pairs:
        try:
            # Source paths
            src_img = os.path.join(source_image_dir, img_file)
            src_lbl = os.path.join(source_label_dir, lbl_file)
            
            # Destination paths
            dst_img = os.path.join(dest_img_dir, img_file)
            dst_lbl = os.path.join(dest_lbl_dir, lbl_file)
            
            # Copy files
            shutil.copy2(src_img, dst_img)
            shutil.copy2(src_lbl, dst_lbl)
            
            copied += 1
            
            if copied % 100 == 0:
                print(f"   📦 {split_name}: Copied {copied}/{len(pairs)} files...")
        
        except Exception as e:
            failed += 1
            print(f"   ⚠️  Failed to copy {img_file}: {e}")
    
    return copied, failed


def split_dataset(config=None, interactive=True):
    """
    Split dataset into train/val/test sets.
    
    Args:
        config (dict): Configuration dictionary with keys matching DEFAULT_CONFIG
        interactive (bool): Whether to prompt for user confirmation
    
    Returns:
        dict: Results with keys 'success', 'train_count', 'val_count', 'test_count', 'failed'
    """
    # Merge with defaults
    cfg = DEFAULT_CONFIG.copy()
    if config:
        cfg.update(config)
    
    # Extract config values
    source_image_dir = cfg["source_image_dir"]
    source_label_dir = cfg["source_label_dir"]
    output_root = cfg["output_root"]
    train_ratio = cfg["train_ratio"]
    val_ratio = cfg["val_ratio"]
    test_ratio = cfg["test_ratio"]
    max_total = cfg["max_total"]
    img_extensions = cfg["img_extensions"]
    
    # Output directories
    train_image_dir = f"{output_root}/train/images"
    train_label_dir = f"{output_root}/train/labels"
    val_image_dir = f"{output_root}/val/images"
    val_label_dir = f"{output_root}/val/labels"
    test_image_dir = f"{output_root}/test/images"
    test_label_dir = f"{output_root}/test/labels"
    
    print("=" * 70)
    print(f"📊 DATASET SPLITTER: {output_root}")
    print("=" * 70)
    print(f"📈 Target Split: {int(train_ratio*100)}% Train / {int(val_ratio*100)}% Val / {int(test_ratio*100)}% Test")
    print()

    # 1. Get all valid pairs
    pairs = get_image_label_pairs(source_image_dir, source_label_dir, img_extensions)
    
    if not pairs:
        print("❌ No valid image-label pairs found!")
        return {"success": False, "error": "No valid pairs found"}
    
    print(f"🔍 Found {len(pairs)} valid pairs in source.")

    # 2. Shuffle first to ensure the selection is random
    random.shuffle(pairs)

    # 3. Limit total images to max_total (Balancing step)
    if len(pairs) > max_total:
        print(f"✂️  Trimming dataset from {len(pairs)} down to {max_total} images (Balancing)...")
        pairs = pairs[:max_total]
    else:
        print(f"⚠️  Note: Only {len(pairs)} pairs found. Using all available (Target was {max_total}).")

    # 4. Calculate split sizes based on the capped total
    total = len(pairs)
    train_size = int(total * train_ratio)
    val_size = int(total * val_ratio)
    test_size = total - train_size - val_size  # Remainder for test
    
    print("📊 Final Split distribution:")
    print(f"   Training:   {train_size} images")
    print(f"   Validation: {val_size} images")
    print(f"   Test:       {test_size} images")

    # Check if dataset folder exists
    if os.path.exists(output_root):
        print(f"⚠️  '{output_root}' folder already exists!")
        if interactive:
            overwrite = input("   Overwrite existing dataset? (y/n): ")
            if overwrite.lower() != 'y':
                print("❌ Cancelled.")
                return {"success": False, "error": "User cancelled"}
        print(f"   Removing existing {output_root} folder...")
        shutil.rmtree(output_root)
    
    if interactive:
        proceed = input(f"🚀 Proceed with split? (y/n): ")
        if proceed.lower() != 'y':
            print("❌ Cancelled.")
            return {"success": False, "error": "User cancelled"}

    print("\n" + "=" * 70)
    print("🔄 Splitting dataset...")
    print("=" * 70)
    
    # Split the pairs
    train_pairs = pairs[:train_size]
    val_pairs = pairs[train_size:train_size + val_size]
    test_pairs = pairs[train_size + val_size:]
    
    # Copy sets
    print("\n📁 Creating training set...")
    train_copied, train_failed = copy_files(
        train_pairs, source_image_dir, source_label_dir,
        train_image_dir, train_label_dir, "Train"
    )
    
    print("\n📁 Creating validation set...")
    val_copied, val_failed = copy_files(
        val_pairs, source_image_dir, source_label_dir,
        val_image_dir, val_label_dir, "Val"
    )
    
    print("\n📁 Creating test set...")
    test_copied, test_failed = copy_files(
        test_pairs, source_image_dir, source_label_dir,
        test_image_dir, test_label_dir, "Test"
    )
    
    print("\n" + "=" * 70)
    print("✅ SPLIT COMPLETED!")
    print("=" * 70)
    print(f"📊 Training set:   {train_copied:,} pairs copied")
    print(f"📊 Validation set: {val_copied:,} pairs copied")
    print(f"📊 Test set:       {test_copied:,} pairs copied")
    
    total_failed = train_failed + val_failed + test_failed
    if total_failed > 0:
        print(f"⚠️  Total failed:   {total_failed}")
    
    print()
    print(f"📂 Output Location: {os.path.abspath(output_root)}")
    print("=" * 70)
    
    return {
        "success": True,
        "train_count": train_copied,
        "val_count": val_copied,
        "test_count": test_copied,
        "failed": total_failed,
        "output_path": os.path.abspath(output_root)
    }


def main():
    """CLI entry point."""
    split_dataset(interactive=True)


if __name__ == "__main__":
    main()