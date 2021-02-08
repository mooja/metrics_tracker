import datetime
import base64
import warnings

from io import BytesIO

from datetime import timezone, timedelta

from itertools import cycle
from collections import defaultdict

from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.utils import timezone

import numpy as np
from matplotlib.figure import Figure

from .models import Tracker, Record, Session
from .forms import RecordForm, TrackerForm, SessionControlsForm, SessionSettingsForm


def index(request):
    trackers = Tracker.objects.all()  # pylint:disable=no-member
    for t in trackers:
        try:
            t.session
        except ObjectDoesNotExist:
            s = Session(tracker=t)
            s.save()
        if t.session.is_finished():
            t.session.finish()
        today = timezone.now().date()
        last_session_update_day = t.session.session_count_update_timestamp.date()
        if last_session_update_day != today:
            t.session.reset_daily_count()

    sessions_json = serializers.serialize('json', Session.objects.all())  # pylint:disable=no-member
    session_forms = (SessionControlsForm(instance=t.session) for t in trackers)
    forms = (
        RecordForm(
            initial={"tracker": t.id}, fh_data={"tracker_id": t.id, "index_view": True}
        )
        for t in Tracker.objects.all()  #pylint:disable=no-member
    )
    colors = cycle(("blue", "green", "red", "purple"))
    trackers_and_forms_and_colors = zip(trackers, forms, colors, session_forms)
    context = {
        "trackers": trackers,
        "trackers_and_forms_and_colors": trackers_and_forms_and_colors,
        "sessions_json": sessions_json
    }
    return render(request, "index.html", context)


def session_detail(request, tracker_id):
    tracker = get_object_or_404(Tracker, id=tracker_id)
    if request.method == 'POST':
        session_form = SessionControlsForm(request.POST, instance=tracker.session)
        if session_form.is_valid():
            session = session_form.save(commit=False)
            if session_form.cleaned_data['action'] == "start":
                session.begin()
            elif session_form.cleaned_data['action'] == "pause":
                session.pause()
            elif session_form.cleaned_data['action'] == "resume":
                session.resume()
            elif session_form.cleaned_data['action'] == "stop":
                session.finish()
            elif session_form.cleaned_data['action'] == "log":
                session.save_as_record()
                cache.delete("week_plot")
                cache.delete("four_week_plot")
            elif session_form.cleaned_data['action'] == "reset":
                session.reset()
            else:
                raise Exception(f"uknown action: {session_form.cleaned_data['action']}")
            return redirect("home")
        return HttpResponse("session form data is not valid: " + str(session_form.errors) )
    return HttpResponse("get not implemented")

    # pomodoro_session = (Session.objects.all().filter(status=='active')  # pylint:disable=no-member


def tracker_detail(request, id=None, delete=False):
    if request.method == "POST":
        form = TrackerForm(request.POST)
        if form.is_valid():
            cache.delete("week_plot")
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
                return HttpResponse(
                    f"Action {form.cleaned_data['action']} is not implemented."
                )

    context = {}
    if not id:
        context["form"] = TrackerForm()
    else:
        tracker = get_object_or_404(Tracker, id=id)
        context["tracker"] = tracker
        context["form"] = TrackerForm(instance=tracker)
        context["record_form"] = RecordForm(
            initial={"tracker": tracker.id},
            fh_data={"index_view": False, "tracker_id": id},
        )
        context["record_forms"] = (
            RecordForm(
                instance=r,
                fh_data={"index_view": False, "tracker_id": id, "record_id": r.id},
            )
            for r in Record.objects.all()  # pylint: disable=no-member
            .filter(tracker__id=id)
            .order_by("-date") 
        )
        context["session_settings_form"] = SessionSettingsForm(instance=tracker.session)

    return render(request, "tracker/tracker_detail.html", context)


@require_POST
def record_detail(request, tracker_id, record_id=None):
    tracker = get_object_or_404(Tracker, id=tracker_id)
    fh_data = {"tracker_id": tracker.id, "record_id": record_id}
    if record_id:
        record = get_object_or_404(Record, id=record_id)
        form = RecordForm(request.POST, instance=record, fh_data=fh_data)
    else:
        record = Record(tracker=tracker)
        form = RecordForm(request.POST, instance=record, fh_data=fh_data)

    if not form.is_valid():
        messages.error(request, f"Error in form submission: {form.errors}")
        return tracker_detail(request, id=tracker_id)

    cache.delete("week_plot")
    cache.delete("four_week_plot")

    if form.cleaned_data["action"] == "add":
        record = Record(date=datetime.date.today(), tracker=tracker)
        form = RecordForm(request.POST, instance=record, fh_data=fh_data)
        form.is_valid()
        form.save()
        messages.success(request, "Added a new record.")
        return redirect("home")

    if form.cleaned_data["action"] == "update":
        record = get_object_or_404(Record, id=record_id)
        form = RecordForm(request.POST, instance=record, fh_data=fh_data)
        form.is_valid()
        form.save()
        messages.success(request, "Updated record.")
        return redirect(reverse("tracker_detail", kwargs={"id": tracker.id}))

    if form.cleaned_data["action"] == "delete":
        record = get_object_or_404(Record, id=record_id)
        form = RecordForm(request.POST, instance=record, fh_data=fh_data)
        form.is_valid()
        record.delete()
        messages.success(request, "Deleted record.")
        return redirect(reverse("tracker_detail", kwargs={"id": tracker.id}))

    return HttpResponse("Not implemented.")


