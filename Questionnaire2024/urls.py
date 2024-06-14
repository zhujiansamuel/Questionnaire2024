"""Questionnaire2024 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from dashboards.views import (HomeIndexView,
                              StyleTest,
                              signup_experimenter,
                              signup_participant,
                              My_page,
                              Global_setup_page,
                              Add_survey,
                              Add_question)
from django.contrib.auth.views import LogoutView, LoginView, PasswordResetView
from survey.views.index_view import upload_survey
from survey.views.index_view import ExperimenterLoginView


from django.conf.urls.static import static
from django.conf import settings
# from django.conf.urls import

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
]

urlpatterns += [
    # path('accounts/', include'django.contrib.auth.urls')),
    path('accounts/login/experimenter', LoginView.as_view(
        template_name='./registration/experimenter_login.html'
    ),
         name='experimenter_login'),

    path('accounts/login/', LoginView.as_view(
        template_name='./registration/login.html'
    ),
         name='login'),


    path('accounts/logout/', LogoutView.as_view(
        template_name='./registration/logout.html'
    ),
         name='logout'),

    path('accounts/password-reset/', PasswordResetView.as_view(
        template_name='./registration/password_reset_form.html'
    ),
         name='password-reset'),

    path("accounts/mypage/", My_page.as_view(), name='mypage'),
    path("__debug__/", include("debug_toolbar.urls")),
    path("dashboards/", include('dashboards.urls')),
    path("survey/", include("survey.urls")),
    path("style/", HomeIndexView.as_view(), name="home"),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
    path("accounts/", include("allauth.urls")),
    path("", StyleTest.as_view(), name="home_n"),
    path("accounts/signup/experimenter/", signup_experimenter, name='register-experimenter'),
    path("accounts/signup/participant/", signup_participant, name='register-participant'),
    path("uploadsurvey/", upload_survey, name="upload_survey"),
    path("dashboards/", ExperimenterLoginView.as_view(), name="dashboards"),
    path("dashboards/global-setup-page/", Global_setup_page.as_view(), name="global-setup-page"),
    path("dashboards/add-survey/", Add_survey.as_view(), name="add-survey"),
    path("dashboards/<int:id>/add-question/", Add_question.as_view(), name="add-question"),
]

urlpatterns += static(settings.MEDIA_ROOT, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)