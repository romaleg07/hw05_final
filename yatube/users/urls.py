from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,

)
from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        login_required(views.MyPasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        )),
        name='password_change'
    ),
    path(
        'logget_out/',
        views.SuccessLogout.as_view(),
        name='logget_out'
    ),
    path(
        'password_change/done/',
        views.SuccessPasswordChange.as_view(),
        name='succsess_password_change'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    # path(
    #     'profile/<str:username>/',
    #     views.profile_page,
    #     name='profile'
    # ),
    path(
        'update_profile/<int:user_id>/',
        views.update_profile,
        name='update_profile'
    ),
]
