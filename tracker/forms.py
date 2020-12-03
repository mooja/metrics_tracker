import re

from django.urls import reverse
from django.shortcuts import reverse
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms import layout

from crispy_forms.layout import *  # pylint: disable=unused-wildcard-import

from .models import Tracker, Record


def validate_action(value):
    action_re = re.compile(r"add|update|delete", re.I)
    if not action_re.match(value):
        raise ValidationError(f"action field should be add|update|delete, rather than {value}.")


class TrackerForm(forms.ModelForm):
    action = forms.CharField(required=True, validators=[validate_action])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "w-full my-2 py-3 px-2 border border-white "

        if "instance" in kwargs and kwargs["instance"].id:
            self.helper.form_action = reverse(
                f"tracker_detail", kwargs={"id": kwargs["instance"].id}
            )
        else:
            self.helper.form_action = reverse("tracker_detail")

        layout = Layout(
            Field("name",
                  placeholder="Tracker Name",
                  css_class="mb-2 px-2 py-1 bg-white text-xl rounded",
            ),
            Div(Field("tracker_type"), css_class=""),
        )

        if not self.instance.id:
            layout.append(Submit("action", "add", css_class="p-2 m-1 bg-blue-300 border rounded"))
        else:
            layout.append(Submit("action", "update", css_class="p-2 m-1 bg-blue-300 border rounded"))

        if self.instance.id:
            layout.append(Submit("action", "delete", css_class="p-2 m-1 bg-red-300 border rounded"))
        
        self.helper.layout = layout

    class Meta:
        model = Tracker
        fields = ("name", "tracker_type", "action")
        widgets = {
            "tracker_type": forms.RadioSelect(choices=Tracker.tracker_type_choices)
        }


class RecordForm(forms.ModelForm):
    action = forms.CharField(required=True, validators=[validate_action])

    def __init__(self, *args, tracker=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "w-full border rounded"

        if "instance" in kwargs and kwargs["instance"].id:
            self.helper.form_action = reverse(
                "record_detail", kwargs={
                    "tracker_id": tracker.id,
                    "record_id": kwargs["instance"].id
                }
            )
        else:
            self.helper.form_action = reverse("record_detail", kwargs={
                "tracker_id": tracker.id
            })

        self.helper.layout = Layout(
            Div(
                Field("num_hours", css_class="w-12 px-1 py-2 mr-2 text-center flex-initial rounded border border-blue-500"),
                HTML(" hour session on "),
                Field("date", type="date", css_class="w-32 mx-2 px-1 py-2 text-center border border-blue-500 rounded "),
                Submit("action", "update" if self.instance.id else "add", css_class="p-2 m-1 bg-blue-300 border rounded"),
                Submit("action", "delete", css_class="p-2 m-1 bg-red-300 border rounded") if self.instance.id else None,
                css_class="flex flex-row items-center",
            )
        )
    
    class Meta:
        model = Record
        fields = ("num_hours", "date", "action")