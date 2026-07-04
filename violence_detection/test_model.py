"""
Run this directly to diagnose the model and video reading issue.
Place this file in: D:\violence_detection_project\violence_detection\
Then run: python test_model.py
"""

import cv2
import numpy as np
import os
import sys

# ── 1. CHECK MODEL ──────────────────────────────────────────────
MODEL_PATH = r"api\modelnew.h5"

print("=" * 60)
print("STEP 1: Loading model...")
print(f"  Path: {os.path.abspath(MODEL_PATH)}")
print(f"  Exists: {os.path.exists(MODEL_PATH)}")

if not os.path.exists(MODEL_PATH):
    print("\n  ERROR: Model file not found!")
    print("  Make sure modelnew.h5 is at: api\\modelnew.h5")
    sys.exit(1)

from tensorflow.keras.models import load_model
model = load_model(MODEL_PATH, compile=False)
print(f"  Output shape : {model.output_shape}")
print(f"  Input shape  : {model.input_shape}")
print("  Model loaded OK")

# ── 2. TEST WITH BLANK FRAME ─────────────────────────────────────
print("\nSTEP 2: Test prediction on blank frame...")
blank = np.zeros((128, 128, 3), dtype="float32")
blank = np.expand_dims(blank, axis=0)
raw = model.predict(blank, verbose=0)
print(f"  Raw output on blank frame: {raw}")
print(f"  [0][0] value: {raw[0][0]:.6f}")

# ── 3. TEST WITH RANDOM FRAME ────────────────────────────────────
print("\nSTEP 3: Test prediction on random noise frame...")
noise = np.random.rand(1, 128, 128, 3).astype("float32")
raw2 = model.predict(noise, verbose=0)
print(f"  Raw output on noise frame: {raw2}")
print(f"  [0][0] value: {raw2[0][0]:.6f}")

# ── 4. TEST VIDEO READING ────────────────────────────────────────
print("\nSTEP 4: Video reading test...")
print("  Enter path to your test video (e.g. fight.mp4):")
video_path = input("  > ").strip().strip('"')

if not os.path.exists(video_path):
    print(f"  ERROR: File not found: {video_path}")
    sys.exit(1)

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("  ERROR: OpenCV cannot open this video file!")
    print("  Try installing: pip install opencv-python")
    sys.exit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"  FPS={fps}, Total frames={total}")

# Read first 5 frames and predict
print("\n  Reading first 5 frames and predicting:")
for i in range(5):
    ret, frame = cap.read()
    if not ret:
        print(f"  Frame {i}: FAILED TO READ")
        continue

    img = cv2.resize(frame, (128, 128))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)
    raw = model.predict(img, verbose=0)
    conf = float(raw[0][0])
    label = "VIOLENCE" if conf > 0.3 else "SAFE"
    print(f"  Frame {i}: raw={raw[0][0]:.6f}  label={label}")

cap.release()

# ── 5. SUMMARY ───────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("  If all frames show confidence ~0.0 → model output is inverted")
print("  If all frames show confidence ~0.5 → preprocessing mismatch")  
print("  If frames show varied values      → model is working correctly")
print("=" * 60)
