from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, get_list_or_404

from tracker.models import Tracker, Record
from tracker.forms import RecordForm, TrackerForm


def index(request):
    trackers = Tracker.objects.all()
    return render(request, "index.html", {"trackers": trackers})


def record_detail(request):
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            return HttpResponse("Form submittion succesful.")
    else:
        return HttpResponse("Record detail view, will probably not implement.")


def tracker_detail(request, id=None):
    if request.method == 'POST':
        form = TrackerForm(request.POST)
        if form.is_valid():
            tracker = Tracker(form.cleaned_data)
            tracker.save()
            return HttpResponse("Form submittion succesful.")
        return render(request, "tracker/tracker_detail.html", {'form': form})

    else:
        if id:
            tracker = get_object_or_404(Tracker, id=id)
        else:
            tracker = Tracker()

        form = TrackerForm(instance=tracker)
        return render(request, "tracker/tracker_detail.html", {'form': form})


def tracker_list(request):
    trackers = Tracker.objects.all()
    return render(request, "tracker/tracker_list.html", {"trackers": trackers})
