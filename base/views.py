from django.shortcuts import render
from django.views.generic.base import TemplateView


def render_template(name):
    """
    Just a shortcuts method.
    """
    return TemplateView.as_view(template_name=name)
