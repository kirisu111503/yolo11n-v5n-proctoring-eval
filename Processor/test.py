import cv2
import os
from ultralytics import YOLO

# --- CONFIGURATION ---
# Path to your custom weights
MODEL_PATH = './yolov11_training_results/weights/best.pt'

# Change this to your test source (can be a folder path, image path, or 0 for webcam)
SOURCE = 'test/images'  # Use '0' for live webcam, or 'path/to/your/test_images/'

# Confidence threshold (0.25 means it ignores detections with < 25% certainty)
CONF_THRESHOLD = 0.5 

def run_test():
    # 1. Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        return

    # 2. Load the trained YOLOv11 model
    print(f"Loading model: {MODEL_PATH}...")
    model = YOLO(MODEL_PATH)

    # 3. Run Inference
    # save=True: saves result images to 'runs/detect/predict'
    # show=True: opens a window to show results in real-time
    # stream=True: more memory efficient for videos/webcams
    print(f"Starting inference on source: {SOURCE}...")
    results = model.predict(
        source=SOURCE,
        conf=CONF_THRESHOLD,
        save=True,
        show=True, 
        stream=True 
    )

    # 4. Process results (Optional: prints detected classes to terminal)
    for r in results:
        # r.boxes contains the bounding boxes
        if len(r.boxes) > 0:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                conf = float(box.conf[0])
                print(f"Detected: {label} ({conf:.2f})")

if __name__ == "__main__":
    run_test()