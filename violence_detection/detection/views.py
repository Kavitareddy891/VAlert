import json, base64, numpy as np, cv2, os, uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta


# ─── AUTH ────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'index'))
        error = 'Invalid username or password'
    return render(request, 'detection/auth/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    error = None
    if request.method == 'POST':
        username  = request.POST.get('username')
        password  = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            error = 'Passwords do not match'
        elif User.objects.filter(username=username).exists():
            error = 'Username already taken'
        else:
            User.objects.create_user(username=username, password=password)
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('index')
    return render(request, 'detection/auth/register.html', {'error': error})


# ─── MAIN PAGES ─────────────────────────────────────────────────

@login_required
def index(request):
    from .models import DetectionEvent
    from django.db.models.functions import TruncDate
    recent = DetectionEvent.objects.filter(user=request.user).order_by('-timestamp')[:5]
    total  = DetectionEvent.objects.filter(user=request.user).count()
    violence_total = DetectionEvent.objects.filter(user=request.user, status='violence').count()
    safe_total = DetectionEvent.objects.filter(user=request.user, status='safe').count()
    return render(request, 'detection/index.html', {
        'recent': recent,
        'total': total,
        'violence_total': violence_total,
        'safe_total': safe_total,
    })


@login_required
def live_view(request):
    return render(request, 'detection/live.html')


@login_required
def upload_view(request):
    return render(request, 'detection/upload.html')


@login_required
def dashboard_view(request):
    from .models import DetectionEvent
    from django.db.models.functions import TruncDate

    user_events = DetectionEvent.objects.filter(user=request.user)

    total        = user_events.count()
    violence_cnt = user_events.filter(status='violence').count()
    safe_cnt     = user_events.filter(status='safe').count()
    avg_conf     = user_events.aggregate(a=Avg('confidence'))['a'] or 0
    last_7_days  = user_events.filter(timestamp__gte=timezone.now() - timedelta(days=7))

    # Daily counts for chart (last 7 days)
    daily = []
    for i in range(6, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        v = user_events.filter(timestamp__date=day, status='violence').count()
        s = user_events.filter(timestamp__date=day, status='safe').count()
        daily.append({'date': str(day), 'violence': v, 'safe': s})

    recent_events = user_events.order_by('-timestamp')[:20]
    screenshots   = user_events.filter(status='violence').exclude(screenshot='').order_by('-timestamp')[:12]

    return render(request, 'detection/dashboard.html', {
        'total': total,
        'violence_cnt': violence_cnt,
        'safe_cnt': safe_cnt,
        'avg_conf': round(avg_conf, 4),
        'daily_json': json.dumps(daily),
        'recent_events': recent_events,
        'screenshots': screenshots,
        'violence_rate': round((violence_cnt / total * 100) if total else 0, 1),
    })


@login_required
def history_view(request):
    from .models import DetectionEvent
    events = DetectionEvent.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'detection/history.html', {'events': events})


@login_required
def settings_view(request):
    from .models import TelegramSettings, SystemSettings
    from .telegram_utils import test_telegram_connection

    tg  = TelegramSettings.objects.first() or TelegramSettings()
    sys = SystemSettings.objects.first() or SystemSettings()
    msg = None
    msg_type = 'success'

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_system':
            sys.threshold       = float(request.POST.get('threshold', 0.3))
            sys.auto_screenshot = request.POST.get('auto_screenshot') == 'on'
            sys.telegram_alerts = request.POST.get('telegram_alerts') == 'on'
            sys.save()
            msg = 'System settings saved.'

        elif action == 'save_telegram':
            tg.bot_token              = request.POST.get('bot_token', '').strip()
            tg.chat_id                = request.POST.get('chat_id', '').strip()
            tg.alert_cooldown_seconds = int(request.POST.get('cooldown', 60))
            tg.enabled                = request.POST.get('enabled') == 'on'
            tg.save()
            msg = 'Telegram settings saved.'

        elif action == 'test_telegram':
            tg.bot_token = request.POST.get('bot_token', '').strip()
            tg.chat_id   = request.POST.get('chat_id', '').strip()
            tg.save()
            ok, result = test_telegram_connection(tg.bot_token, tg.chat_id)
            msg = 'Telegram test message sent successfully!' if ok else f'Failed: {result}'
            msg_type = 'success' if ok else 'error'

    # Reload after save
    tg  = TelegramSettings.objects.first() or TelegramSettings()
    sys = SystemSettings.objects.first() or SystemSettings()
    return render(request, 'detection/settings.html', {
        'tg': tg, 'sys': sys, 'msg': msg, 'msg_type': msg_type,
    })


# ─── API ────────────────────────────────────────────────────────

@csrf_exempt
@login_required
def predict_frame_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data       = json.loads(request.body)
        image_data = data.get('image', '')
        if ',' in image_data:
            image_data = image_data.split(',')[1]

        img_bytes = base64.b64decode(image_data)
        np_arr    = np.frombuffer(img_bytes, np.uint8)
        frame     = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return JsonResponse({'error': 'Invalid image data'}, status=400)

        from .ml_utils import predict_frame, log_detection_event, get_threshold
        confidence  = predict_frame(frame, settings.IMG_SIZE)
        threshold   = get_threshold()
        is_violence = confidence > threshold

        # Only log violence events from live feed (avoid DB flood)
        if is_violence:
            log_detection_event(
                user=request.user,
                detection_type='live',
                confidence=confidence,
                frame=frame,
            )

        return JsonResponse({
            'confidence': round(confidence, 4),
            'label': 'VIOLENCE DETECTED' if is_violence else 'NO VIOLENCE',
            'is_violence': is_violence,
            'threshold': threshold,
        })
    except Exception as e:
        import traceback; print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def analyze_video_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    video_file = request.FILES.get('video')
    if not video_file:
        return JsonResponse({'error': 'No video file provided'}, status=400)

    upload_dir = os.path.join(str(settings.MEDIA_ROOT), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    ext        = os.path.splitext(video_file.name)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    video_path  = os.path.join(upload_dir, unique_name)

    with open(video_path, 'wb+') as f:
        for chunk in video_file.chunks():
            f.write(chunk)

    try:
        from .ml_utils import analyze_video
        results = analyze_video(video_path, settings.IMG_SIZE, user=request.user)
        results['filename'] = video_file.name
        return JsonResponse(results)
    except Exception as e:
        import traceback; print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


@login_required
def stats_api(request):
    from .models import DetectionEvent
    from django.db.models.functions import TruncDate
    events = DetectionEvent.objects.filter(user=request.user)
    daily  = []
    for i in range(6, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        v = events.filter(timestamp__date=day, status='violence').count()
        s = events.filter(timestamp__date=day, status='safe').count()
        daily.append({'date': str(day), 'violence': v, 'safe': s})
    return JsonResponse({'daily': daily})
