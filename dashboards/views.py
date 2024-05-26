from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin


from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from dashboards.models import ApplicationUser
from django.contrib.auth.models import Permission
from survey.models.response import Response

from .forms import ExperimenterCreationForm, ParticipantCreationForm

class HomeIndexView(TemplateView):
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_logged'] = self.request.user.is_authenticated
        return context

# def Login_survey(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         if username and password:
#             username = username.strip()
#             try:
#                 user = ApplicationUser.objects.get(username=username)
#             except:
#                 return render(request, './registration/login.html')
#             if user.password == password:
#                 return redirect('survey/')
#     return render(request, './registration/login.html')

class StyleTest(TemplateView):
    template_name = "style.html"


# def logout_view(request):
#     response = logout(request, next_page=reverse('app.home.views.home'))
#     response.delete_cookie('user_location')
#     return response

def signup_experimenter(request):
    if request.method == 'POST':
        form = ExperimenterCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(
                username=username,
                password=password
            )
            perm_codename = ["add_category",
                             "change_category",
                             "delete_category",
                             "view_category",
                             "add_survey",
                             "change_survey",
                             "delete_survey",
                             "view_survey",
                             "view_response",
                             "add_question",
                             "change_question",
                             "delete_question",
                             "view_question",
                             "add_answer",
                             "change_answer",
                             "delete_answer",
                             "view_answer",
                             "experimenter",
                             "participant"
                             ]
            for codename in perm_codename:
                user.user_permissions.add(Permission.objects.filter(codename=codename)[0])

            user.is_staff = True
            user.save()
            login(request, user)
            print(user.has_perm('survey.experimenter'))
            print(user.has_perm('survey.participant'))
            return redirect('admin:index')  # Replace 'home' with the URL name of your home page
    else:
        form = ExperimenterCreationForm()
    return render(request, './registration/register_experimenter.html', {'form': form})


def signup_participant(request):
    if request.method == 'POST':
        form = ParticipantCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(
                username=username,
                password=password
            )

            login(request, user)
            ad = Permission.objects.filter(codename='participant')[0]
            print(ad)
            user.user_permissions.add(ad)
            print(user.has_perm('survey.participant'))
            return redirect('home_n')  # Replace 'home' with the URL name of your home page
    else:
        form = ParticipantCreationForm()
    return render(request, './registration/register_participant.html', {'form': form})



class My_page(PermissionRequiredMixin,TemplateView):
    template_name = "mypage.html"
    permission_required = ('survey.participant',)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answer_list = Response.objects.filter(
            user=self.request.user
        )
        context["answer_list"] = answer_list
        return context

# def login_experimenter(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         if username and password:
#             username = username.strip()
#             try:
#                 user = ApplicationUser.objects.get(username=username)
#             except:
#                 return render(request, './registration/experimenter_login.html')
#             if user.password == password:
#                 return redirect('survey/')
#     return render(request, './registration/login.html')




