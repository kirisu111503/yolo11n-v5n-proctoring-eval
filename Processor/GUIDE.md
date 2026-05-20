# YOLOv11 Robustness Testing & Dataset Augmentation Pipeline

A comprehensive Python toolkit for testing YOLOv11 object detection model robustness through systematic data augmentation. This project generates stress-test datasets with various environmental challenges (darkness, blur, occlusion) to evaluate model performance under real-world conditions.

---

## Project Overview

This thesis project focuses on evaluating how well YOLOv11 models perform when exposed to challenging real-world scenarios:
- **Low lighting conditions** (darkness/brightness variations)
- **Motion blur and focus blur**
- **Object occlusion** (partial/full coverage)
- **Compound challenges** (multiple effects combined)

The toolkit provides automated pipelines to split datasets, apply augmentations, generate test sets, and analyze model performance metrics.

---

## Repository Structure

### Core Pipeline Scripts

- **`head.py`** - Master orchestrator
  - Processes multi-class datasets organized by category (book, phone, calculator, etc.)
  - Sequentially applies split → brightness → blur → occlusion augmentations
  - Expects input folders with `images/` and `labels/` subfolders
  - Generates `{category}_dataset/train/val/test` output structure

- **`split.py`** - Dataset splitter
  - Divides raw image-label pairs into train/val/test sets
  - Supports configurable split ratios (default: 70/15/15)
  - Enforces image-label pairing validation
  - Caps maximum dataset size for balanced sampling

- **`merge.py`** - Dataset merger
  - Combines multiple split datasets into a single unified dataset
  - Supports progress tracking and integrity verification
  - Optional prefix naming for source dataset tracking

---

### Single Augmentation Scripts

#### Blur Effects
- **`blur.py`** - Gaussian blur augmentation
  - Applies fixed blur radius to dataset images
  - Saves blurred copies in-place with suffix naming
  - Preserves label files unchanged

- **`test_blur.py`** - Blur test set generator
  - Creates dedicated blurred test dataset from original test images
  - Configurable blur radius (default: 2.0px)

#### Brightness/Darkness Effects
- **`brightness.py`** - Brightness augmentation
  - Generates multiple brightness variations per image
  - Supports fixed steps (0.7, 0.85, 1.0, 1.15, 1.3) or random modes
  - Useful for simulating lighting conditions

- **`test_brightness.py`** - Brightness test set generator
  - Creates both bright (1.5x) and dark (0.5x) test variants
  - Useful for evaluating model under extreme lighting

#### Occlusion Effects
- **`occlusion.py`** - Standalone occlusion tool
  - Applies random rectangular/circular occlusion shapes to detected objects
  - Covers 30-60% of object area per instance
  - Supports custom ratios and colors
  - Can be imported and used by other scripts

- **`test_occlusion.py`** - Occlusion test set generator
  - Creates occluded test dataset from original test images
  - Randomly places occlusion blocks within bounding boxes

---

### Compound Augmentation Scripts

These scripts apply multiple effects in sequence for stress testing:

- **`apply_triple_threat.py`** - Step-by-step visualization pipeline
  - Saves intermediate augmentation stages: original → occluded → brightened → blurred
  - Useful for creating figure visualizations
  - Generates 4 sequential images per input

- **`blur_occlusion.py`** - Occlusion + Blur
  - Order: occlusion first, then blur
  - Creates test_blur_occlusion dataset

- **`brightness_blur.py`** - Darkness + Blur
  - Order: darkness (0.5x brightness), then blur
  - Simulates low-light motion blur scenario
  - Creates test_blur_bright dataset

- **`brightness_occlusion.py`** - Darkness + Occlusion
  - Order: darkness first, then occlusion
  - Tests detection under low light with partial coverage

- **`bright_blur_occlusion.py`** - Brightness + Blur + Occlusion
  - Order: occlusion → brightness → blur
  - Triple stress test with all effects

- **`dark_blur.py`** - Darkness + Blur
  - Order: darkness (0.5x), then blur
  - Creates test_dark_blur dataset

- **`dark_occlusion.py`** - Darkness + Occlusion
  - Order: darkness (0.5x), then occlusion
  - Tests in low-light conditions

