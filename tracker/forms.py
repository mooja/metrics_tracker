from django import forms
from .models import Tracker, Record


class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        fields = ("id", "name",)


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ("date", "num_hours",)