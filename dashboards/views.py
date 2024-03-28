from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from dashboards.models import ApplicationUser


class HomeIndexView(TemplateView):
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_logged'] = self.request.user.is_authenticated
        return context

def Login_survey(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            username = username.strip()
            try:
                user = ApplicationUser.objects.get(username=username)
            except:
                return render(request, './registration/login.html')
            if user.password == password:
                return redirect('survey/')
    return render(request, './registration/login.html')

# def Logout_survey(request):
#     pass
#     return render(request, './registration/logout.html')
#
# def Register_survey(request):
#     pass
#     return render(request, './registration/register.html')

class StyleTest(TemplateView):
    template_name = "style.html"