- **`dark_blur_occlusion.py`** - Darkness + Blur + Occlusion
  - All three effects in sequence
  - Maximum stress test scenario

---

### Evaluation & Analysis Scripts

- **`analyze.py`** - Model validation analyzer
  - Loads trained YOLOv11 model
  - Runs validation on test split with detailed metrics
  - Outputs: mAP50-95, mAP50, Precision, Recall
  - Generates confusion matrices and F1-curves

- **`test.py`** - Real-time inference tester
  - Runs inference on test images or live webcam feed
  - Displays detection results with confidence scores
  - Saves annotated output images to `runs/detect/predict`

- **`match.py`** - Dataset integrity checker
  - Scans for orphan images (images without labels)
  - Scans for orphan labels (labels without images)
  - Interactive cleanup options to remove mismatches

---

### Visualization

- **`comic-strip.py`** - Visual pipeline generator
  - Creates a composite "comic strip" image showing 4 augmentation stages
  - Useful for thesis figures and presentations
  - Reads from step-by-step-augmentation folder output

---

### Jupyter Notebooks

- **`yolov11n.ipynb`** - YOLOv11 Nano experiments
  - Model training, evaluation, and testing workflows

- **`yolov5n.ipynb`** - YOLOv5 Nano experiments
  - Comparison baseline experiments

---

## Dataset Structure

### Expected Input Format (Raw Data)

```
book/
├── images/
│   ├── book_001.jpg
│   ├── book_002.jpg
│   └── ...
└── labels/
    ├── book_001.txt
    ├── book_002.txt
    └── ...

phone/
├── images/
└── labels/

calculator/
├── images/
└── labels/
```

### Output Format (After Pipeline)

```
book_dataset/
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/

phone_dataset/
├── train/
├── val/
└── test/

calculator_dataset/
├── train/
├── val/
└── test/

dataset/ (merged)
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

### Label Format (YOLO)

Text files with one detection per line:
```
<class_id> <x_center> <y_center> <width> <height>
```
- All coordinates are normalized (0.0 to 1.0)
- Class IDs are integers (0, 1, 2, ...)

---

## Usage Guide

### 1. Split Dataset

```bash
python split.py
```
- Interactive mode prompts for confirmation
- Splits into 70% train, 15% val, 15% test
- Creates output folder with subfolder structure

**Programmatic usage:**
```python
from split import split_dataset

config = {
    "source_image_dir": "book/images",
    "source_label_dir": "book/labels",
    "output_root": "book_dataset",
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,
}

split_dataset(config=config, interactive=False)
```

### 2. Apply Augmentations to Training Data

#### Using Master Pipeline (Recommended)
```bash
python head.py
```
Automatically processes all categories and applies all augmentations in sequence.

#### Manual Augmentation Steps
```bash
# Brightness augmentation
python brightness.py

# Blur augmentation
python blur.py

# Occlusion augmentation
python occlusion.py
```

### 3. Generate Test Sets

Create stress-test variants without affecting training data:

```bash
# Individual effects
python test_blur.py          # Creates test_blur/
python test_brightness.py    # Creates test_bright/ and test_dark/
python test_occlusion.py     # Creates test_occ/

# Compound effects
python blur_occlusion.py     # Creates test_blur_occlusion/
python brightness_blur.py    # Creates test_blur_bright/
python dark_blur.py          # Creates test_dark_blur/
```

### 4. Analyze Model Performance

```bash
# Full validation analysis
python analyze.py

# Live inference testing
python test.py

