from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm, ProfileForm
from users.models import User
from django.views.generic.base import TemplateView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
# from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


@login_required
def update_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user == user:
        profile_form = ProfileForm(
            request.POST or None,
            files=request.FILES or None,
            instance=user
        )
        if profile_form.is_valid():
            user = profile_form.save(commit=False)
            user.user_id = user.id
            profile_form.save()
            return redirect(
                reverse_lazy('posts:profile', args=[user.username])
            )
        return render(request, 'users/add_profile_info.html', {
            'form': profile_form
        })
    return redirect(reverse_lazy('posts:profile', args=[user.username]))


@login_required
def profile_page(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        context = {
            'user': user,
        }
        return render(request, 'users/profile.html', context)
    return redirect(reverse_lazy('posts:profile', args=[username]))


class SuccessLogout(TemplateView):
    template_name = 'users/logged_out.html'


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('auth:succsess_password_change')


class SuccessPasswordChange(TemplateView):
    template_name = 'users/password_change_done.html'


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('auth:succsess_password_change')
