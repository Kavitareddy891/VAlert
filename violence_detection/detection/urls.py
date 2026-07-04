from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('register/', views.register_view, name='register'),

    # Main pages
    path('',          views.index,         name='index'),
    path('live/',     views.live_view,     name='live'),
    path('upload/',   views.upload_view,   name='upload'),
    path('dashboard/',views.dashboard_view,name='dashboard'),
    path('history/',  views.history_view,  name='history'),
    path('settings/', views.settings_view, name='settings'),

    # API
    path('api/predict-frame/',  views.predict_frame_api,  name='predict_frame'),
    path('api/analyze-video/',  views.analyze_video_api,  name='analyze_video'),
    path('api/stats/',          views.stats_api,          name='stats_api'),
]