# Dataset integrity check
python match.py
```

### 5. Merge Datasets

```bash
python merge.py
```
Combines split datasets from multiple categories into a single unified dataset.

### 6. Generate Visualizations

```bash
python apply_triple_threat.py    # Creates step-by-step images
python comic-strip.py             # Creates composite figure
```

---

## Configuration

### Key Parameters

#### Blur Settings
- `BLUR_RADIUS`: Gaussian blur strength (default: 2.0-2.5px)
  - 0.5 = light blur
  - 2.0-3.0 = moderate blur (good for testing)
  - 5.0+ = heavy blur

#### Brightness/Darkness
- `BRIGHTNESS_FACTOR`: Multiplier for brightness
  - 0.5 = 50% darker
  - 1.0 = original
  - 1.5 = 50% brighter

#### Occlusion
- `OCCLUSION_RATIOS`: Coverage percentages `[0.30, 0.45, 0.60]`
  - Controls how much of the object is hidden
- `OCC_COLOR`: RGB tuple for occlusion blocks
  - `(128, 128, 128)` = neutral grey
  - `(40, 40, 40)` = dark grey (for low-light scenarios)

#### Dataset
- `max_total`: Cap on dataset size (default: 1786)
- Split ratios: train/val/test proportions

---

## Dependencies

```bash
pip install Pillow ultralytics opencv-python torch torchvision
```

### Key Libraries
- **Pillow**: Image manipulation (blur, brightness, occlusion)
- **Ultralytics**: YOLOv11 training and inference
- **OpenCV**: Video/webcam input for inference
- **PyTorch**: Deep learning backend

---

## Model Setup

### Training
Use the Jupyter notebooks to train YOLOv11 on your augmented dataset:
```bash
jupyter notebook yolov11n.ipynb
```

### Inference
Point the model path in `test.py` and `analyze.py`:
```python
MODEL_PATH = './yolov11_training_results/weights/best.pt'
```

---

## Quick Start & Execution Sequence

### ⚡ **Fastest Path (Automated)**

If you want to automate everything with the master pipeline:

```bash
# Step 1: Organize raw data
# Create folders: book/, phone/, calculator/ (each with images/ and labels/ subfolders)

# Step 2: Run master pipeline (handles everything)
python head.py

# Step 3: Train model
jupyter notebook yolov11n.ipynb

# Step 4: Generate stress-test datasets
python test_blur.py
python test_brightness.py
python test_occlusion.py
python blur_occlusion.py
python brightness_blur.py
python dark_blur.py
python dark_occlusion.py
python dark_blur_occlusion.py

# Step 5: Evaluate robustness
python analyze.py
```

---

### 🔧 **Manual Control Path (Step-by-Step)**

If you want fine-grained control over each augmentation:

```bash
# Step 1: Split your dataset
python split.py
# Follow prompts to configure split ratios and confirm

# Step 2: Apply training augmentations individually
python brightness.py    # Generates brightness variations (original + augmented)
python blur.py         # Blurs all images in dataset (including newly augmented ones)
python occlusion.py    # Adds occlusion to all images (building on previous augmentations)

# Step 3: (Optional) Verify dataset integrity
python match.py

# Step 4: Train your model
jupyter notebook yolov11n.ipynb

# Step 5: Generate independent test variants (can run in any order)
python test_blur.py                  # Original test set + blur
python test_brightness.py            # Original test set + bright/dark variants
python test_occlusion.py             # Original test set + occlusion
python blur_occlusion.py             # Original test set + occlusion + blur
python brightness_blur.py            # Original test set + dark + blur
python dark_blur.py                  # Original test set + dark + blur (variant)
python dark_occlusion.py             # Original test set + dark + occlusion
python dark_blur_occlusion.py        # Original test set + dark + blur + occlusion

# Step 6: Create visualizations
python apply_triple_threat.py        # Step-by-step augmentation images
python comic-strip.py                # Composite figure for thesis

# Step 7: Evaluate on all test variants
python analyze.py                    # Run multiple times with different test folders
```

---

### **Pre-Execution Checklist**

Before running any scripts, ensure:

- [ ] **Python 3.8+** installed
- [ ] **Dependencies installed**: `pip install Pillow ultralytics opencv-python torch torchvision`
- [ ] **Raw data organized** in proper folder structure:
  ```
  book/images/       (at least 10 images)
  book/labels/       (matching .txt files)
  phone/images/
  phone/labels/
  calculator/images/
  calculator/labels/
  ```
- [ ] **Label format correct**: YOLO format with normalized coordinates
  ```
  0 0.5 0.5 0.4 0.3
  1 0.3 0.7 0.2 0.4
  ```
- [ ] **Working directory** is the root of this project
- [ ] **No existing output folders** (or you're ready to overwrite them)

---

### **Script Dependency & Execution Order**

```
PHASE 1: PREPARATION
├─ match.py (optional, check data integrity first)
└─ split.py (REQUIRED - creates folder structure)

