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

        if self.instance and self.instance.id:
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
        fields = ("name", "action")


class RecordForm(forms.ModelForm):
    action = forms.CharField(required=True, validators=[validate_action])

    def __init__(self, *args, fh_data, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "w-full p-0"

        if fh_data.get('record_id', False):
            self.helper.form_action = reverse("record_detail", kwargs={'tracker_id': fh_data["tracker_id"], 'record_id': fh_data["record_id"]})
        else:
            self.helper.form_action = reverse("record_detail", kwargs={'tracker_id': fh_data["tracker_id"]})


        index_layout = Layout(
            Div(
                HTML("<style>label { display: none }</style>"),
                "tracker",
                Field("num_hours", placeholder="New session time.", css_class="w-full px-1 py-2 mb-1 text-center text-lg"),
                Field("date", widget=forms.HiddenInput(), css_class="hidden"),
                Submit("action", "add", css_class="w-1/2 px-1 py-2 capitalize"),
                css_class="flex flex-col justify-center items-center"
            )
        )

        record_detai_layout = Layout(
            Div(
                Field("num_hours", css_class="w-12 px-1 py-2 mr-2 text-center flex-initial rounded border border-blue-500"),
                HTML(" hour session on "),
                Field("date", type="date", css_class="w-32 mx-2 px-1 py-2 text-center border border-blue-500 rounded "),
                Submit("action", "update" if self.instance.id else "add", css_class="p-2 m-1 bg-blue-300 border rounded"),
                Submit("action", "delete", css_class="p-2 m-1 bg-red-300 border rounded") if self.instance.id else None,
                "tracker",
                HTML("{{ form.erros }}"),
                css_class="flex flex-row items-center",
            )
        )

        self.helper.layout = index_layout if fh_data.get("index_view", False) else record_detai_layout

    
    class Meta:
        model = Record
        fields = ("tracker", "num_hours", "date", "action")
        widgets = {
            "tracker": forms.HiddenInput(),
        }