import datetime

from itertools import cycle

from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib import messages

from tracker.models import Tracker, Record
from tracker.forms import RecordForm, TrackerForm


def index(request):
    trackers = Tracker.objects.all()  # pylint:disable=no-member
    forms = (RecordForm(tracker=t, initial={"tracker_id": t.id }) for t in Tracker.objects.all())  # pylint:disable=no-member
    colors = cycle(('blue', 'green', 'red', 'purple'))
    trackers_and_forms_and_colors = zip(trackers, forms, colors)

    context = {"trackers": trackers, "trackers_and_forms_and_colors": trackers_and_forms_and_colors}
    return render(request, "index.html", context)


def tracker_detail(request, id=None, delete=False):
    if request.method == "POST":
        form = TrackerForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["action"] == "add":
                form.save()
                messages.success(request, "Tracker created.")
                return redirect("tracker_detail", form.instance.id)

            elif form.cleaned_data["action"] == "update":
                tracker = get_object_or_404(Tracker, id=id)
                form = TrackerForm(request.POST, instance=tracker)
                form.is_valid()
                form.save()
                messages.success(request, "Tracker updated.")
                return redirect("tracker_detail", form.instance.id)

            elif form.cleaned_data["action"] == "delete":
                tracker = get_object_or_404(Tracker, id=id)
                tracker.delete()
                messages.success(request, "Tracker deleted.")
                return redirect("home")
            
            else:
                return HttpResponse(f"Action {form.cleaned_data['action']} is not implemented.")
    

    tracker = get_object_or_404(Tracker, id=id) if id else Tracker()
    context = {}
    context["form"] = TrackerForm(instance=tracker) if id else TrackerForm()

    if id:
        context["record_form"] = RecordForm(tracker=tracker)
        context["record_forms"] = (
            RecordForm(tracker=tracker, instance=r)
            for r in Record.objects.all().filter(tracker_id=id)  # pylint: disable=no-member
        )

    return render(request, "tracker/tracker_detail.html", context)


@require_POST
def record_detail(request, tracker_id, record_id=None):
    tracker = get_object_or_404(Tracker, id=tracker_id)
    form = RecordForm(request.POST, tracker=tracker)

    if not form.is_valid():
        messages.error(request, "Error in form submission.")
        return tracker_detail(request, id=tracker_id)
    
    if form.cleaned_data["action"] == "add":
        record = Record(date=datetime.date.today(), tracker=tracker)
        form = RecordForm(request.POST, tracker=tracker, instance=record)
        form.is_valid()
        form.save()
        messages.success(request, "Added a new record.")
        return redirect("tracker_detail", tracker.id)
    
    if form.cleaned_data["action"] == "update":
        record = get_object_or_404(Record, id=record_id)
        form = RecordForm(request.POST, tracker=tracker, instance=record)
        form.is_valid()
        form.save()
        messages.success(request, "Updated record.")
        return redirect("tracker_detail", tracker.id)

    if form.cleaned_data["action"] == "delete":
        record = get_object_or_404(Record, id=record_id)
        form = RecordForm(request.POST, tracker=tracker, instance=record)
        form.is_valid()
        record.delete()
        messages.success(request, "Deleted record.")
        return redirect("tracker_detail", tracker.id)

    return HttpResponse("Not implemented.")


@require_POST
def tracker_delete(request, id):
    tracker = get_object_or_404(Tracker, id=id)
    tracker.delete()
    return redirect("home")