PHASE 2: TRAINING AUGMENTATION (Sequential - each builds on previous)
├─ brightness.py (optional - generates brightness variations)
├─ blur.py (optional - blurs images including augmented ones)
└─ occlusion.py (optional - adds occlusion to all images)

        OR use head.py to automate all of Phase 1 & 2

PHASE 3: MODEL TRAINING (Jupyter)
└─ yolov11n.ipynb (train your model on augmented data)

PHASE 4: TEST SET GENERATION (All independent - run in any order)
├─ test_blur.py
├─ test_brightness.py
├─ test_occlusion.py
├─ blur_occlusion.py
├─ brightness_blur.py
├─ dark_blur.py
├─ dark_occlusion.py
└─ dark_blur_occlusion.py

PHASE 5: VISUALIZATION & EVALUATION
├─ apply_triple_threat.py (creates step-by-step images)
├─ comic-strip.py (creates composite figure)
├─ analyze.py (evaluate model on each test set)
└─ test.py (live inference testing)

PHASE 6: MERGING (Optional - if combining multiple datasets)
└─ merge.py (combines split datasets into one)
```

---

### **Common Workflows**

#### **Workflow A: Full Thesis Evaluation** *(Recommended)*
```bash
# 1. Prepare and split
python match.py                     # Check data integrity
python head.py                      # Orchestrate split + augmentations

# 2. Train
jupyter notebook yolov11n.ipynb     # Train model on augmented data

# 3. Test robustness on all variants
for file in test_*.py blur_*.py brightness_*.py dark_*.py; do
    python "$file"
done

# 4. Generate results
python analyze.py                   # Run multiple times per test variant
python comic-strip.py               # Create figures for thesis

# 5. (Optional) Merge datasets
python merge.py
```

#### **Workflow B: Quick Test** *(Fast feedback)*
```bash
# 1. Quick split
python split.py

# 2. Train
jupyter notebook yolov11n.ipynb

# 3. Quick evaluation
python test_blur.py
python analyze.py
```

#### **Workflow C: Custom Augmentation** *(Fine-tuned control)*
```bash
# 1. Split with custom ratios
python split.py

# 2. Apply specific augmentations only
python brightness.py       # If you only want brightness variations
# Skip blur.py and occlusion.py if not needed

# 3. Train
jupyter notebook yolov11n.ipynb

# 4. Test specific scenarios
python test_brightness.py
python analyze.py
```

#### **Workflow D: Stress Testing Only** *(Testing existing model)*
```bash
# Skip training, generate test sets from existing original test folder
python test_blur.py
python test_brightness.py
python test_occlusion.py
python blur_occlusion.py
python dark_blur_occlusion.py

