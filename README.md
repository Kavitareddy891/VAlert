# 🛡️ V-Alert: AI-Powered Violence Detection and Alert System

An intelligent web application built using **Django**, **TensorFlow**, and **OpenCV** that detects violence in live camera feeds and uploaded videos using deep learning. When violence is detected, the system automatically captures a screenshot, stores detection details, and can send Telegram alerts.

---

## 📌 Features

- 🎥 Live Camera Violence Detection
- 📁 Upload Video for Analysis
- 🤖 AI-based Violence Detection using TensorFlow
- 📸 Automatic Screenshot Capture
- 📊 Detection History Dashboard
- ⚙️ Adjustable Detection Threshold
- 🔔 Telegram Alert Integration
- 👤 User Authentication (Login & Registration)
- 📈 Statistics Dashboard

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap

### Backend
- Python
- Django

### AI & Computer Vision
- TensorFlow
- Keras
- OpenCV
- NumPy

### Database
- SQLite (Development)

### Deployment
- Render
- GitHub

---

## 📂 Project Structure

```
visionguard_v2/
│
├── violence_detection/
│   ├── detection/
│   ├── media/
│   ├── static/
│   ├── templates/
│   ├── violence_detection/
│   ├── manage.py
│   ├── requirements.txt
│   └── modelnew.h5
│
└── README.md
```

---

## 🚀 Installation

### Clone the Repository

```bash
git clone https://github.com/Kavitareddy891/VAlert.git
cd VAlert/violence_detection
```

### Create Virtual Environment

```bash
python -m venv .envi
```

### Activate Environment

Windows

```bash
.envi\Scripts\activate
```

Linux/Mac

```bash
source .envi/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Migrations

```bash
python manage.py migrate
```

### Start the Server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

## 🧠 Machine Learning Model

The project uses a pretrained TensorFlow model:

```
modelnew.h5
```

Model Configuration:

- Image Size: 128 × 128
- Confidence Threshold: 0.30
- Framework: TensorFlow / Keras

---

## 🔔 Alert System

When violence is detected:

- Screenshot is captured
- Detection record is saved
- Telegram notification is sent (if configured)

---

## ⚙️ Configuration

Update the following in `settings.py`:

```python
MODEL_PATH = BASE_DIR / "modelnew.h5"
```

For production, configure:

- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- Telegram Bot Token
- Telegram Chat ID

---

## 📊 Future Enhancements

- Face Recognition
- Weapon Detection
- Multi-Camera Support
- Cloud Storage
- PostgreSQL Database
- Docker Deployment

---

## 👩‍💻 Developed By

**Kavita Reddy**

Master of Computer Applications (MCA)

Hyderabad, India

GitHub:
https://github.com/Kavitareddy891

---

## 📜 License

This project is developed for educational and research purposes.

---

## ⭐ Support

If you found this project helpful, please consider giving it a ⭐ on GitHub.
