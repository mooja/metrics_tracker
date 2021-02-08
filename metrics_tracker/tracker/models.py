import datetime
import base64
import json

from io import BytesIO
from datetime import timedelta, timezone
from collections import namedtuple, defaultdict

from django.utils import timezone

from matplotlib.figure import Figure

from django.db import models


class Tracker(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"<Tracker \"{self.name}\">"

    def hours_this_week(self):
        start = datetime.date.today()
        while start.isoweekday() != 1:
            start = start - timedelta(days=1)

        records_this_week = Record.objects.all().filter(tracker=self, date__gte=start)  # pylint: disable=no-member
        hours_this_week = sum(r.num_hours for r in records_this_week)
        return hours_this_week
    

    def this_week_plot(self, figure):
        start = datetime.date.today()
        while start.isoweekday() != 1:
            start = start - timedelta(days=1)
        
        records_this_week = Record.objects.all()\
            .filter(tracker=self, date__gte=start) # pylint: disable=no-member
        
        dates_hours = dict()
        date = start
        while date <= datetime.date.today():
            dates_hours[date] = 0
            date += timedelta(days=1)

        for r in records_this_week:
            dates_hours[r.date] += r.num_hours
        
        ax = figure.subplots()
        ax.plot(dates_hours.keys(), dates_hours.values())


    def hours_last_week(self):
        hours = sum(r.sum_hours for r in self.prev_weeks_records(1))
        return hours
    

    def prev_weeks_records(self, num_weeks=4):
        start = datetime.date.today()
        while start.isoweekday() != 1:
            start = start - timedelta(days=1)
        start = start - timedelta(weeks=1)

        WeekRecord = namedtuple("WeekRecord", "start, end, sum_hours")
        for _ in range(num_weeks):
            end = start + timedelta(weeks=1)
            sum_hours = sum(r.num_hours 
                for r in Record.objects.all()  #y pylint: disable=no-member
                            .filter(tracker=self, date__gte=start, date__lte=end)
            )
            yield WeekRecord(start, end, sum_hours)
            start = start - timedelta(weeks=1)


class Record(models.Model):
    tracker = models.ForeignKey(
        Tracker, blank=True, null=False, on_delete=models.CASCADE,
        related_name="records",
        related_query_name="record"
    )
    date = models.DateField(null=False, default=timezone.now)
    num_hours = models.DurationField(null=False)

    def __str__(self):
        return f"<Record for {self.tracker.name}, id={self.id}>"  # pylint: disable=no-member



class Session(models.Model):
    NEW = 'NEW'
    ACTIVE = 'ACTIVE'
    PAUSED = 'PAUSED'
    FINISHED = 'FINISHED'
    SESSION_CHOICES = (
        (NEW, 'New'),
        (ACTIVE, 'Active'),
        (PAUSED, 'Paused'),
        (FINISHED, 'Finished'),
    )

    tracker = models.OneToOneField(Tracker, on_delete=models.CASCADE, primary_key=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=SESSION_CHOICES, default=NEW)

    target_duration = models.DurationField(default=timedelta(minutes=60))
    target_session_count = models.IntegerField(null=False, default=1)
    session_count_today = models.IntegerField(null=False, default=0)
    session_count_update_timestamp = models.DateTimeField(null=False, default=datetime.datetime.now(tz=timezone.utc))

    pause_time = models.DateTimeField(null=True, blank=True)
    paused_duration = models.DurationField(default=timedelta())


    def is_finished(self) -> bool:
        return self.active_duration >= self.target_duration

    @property
    def active_duration(self):
        if not self.start:
            return timedelta()

        now = datetime.datetime.now(timezone.utc)
        if self.status == Session.FINISHED:
            dur = self.end - self.start - self.paused_duration
        else:
            dur = now - self.start - self.paused_duration

        if self.status == Session.PAUSED:
            dur -= (now - self.pause_time)

        return dur
    
    def begin(self):
        now = datetime.datetime.now(timezone.utc)
        self.start = now
        self.end = None
        self.paused_duration = datetime.timedelta()
        self.pause_time = None
        self.status = Session.ACTIVE
        self.save()
    
    def pause(self):
        now = datetime.datetime.now(timezone.utc)
        self.pause_time = now
        self.status = Session.PAUSED
        self.save()
    
    def resume(self):
        now = datetime.datetime.now(timezone.utc)
        assert self.status == Session.PAUSED, "session must be paused in order to resume"
        assert self.pause_time is not None, "session must be paused to unpause it."
        self.paused_duration += (now - self.pause_time)
        self.pause_time = None
        self.status = Session.ACTIVE
        self.save()
    
    def finish(self):
        self.status = Session.FINISHED
        now = datetime.datetime.now(timezone.utc)
        self.end = now
        self.save()
    
    def save_as_record(self):
        date = self.start.date()
        now = datetime.datetime.now(timezone.utc)
        if self.active_duration > self.target_duration:
            record = Record(tracker=self.tracker, date=date, num_hours=self.target_duration)
        else:
            record = Record(tracker=self.tracker, date=date, num_hours=self.active_duration)
        self.session_count_today += 1
        self.session_count_update_timestamp = now
        record.save()
        self.reset()

    def reset(self):
        now = datetime.datetime.now(timezone.utc)
        self.status = Session.NEW
        self.start = None
        self.end = None
        self.pause_time = None
        self.paused_duration = datetime.timedelta()
        self.session_count_update_timestamp = now
        self.save()
    
    def reset_daily_count(self):
        self.session_count_today = 0
        self.save()