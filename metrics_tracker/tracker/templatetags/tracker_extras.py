from datetime import timedelta

from django import template

register = template.Library()


def minutes(td: timedelta):
    assert isinstance(td, timedelta), "Duration must be a timedelta"
    return str(int(td / timedelta(minutes=1))).zfill(2) 

def seconds(td: timedelta):
    assert isinstance(td, timedelta), "Duration must be a timedelta"
    return str(int(td / timedelta(seconds=1) % 60)).zfill(2)

register.filter('minutes', minutes)
register.filter('seconds', seconds)