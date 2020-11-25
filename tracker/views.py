from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, get_list_or_404

from tracker.models import Tracker, Record
from tracker.forms import RecordForm, TrackerForm


def index(request):
    trackers = Tracker.objects.all()
    return render(request, "index.html", {"trackers": trackers})


def record_detail(request):
    if request.method == "POST":
        form = RecordForm(request.POST)
        if form.is_valid():
            return HttpResponse("Form submittion succesful.")
    else:
        return HttpResponse("Record detail view, will probably not implement.")


def tracker_detail(request, id=None):
    if id:
        tracker = get_object_or_404(Tracker, id=id)
        form = TrackerForm(request.POST, instance=tracker)
    else:
        form = TrackerForm(request.POST)
        tracker = None

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))

    return render(
        request, "tracker/tracker_detail.html", {"form": form, "tracker": tracker}
    )

def tracker_delete(request, id):
    pass