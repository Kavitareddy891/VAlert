import numpy as np
import cv2
import os
import base64
from datetime import datetime

_model = None

def get_model():
    global _model
    if _model is None:
        from django.conf import settings
        from tensorflow.keras.models import load_model
        model_path = str(settings.MODEL_PATH)
        if os.path.exists(model_path):
            print(f"[ViolenceDetector] Loading model from {model_path}...")
            _model = load_model(model_path, compile=False)
            print(f"[ViolenceDetector] Model loaded. Output shape: {_model.output_shape}")
        else:
            raise FileNotFoundError(f"Model not found at: {model_path}")
    return _model


def get_threshold():
    try:
        from .models import SystemSettings
        s = SystemSettings.objects.first()
        if s:
            return s.threshold
    except:
        pass
    from django.conf import settings
    return settings.THRESHOLD


def save_screenshot(frame):
    """Save a frame as screenshot and return the relative path."""
    try:
        from django.conf import settings
        screenshot_dir = os.path.join(str(settings.MEDIA_ROOT), 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)
        filename = f"violence_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
        filepath = os.path.join(screenshot_dir, filename)
        cv2.imwrite(filepath, frame)
        return f"screenshots/{filename}", filepath
    except Exception as e:
        print(f"[save_screenshot] Error: {e}")
        return None, None


def predict_frame(frame, img_size=128):
    """Exact same preprocessing as original live_detection.py."""
    model = get_model()
    img = cv2.resize(frame, (img_size, img_size))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)
    prediction = model.predict(img, verbose=0)[0][0]
    confidence = float(prediction)
    print(f"[predict_frame] confidence={confidence:.4f}")
    return confidence


def log_detection_event(user, detection_type, confidence, frame=None,
                         video_filename=None, violence_percentage=None,
                         total_frames=None, violence_frames=None):
    """Save detection event to DB, take screenshot, send Telegram alert."""
    try:
        from .models import DetectionEvent, SystemSettings
        from .telegram_utils import send_telegram_alert

        threshold   = get_threshold()
        is_violence = confidence > threshold
        status      = 'violence' if is_violence else 'safe'

        sys_settings = SystemSettings.objects.first()
        auto_screenshot = sys_settings.auto_screenshot if sys_settings else True

        screenshot_rel  = None
        screenshot_full = None

        # Auto screenshot on violence
        if is_violence and frame is not None and auto_screenshot:
            screenshot_rel, screenshot_full = save_screenshot(frame)

        event = DetectionEvent(
            user=user,
            detection_type=detection_type,
            status=status,
            confidence=confidence,
            video_filename=video_filename,
            violence_percentage=violence_percentage,
            total_frames=total_frames,
            violence_frames=violence_frames,
        )
        if screenshot_rel:
            event.screenshot = screenshot_rel
        event.save()

        # Telegram alert
        if is_violence:
            sent = send_telegram_alert(confidence, screenshot_full, detection_type)
            if sent:
                event.telegram_sent = True
                event.save()

        return event
    except Exception as e:
        print(f"[log_detection_event] Error: {e}")
        return None


def analyze_video(video_path, img_size=128, sample_interval=15, user=None):
    threshold = get_threshold()

    print(f"[analyze_video] Opening: {video_path}")
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"[analyze_video] FPS={fps}, Total frames={total_frames}")

    if not fps or fps <= 0:
        fps = 25.0

    duration = total_frames / fps if total_frames > 0 else 0
    frame_results = []
    frame_number  = 0
    violence_count = 0
    read_errors   = 0
    peak_frame    = None
    peak_conf     = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            read_errors += 1
            if read_errors > 10:
                break
            continue
        read_errors = 0

        if frame_number % sample_interval == 0:
            try:
                img = cv2.resize(frame, (img_size, img_size))
                img_arr = img.astype("float32") / 255.0
                img_arr = np.expand_dims(img_arr, axis=0)
                prediction = get_model().predict(img_arr, verbose=0)[0][0]
                confidence = float(prediction)
                is_violence = confidence > threshold

                if is_violence:
                    violence_count += 1
                    if confidence > peak_conf:
                        peak_conf  = confidence
                        peak_frame = frame.copy()

                frame_results.append({
                    'frame_number': frame_number,
                    'timestamp': round(frame_number / fps, 2),
                    'confidence': round(confidence, 4),
                    'label': 'VIOLENCE' if is_violence else 'SAFE',
                })
                print(f"[analyze_video] Frame {frame_number}: {confidence:.4f} -> {'VIOLENCE' if is_violence else 'SAFE'}")
            except Exception as e:
                print(f"[analyze_video] Error on frame {frame_number}: {e}")

        frame_number += 1
        if frame_number > 100000:
            break

    cap.release()

    total_analyzed = len(frame_results)
    if total_analyzed == 0:
        return {
            'frame_results': [], 'violence_count': 0, 'total_analyzed': 0,
            'max_confidence': 0, 'avg_confidence': 0, 'violence_percentage': 0,
            'overall_label': 'UNKNOWN - No frames could be analyzed',
            'duration': round(duration, 2), 'fps': round(fps, 2),
        }

    confidences        = [r['confidence'] for r in frame_results]
    violence_percentage = (violence_count / total_analyzed) * 100
    overall_label      = 'VIOLENCE DETECTED' if violence_percentage >= 30 else 'NO VIOLENCE'
    max_conf           = round(max(confidences), 4)

    # Log to DB
    video_filename = os.path.basename(video_path)
    log_detection_event(
        user=user,
        detection_type='video',
        confidence=max_conf,
        frame=peak_frame,
        video_filename=video_filename,
        violence_percentage=round(violence_percentage, 2),
        total_frames=total_analyzed,
        violence_frames=violence_count,
    )

    return {
        'frame_results': frame_results,
        'violence_count': violence_count,
        'total_analyzed': total_analyzed,
        'max_confidence': max_conf,
        'avg_confidence': round(sum(confidences) / total_analyzed, 4),
        'violence_percentage': round(violence_percentage, 2),
        'overall_label': overall_label,
        'duration': round(duration, 2),
        'fps': round(fps, 2),
    }
