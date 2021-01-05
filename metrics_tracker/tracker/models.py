import datetime
import base64

from io import BytesIO
from datetime import timedelta
from collections import namedtuple, defaultdict

from matplotlib.figure import Figure

from django.db import models


# Create your models here.
class Tracker(models.Model):
    name = models.CharField(max_length=200)

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
    date = models.DateField(null=False, default=datetime.date.today())
    num_hours = models.IntegerField(null=False)