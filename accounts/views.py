from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
)
from django.http import HttpResponseRedirect
from django.views.generic import CreateView

from accounts.forms import LoginForm, SignupForm
from accounts.models import User


class SignupView(CreateView):
    model = User
    form_class = SignupForm
    template_name = "crispy_form.html"
    success_url = "accounts:login"
    extra_context = {"form_title": "회원가입"}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            redirect_to = self.success_url
            if redirect_to != request.path:
                messages.warning(request, "로그인 유저는 회원가입할 수 없습니다.")
                return HttpResponseRedirect(redirect_to)
        response = super().dispatch(request, *args, **kwargs)
        return response

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.object
        auth_login(self.request, user)
        messages.success(self.request, "회원가입을 환영합니다.")

        return response


signup = SignupView.as_view()


class LoginView(DjangoLoginView):
    form_class = LoginForm
    template_name = "crispy_form.html"
    redirect_authenticated_user = True
    extra_context = {"form_title": "로그인"}


login = LoginView.as_view()


class LogoutView(DjangoLogoutView):
    next_page = "accounts:login"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(self.request, message="로그아웃 했습니다.")
        return response


logout = LogoutView.as_view()
