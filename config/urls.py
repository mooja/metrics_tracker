import importlib

from pathlib import Path

from django.urls import path, include
from django.conf import settings

from metrics_tracker.tracker import views


urlpatterns = [
    path("", views.index, name="home"),
    path("plots/week/", views.week_plot, name="week_plot"),
    path("plots/four_weeks/", views.four_week_plot, name="four_week_plot"),
    path("session/<int:tracker_id>/", views.session_detail, name="session_detail"),
    path("session/settings/<int:tracker_id>/", views.session_settings_detail, name="session_settings_detail"),
    path("trackers/", views.tracker_detail, name="tracker_detail"),
    path("trackers/<int:id>/", views.tracker_detail, name="tracker_detail"),
    path("trackers/<int:id>/delete/", views.tracker_delete, name="tracker_delete"),
    path("trackers/<int:tracker_id>/records/", views.record_detail, name="record_detail"),
    path("trackers/<int:tracker_id>/records/<int:record_id>", views.record_detail, name="record_detail"),
]
