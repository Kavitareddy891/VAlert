# VisionGuard AI — Violence Detection Django App

## Project Structure

```
violence_detection/
├── api/
│   └── modelnew.h5          ← Place your trained model here
├── detection/
│   ├── templates/detection/ ← HTML pages
│   ├── ml_utils.py          ← Model loading & inference
│   ├── views.py             ← Django views + API endpoints
│   └── urls.py
├── violence_detection/
│   └── settings.py
├── media/uploads/           ← Temp video uploads (auto-created)
├── requirements.txt
└── manage.py
```

## Setup Instructions

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Place your model
Copy your trained model file to:
```
violence_detection/api/modelnew.h5
```

### 3. Run migrations
```bash
python manage.py migrate
```

### 4. Start the server
```bash
python manage.py runserver
```

### 5. Open in browser
- Dashboard:     http://127.0.0.1:8000/
- Live Camera:   http://127.0.0.1:8000/live/
- Upload Video:  http://127.0.0.1:8000/upload/

---

## Configuration (settings.py)

| Setting | Default | Description |
|---------|---------|-------------|
| `MODEL_PATH` | `api/modelnew.h5` | Path to your .h5 model |
| `IMG_SIZE` | `128` | Input image size for the model |
| `THRESHOLD` | `0.3` | Confidence threshold for violence detection |

---

## API Endpoints

### POST `/api/predict-frame/`
Send a base64-encoded image, get a prediction.

**Request body:**
```json
{ "image": "data:image/jpeg;base64,..." }
```

**Response:**
```json
{
  "confidence": 0.7432,
  "label": "VIOLENCE DETECTED",
  "is_violence": true,
  "threshold": 0.3
}
```

---

### POST `/api/analyze-video/`
Upload a video file for full analysis.

**Form data:** `video` (file)

**Response:**
```json
{
  "overall_label": "VIOLENCE DETECTED",
  "violence_percentage": 45.2,
  "violence_count": 12,
  "total_analyzed": 27,
  "max_confidence": 0.9821,
  "avg_confidence": 0.5412,
  "duration": 30.5,
  "fps": 30.0,
  "frame_results": [...]
}
```

---

## Notes

- The model is loaded **once** at first request and cached in memory.
- Uploaded videos are automatically deleted after analysis.
- Live camera sends frames to the server every 500ms for prediction.
- Use `opencv-python-headless` (not `opencv-python`) for server environments.
