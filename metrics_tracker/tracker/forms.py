import re

from django.urls import reverse
from django.shortcuts import reverse
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms import layout

from crispy_forms.layout import *  # pylint: disable=unused-wildcard-import

from .models import Tracker, Record, Session


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

    def __init__(self, *args, fh_data={}, **kwargs):
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
                Field("num_hours", css_class="px-1 py-2 mr-2 text-center flex-initial rounded border border-blue-500"),
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


class SessionSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_action = reverse("session_settings_detail", kwargs={'tracker_id': self['tracker'].value()})
        self.helper.form_class = 'bg-gray-200 py-8 flex flex-row nowrap items-center'
        self.helper.layout = Layout(
            Hidden('tracker', self['tracker'].value()),
            Field('target_session_count', self['target_session_count'].value(), css_class="flex-initial w-10 px-1 py-2 shadow mr-2 text-center"),
            HTML('Session(s) per Day, with the duration of '),
            Field('target_duration', self['target_duration'].value(), css_class="flex-initial w-20 px-1 py-2 mx-2 shadow text-center"),
            HTML('<input type="submit" value="Update" class="flex-initial px-1 py-2 bg-green-300">')
        )

    class Meta:
        model = Session
        fields = ("tracker", "target_duration", "target_session_count")


def ActionValidator(action):
    actions_re = re.compile(r"start|stop|pause|resume|next|log|reset")
    if not actions_re.match(action):
        raise ValidationError("form does not suppert this action")


class SessionControlsForm(forms.ModelForm):
    action = forms.CharField(required=True, validators=[ActionValidator])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_class = "flex-initial w-full sm:w-1/3 mt-2 sm:mt-0 flex flex-row justify-center sm:justify-end"
        self.helper.form_action = reverse("session_detail", kwargs={'tracker_id': self['tracker'].value()})
        self.helper.layout = Layout(
            Hidden('tracker', self['tracker'].value()),
            Hidden('status', self['status'].value()),
        )

        if self['status'].value() == 'NEW':
            self.helper.layout.append(
               HTML('<button type="submit" name="action" class="bg-green-600 text-white font-bold px-1 py-2 ml-1" value="start">Start</button>') 
            )

        elif self['status'].value() == 'ACTIVE':
            self.helper.layout.extend((
               HTML('<button type="submit" name="action" class="bg-yellow-600 text-white font-bold px-1 py-2 ml-1" value="pause">Pause</button>'),
               HTML('<button type="submit" name="action" class="bg-red-600 text-white font-bold px-1 py-2 ml-1" value="stop">Stop</button>')
            ))

        elif self['status'].value() == 'PAUSED':
            self.helper.layout.extend((
               HTML('<button type="submit" name="action" class="bg-green-600 text-white font-bold px-1 py-2 ml-1" value="resume">Resume</button>'),
               HTML('<button type="submit" name="action" class="bg-red-600 text-white font-bold px-1 py-2 ml-1" value="stop">Stop</button>')
            ))

        elif self['status'].value() == 'FINISHED':
            self.helper.layout.extend([
               HTML('<button type="submit" name="action" class="bg-blue-600 text-white font-bold px-1 py-2 ml-1" value="log">Save</button>'),
               HTML('<button type="submit" name="action" class="bg-red-600 text-white font-bold px-1 py-2 ml-1" value="reset">Discard</button>'),
            ])

    
    class Meta:
        model = Session
        fields = ("tracker", "action", "status")