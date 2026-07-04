import requests
import os
from datetime import datetime, timedelta
from django.utils import timezone


def send_telegram_alert(confidence, screenshot_path=None, detection_type='live'):
    """Send violence alert to Telegram with optional screenshot."""
    try:
        from .models import TelegramSettings, SystemSettings

        settings_obj = SystemSettings.objects.first()
        if not settings_obj or not settings_obj.telegram_alerts:
            return False

        tg = TelegramSettings.objects.first()
        if not tg or not tg.enabled or not tg.bot_token or not tg.chat_id:
            return False

        # Check cooldown
        if tg.last_alert_sent:
            cooldown = timedelta(seconds=tg.alert_cooldown_seconds)
            if timezone.now() - tg.last_alert_sent < cooldown:
                print(f"[Telegram] Cooldown active, skipping alert")
                return False

        token    = tg.bot_token
        chat_id  = tg.chat_id
        emoji    = "🚨"
        src      = "Live Camera" if detection_type == 'live' else "Video Upload"
        now_str  = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        message = (
            f"{emoji} *VIOLENCE DETECTED*\n\n"
            f"📍 Source: {src}\n"
            f"📊 Confidence: `{confidence:.4f}`\n"
            f"⏰ Time: `{now_str}`\n\n"
            f"⚠️ Immediate attention required!"
        )

        # Send photo if screenshot exists
        if screenshot_path and os.path.exists(screenshot_path):
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            with open(screenshot_path, 'rb') as photo:
                resp = requests.post(url, data={
                    'chat_id': chat_id,
                    'caption': message,
                    'parse_mode': 'Markdown',
                }, files={'photo': photo}, timeout=10)
        else:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            resp = requests.post(url, json={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown',
            }, timeout=10)

        if resp.status_code == 200:
            tg.last_alert_sent = timezone.now()
            tg.save()
            print(f"[Telegram] Alert sent successfully")
            return True
        else:
            print(f"[Telegram] Failed: {resp.text}")
            return False

    except Exception as e:
        print(f"[Telegram] Error: {e}")
        return False


def test_telegram_connection(bot_token, chat_id):
    """Test if bot token and chat ID are valid."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(url, json={
            'chat_id': chat_id,
            'text': '✅ VisionGuard AI connected successfully! You will receive violence detection alerts here.',
        }, timeout=10)
        return resp.status_code == 200, resp.json()
    except Exception as e:
        return False, str(e)
