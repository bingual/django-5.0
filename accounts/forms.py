from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_tailwind.layout import Submit
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import ModelForm
from tailwind.validate import ValidationError

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
        self.helper.form_class = "space-y-6"
        self.helper.label_class = (
            "block mb-2 text-sm font-medium text-gray-900 dark:text-white"
        )

        self.helper.layout = Layout("username", "password1", "password2", "email")
        self.helper.add_input(
            Submit(
                "submit",
                "회원가입",
                css_class="w-full text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none "
                "focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 "
                "dark:hover:bg-blue-700 dark:focus:ring-blue-800",
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
        self.helper.form_class = "space-y-6"
        self.helper.label_class = (
            "block mb-2 text-sm font-medium text-gray-900 dark:text-white"
        )

        self.helper.layout = Layout("username", "password")
        self.helper.add_input(
            Submit(
                "submit",
                "로그인",
                css_class="w-full text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none "
                "focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 "
                "dark:hover:bg-blue-700 dark:focus:ring-blue-800",
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
        self.helper.form_class = "space-y-6"
        self.helper.label_class = (
            "block mb-2 text-sm font-medium text-gray-900 dark:text-white"
        )

        self.helper.layout = Layout("avatar")
        self.helper.add_input(
            Submit(
                "submit",
                "저장",
                css_class="w-full text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none "
                "focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 "
                "dark:hover:bg-blue-700 dark:focus:ring-blue-800",
            )
        )
