"""metrics_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from tracker import views

urlpatterns = [
    path("", views.index, name="home"),
    path("plots/week/", views.week_plot, name="week_plot"),
    path("trackers/", views.tracker_detail, name="tracker_detail"),
    path("trackers/<int:id>/", views.tracker_detail, name="tracker_detail"),
    path("trackers/<int:id>/delete/", views.tracker_delete, name="tracker_delete"),
    path("trackers/<int:tracker_id>/records/", views.record_detail, name="record_detail"),
    path("trackers/<int:tracker_id>/records/<int:record_id>", views.record_detail, name="record_detail"),
]
