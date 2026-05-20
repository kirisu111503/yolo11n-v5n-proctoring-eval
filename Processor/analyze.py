from ultralytics import YOLO
import os

# CONFIGURATION
MODEL_PATH = './yolov11_training_results/weights/best.pt'
DATA_YAML = './dataset.yaml' # Ensure this points to your local test images/labels

def analyze_model():
    # 1. Load the model
    model = YOLO(MODEL_PATH)

    # 2. Run Validation on the TEST split
    # split='test' tells YOLO to use the 'test' path from your YAML
    # save_json=True saves a detailed result file for further coding
    # plots=True generates Confusion Matrix, F1-curve, etc.
    print("Running analytical evaluation on test set...")
    metrics = model.val(
        data=DATA_YAML,
        split='test',  
        imgsz=640,
        batch=16,
        conf=0.25,     # Confidence threshold
        iou=0.6,       # NMS IoU threshold
        save_json=True,
        plots=True     # Generate visual analysis charts
    )

    # 3. Print out the results for analysis
    print("\n--- TEST SET ANALYSIS ---")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"mAP50:    {metrics.box.map50:.4f}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall:    {metrics.box.mr:.4f}")
    
    print(f"\nResults and charts saved to: {model.predictor.save_dir}")

if __name__ == "__main__":
    analyze_model()