# Evaluate existing model
python analyze.py                   # Point to your trained weights
python test.py                      # Run live inference
```

---

### **Configuration Before Running**

Edit these settings in the respective script files:

**Before `split.py`:**
```python
train_ratio = 0.70      # Change split percentages
val_ratio = 0.15
test_ratio = 0.15
max_total = 1786        # Cap dataset size
```

**Before `brightness.py`:**
```python
brightness_range = (0.7, 1.3)      # Min to max brightness
brightness_steps = [0.7, 0.85, 1.0, 1.15, 1.3]  # Specific values
```

**Before `blur.py`:**
```python
blur_radius = 0.5       # 0.5=light, 2.0-3.0=moderate, 5.0+=heavy
```

**Before `occlusion.py`:**
```python
OCCLUSION_RATIOS = [0.30, 0.45, 0.60]  # Coverage percentages
OCC_COLOR = (128, 128, 128)             # RGB for occlusion blocks
```

**Before `analyze.py` or `test.py`:**
```python
MODEL_PATH = './yolov11_training_results/weights/best.pt'  # Point to your trained model
```

---

### **Expected Execution Times**

| Script | Input Size | Typical Time | Notes |
|--------|-----------|-------------|-------|
| `split.py` | 1000 images | ~5-10 sec | Fast file copying |
| `brightness.py` | 700 images (train) | ~30-60 sec | Generates variations |
| `blur.py` | 1400+ images (including augmented) | ~2-5 min | Processes each image |
| `occlusion.py` | 2000+ images | ~3-10 min | Reads labels, draws shapes |
| `head.py` | Full pipeline | ~10-20 min | Runs all phases sequentially |
| `test_*.py` | 150 test images | ~10-30 sec | Generates one variant |
| `analyze.py` | 150 images + model | ~2-5 min | Validation with metrics |
| `yolov11n.ipynb` | Augmented dataset | 30-120 min | GPU-dependent; can be hours |

---

### **Troubleshooting Execution Issues**

| Problem | Cause | Solution |
|---------|-------|----------|
| `FileNotFoundError: images/ not found` | Wrong directory structure | Verify you're in project root; check folder structure |
| `KeyError` in `head.py` | Categories folder missing | Create `book/`, `phone/`, `calculator/` folders |
| Script hangs or is very slow | Processing large dataset | Reduce `max_total` in `split.py` or use smaller dataset |
| `ModuleNotFoundError: No module named 'PIL'` | Dependencies not installed | Run `pip install Pillow ultralytics opencv-python torch` |
| Label coordinates look wrong | YOLO format issue | Labels must be normalized (0.0-1.0), not pixel values |
| `analyze.py` shows 0 detections | Wrong model path | Update `MODEL_PATH` to your trained weights location |
| Out of memory error | Dataset too large | Reduce `max_total` or process in smaller batches |

---

### **Monitoring Progress**

All scripts print progress indicators:
```
✅ Processed 100/1000...
🌫️  Generating Blur + Occlusion Set...
🧱 OCCLUSION AUGMENTATION
Progress: |████████████--------| 75.0%
```

- Green checkmarks (✅) = successful operations
- Yellow warnings (⚠️) = skipped files (usually orphan images)
- Red errors (❌) = failed files (check logs)
- Progress bars show completion percentage

---

## Expected Workflow

1. **Prepare raw data** → Organize into `book/`, `phone/`, `calculator/` folders
2. **Run pipeline** → Execute `python head.py` (automated) OR follow manual steps
3. **Check data** → Run `python match.py` to verify no orphan files
4. **Train model** → Use `yolov11n.ipynb` with augmented training data
5. **Generate test sets** → Run all `test_*.py` and compound augmentation scripts
6. **Evaluate robustness** → Run `python analyze.py` on each test variant
7. **Visualize results** → `python comic-strip.py` and `apply_triple_threat.py` for thesis figures
8. **(Optional) Merge** → `python merge.py` to combine multiple datasets

---

## Evaluation Metrics

The `analyze.py` script reports:

- **mAP50-95**: Mean Average Precision across all IoU thresholds (0.5-0.95)
- **mAP50**: Mean Average Precision at IoU=0.5
- **Precision**: True positives / (true positives + false positives)
- **Recall**: True positives / (true positives + false negatives)

---

## Notes

- All augmentations preserve label coordinates (bounding boxes don't move)
- Labels are copied as-is during augmentation
- For thesis work, blur radius 2.0-3.0 provides good challenge without being unrealistic
- Compound augmentations are applied in specific order (see script descriptions)
- The master pipeline (`head.py`) only augments training data, leaving val/test untouched

---

## Troubleshooting

**Issue: No matching image-label pairs found**
- Solution: Ensure `.txt` label files have matching basenames as images
- Run `match.py` to identify and clean orphans

**Issue: Missing model file error in `test.py`**
- Solution: Update `MODEL_PATH` to point to your trained weights
- Expected path: `./yolov11_training_results/weights/best.pt`

**Issue: Occlusion ratios seem too aggressive**
- Solution: Adjust `OCCLUSION_RATIOS` in relevant script (e.g., 0.15-0.30 for lighter occlusion)

**Issue: Blur is too subtle or too strong**
- Solution: Adjust `BLUR_RADIUS` (try 1.5 for lighter, 3.5 for stronger)

---

## Author Notes

This toolkit was developed for an undergraduate CS thesis focused on evaluating YOLOv11 robustness under environmental stress. It provides a systematic way to:
- Generate reproducible stress-test datasets
- Isolate individual failure modes (blur, darkness, occlusion)
- Measure performance degradation quantitatively
- Create publication-quality visualizations

For questions or customization, refer to individual script headers and inline documentation.