@require_POST
def tracker_delete(request, id):
    tracker = get_object_or_404(Tracker, id=id)
    tracker.delete()
    return redirect("home")


def dates_this_week():
    monday = datetime.date.today()
    while monday.isoweekday() != 1:
        monday = monday - datetime.timedelta(days=1)
    dates = [monday + datetime.timedelta(days=i) for i in range(7)]
    dates.sort()
    return dates


def week_plot(request):
    image = cache.get("week_plot")
    if image:
        return HttpResponse(image, content_type="image/svg+xml")

    trackers = Tracker.objects.all()  # pylint: disable=no-member

    figure = Figure(figsize=(7, 2))
    ax = figure.subplots()
    width = 0.20
    colors = cycle(("blue", "green", "red", "purple"))

    for i, t in enumerate(trackers):
        dates = dict()
        for d in dates_this_week():
            dates[d] = timedelta()

        records = Record.objects.all().filter(  # pylint: disable=no-member
            tracker=t, date__gte=min(dates.keys())
        )  
        for r in records:
            dates[r.date] += r.num_hours

        dates, values = zip(*sorted(dates.items()))
        dates = [d.strftime("%a") for d in dates]
        values = [(v / timedelta(hours=1)) for v in values]
        locations = [x + width*i for x in range(7)]
        ax.bar(
            locations, values, tick_label=dates, width=width, color=next(colors)
        )  # pylint:disable=no-member


    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        figure.tight_layout()
    
    buf = BytesIO()
    figure.savefig(buf, format="svg")
    cache.set("week_plot", buf.getvalue())
    return HttpResponse(buf.getbuffer(), content_type="image/svg+xml")


@require_GET
def four_week_plot(request):
    image = cache.get("four_week_plot")
    if image:
        return HttpResponse(image, content_type="image/svg+xml")

    # find monday of this week
    monday = datetime.date.today()
    while monday.isoweekday() != 1:
        monday -= datetime.timedelta(days=1)

    # find monday five weeks ago
    start = monday - datetime.timedelta(days=7 * 4)
    end = start + datetime.timedelta(days=7)
    data = dict()
    trackers = Tracker.objects.all()  # pylint: disable=no-member

    # collect data and store it in dict
    for _ in range(4):
        data[start] = dict()
        for t in trackers:
            # find sum of all records monday-sunday
            total = (
                Record.objects.all()  # pylint:disable=no-member
                .filter(tracker=t)
                .filter(date__gte=start)
                .filter(date__lt=end)
                .aggregate(Sum("num_hours"))
            )
            # record it in the range dictionary
            data[start][t.name] = total
        start += datetime.timedelta(days=7)
        end += datetime.timedelta(days=7)

    # create figure
    figure = Figure(figsize=(8, 2))
    ax = figure.subplots()
    width = 0.20
    colors = cycle(("blue", "green", "red", "purple"))

    # plot the data dict
    dates = list(sorted(data.keys()))
    dates_pretty = [d.strftime("%b %d") for d in dates]
    for i, t in enumerate(trackers):
        values = []
        for d in dates:
            values.append((data[d][t.name]["num_hours__sum"] or timedelta()) / timedelta(days=1))
        locations = [x + width * i - width for x in range(4)]
        ax.bar(
            locations, values, tick_label=dates_pretty, width=width, color=next(colors)
        )

    # save the image in cache
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        figure.tight_layout()
    buf = BytesIO()
    figure.savefig(buf, format="svg")
    cache.set("four_week_plot", buf.getvalue())
    return HttpResponse(buf.getbuffer(), content_type="image/svg+xml")


@require_POST
def session_settings_detail(request, tracker_id):
    tracker = get_object_or_404(Tracker, id=tracker_id)
    form = SessionSettingsForm(request.POST, instance=tracker.session)
    if form.is_valid():
        form.save()
        messages.success(request, "Session settings saved.")
        return redirect("tracker_detail", tracker.id)
    else:
        messages.error(request, form.errors.as_json())
        return redirect("tracker_detail", tracker.id)