from django.db import models
import datetime


# Create your models here.
class Tracker(models.Model):
    name = models.CharField(max_length=200)
    tracker_type_choices = [("H", "Hours Spent"), ("B", "Boolean")]
    tracker_type = models.CharField(max_length=2, choices=tracker_type_choices)

    def hours_this_week(self):
        week_ago = datetime.date.today() - datetime.timedelta(weeks=1)
        records_this_week = Record.objects.all().filter(tracker=self, date__gte=week_ago)
        hours_this_week = sum(r.num_hours for r in records_this_week)
        return hours_this_week



class Record(models.Model):
    tracker = models.ForeignKey(
        Tracker, blank=True, null=False, on_delete=models.CASCADE,
        related_name="records",
        related_query_name="record"
    )
    date = models.DateField(null=False, default=datetime.date.today())
    num_hours = models.IntegerField(null=False)