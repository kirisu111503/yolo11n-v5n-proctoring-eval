import shutil
import sys
from pathlib import Path

def merge_datasets(source_datasets, output_dir, add_prefix=True):
    """
    Merge multiple datasets into a single folder with a progress bar.
    """
    output_path = Path(output_dir)
    output_images = output_path / 'images'
    output_labels = output_path / 'labels'
    
    output_images.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
    all_tasks = []

    # Step 1: Gather all valid image-label pairs first to calculate total count
    for source in source_datasets:
        source_path = Path(source)
        if not source_path.exists():
            continue
            
        img_folder = source_path / 'images'
        lbl_folder = source_path / 'labels'
        dataset_name = source_path.parent.name 
        
        image_files = {img.stem: img for img in img_folder.iterdir() if img.suffix.lower() in image_extensions}
        label_files = {lbl.stem: lbl for lbl in lbl_folder.glob('*.txt')}
        matched_stems = set(image_files.keys()) & set(label_files.keys())
        
        for stem in matched_stems:
            all_tasks.append((image_files[stem], label_files[stem], dataset_name))

    total_files = len(all_tasks)
    if total_files == 0:
        print(f"   No files found for this split.")
        return 0

    # Step 2: Copy files with visual progress
    for i, (img_path, lbl_path, dataset_name) in enumerate(all_tasks, 1):
        new_stem = f"{dataset_name}_{img_path.stem}" if add_prefix else img_path.stem
        
        shutil.copy2(img_path, output_images / f"{new_stem}{img_path.suffix}")
        shutil.copy2(lbl_path, output_labels / f"{new_stem}.txt")
        
        # Simple Progress Bar Calculation
        percent = (i / total_files) * 100
        bar_length = 30
        filled_length = int(bar_length * i // total_files)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        # \r allows the line to overwrite itself in the terminal
        sys.stdout.write(f'\r   Progress: |{bar}| {percent:.1f}% ({i}/{total_files})')
        sys.stdout.flush()

    print() # New line after progress bar finishes
    return total_files

def verify_merged_dataset(output_dir):
    out = Path(output_dir)
    img_count = len(list((out / 'images').glob('*')))
    lbl_count = len(list((out / 'labels').glob('*.txt')))
    status = "✅ OK" if img_count == lbl_count else "❌ MISMATCH"
    print(f"   Summary: {img_count} images | {lbl_count} labels | {status}")

if __name__ == "__main__":
    DATASET_NAMES = ['phone_dataset', 'calculator_dataset', 'book_dataset']
    SPLITS = ['train', 'test', 'val']
    MASTER_OUTPUT = 'dataset'

    print("🚀 Starting YOLOv11 Dataset Merger...")

    for split in SPLITS:
        sources = [f"{ds}/{split}" for ds in DATASET_NAMES]
        dest = f"{MASTER_OUTPUT}/{split}"
        
        print(f"\nProcessing {split.upper()} split...")
        total = merge_datasets(sources, dest, add_prefix=True)
        if total > 0:
            verify_merged_dataset(dest)

    print(f"\n✅ All tasks complete. Dataset ready at: ./{MASTER_OUTPUT}")