from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_tailwind.layout import Submit
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from accounts.models import User, Profile


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.helper = FormHelper()
        self.helper.attrs = {"novalidate": True}
        self.helper.form_class = "helper_form"
        self.helper.label_class = "helper_label"

        self.helper.layout = Layout("username", "password1", "password2", "email")
        self.helper.add_input(
            Submit(
                "submit",
                "회원가입",
                css_class="helper_submit",
            )
        )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email:
            qs = User.objects.filter(email=email)
            if qs.exists():
                raise ValidationError("해당 이메일은 이미 존재합니다.")
        return email


class LoginForm(AuthenticationForm):

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"novalidate": True}
        self.helper.form_class = "helper_form"
        self.helper.label_class = "helper_label"

        self.helper.layout = Layout("username", "password")
        self.helper.add_input(
            Submit(
                "submit",
                "로그인",
                css_class="helper_submit",
            )
        )


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"novalidate": True}
        self.helper.form_class = "helper_form"
        self.helper.label_class = "helper_label"

        self.helper.layout = Layout("avatar")
        self.helper.add_input(
            Submit(
                "submit",
                "저장",
                css_class="helper_submit",
            )
        )
