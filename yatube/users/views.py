from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm
from django.views.generic.base import TemplateView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class SuccessLogout(TemplateView):
    template_name = 'users/logged_out.html'


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('auth:succsess_password_change')


class SuccessPasswordChange(TemplateView):
    template_name = 'users/password_change_done.html'


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('auth:succsess_password_change')
