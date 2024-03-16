from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect


class HomeIndexView(TemplateView):
    template_name = "home.html"

