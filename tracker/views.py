import datetime

from itertools import cycle

from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, get_list_or_404

from tracker.models import Tracker, Record
from tracker.forms import RecordForm, TrackerForm


def index(request):
    trackers = Tracker.objects.all()
    forms = (RecordForm(initial={"tracker_id": t.id}) for t in Tracker.objects.all())
    colors = cycle(('blue', 'green', 'red', 'purple'))
    trackers_and_forms_and_colors = zip(trackers, forms, colors)

    context = {"trackers": trackers, "trackers_and_forms_and_colors": trackers_and_forms_and_colors}
    return render(request, "index.html", context)


@require_POST
def record_detail(request, id):
    tracker = get_object_or_404(Tracker, id=id)
    record = Record(date=datetime.date.today(), tracker=tracker)
    form = RecordForm(request.POST, instance=record)
    if form.is_valid():
        form.save()
        return redirect("home")
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
            return redirect("home")

    return render(
        request, "tracker/tracker_detail.html", {"form": form, "tracker": tracker}
    )


@require_POST
def tracker_delete(request, id):
    tracker = get_object_or_404(Tracker, id=id)
    tracker.delete()
    return redirect("home")