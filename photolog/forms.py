from typing import List

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_tailwind.layout import Submit
from django import forms
from django.core.files import File
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.urls import reverse

from photolog.models import Note, Photo, Comment
from theme.helper import make_thumb


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_clean = super().clean  # 함수를 호출하지 않습니다.
        if isinstance(data, (list, tuple)):
            return [single_clean(file) for file in data]
        else:
            return single_clean(data)


class NoteCreateForm(forms.ModelForm):
    photos = MultipleImageField(required=True)

    class Meta:
        model = Note
        fields = ["title", "content", "tags"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"novalidate": True}
        self.helper.form_class = "helper_form"
        self.helper.label_class = "helper_label"

        self.helper.layout = Layout("title", "content", "photos", "tags")
        self.helper.add_input(
            Submit(
                "submit",
                "생성",
                css_class="helper_submit",
            )
        )

    def clean_photos(self):
        is_required = self.fields["photos"].required

        file_list: List[File] = self.cleaned_data.get("photos")
        if not file_list and is_required:
            raise forms.ValidationError("최소 1개의 사진을 등록해주세요.")
        elif file_list:
            try:
                file_list = [make_thumb(file) for file in file_list]
            except Exception as e:
                raise forms.ValidationError(
                    "썸네일 생성 중에 오류가 발생했습니다."
                ) from e
        return file_list


class NoteUpdateForm(NoteCreateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photos"].required = False
        self.helper.form_tag = False
        self.helper.inputs = []


class PhotoInlineForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ["image"]


class CustomBaseInlineFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if index == 0:
            form.fields["DELETE"].widget = forms.HiddenInput()


PhotoUpdateFormSet = inlineformset_factory(
    parent_model=Note,
    model=Photo,
    form=PhotoInlineForm,
    formset=CustomBaseInlineFormSet,
    extra=0,
    can_delete=True,
)
PhotoUpdateFormSet.helper = FormHelper()
PhotoUpdateFormSet.helper.form_tag = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["message"]

    def __init__(self, *args, **kwargs):
        self.note = kwargs.pop("note", None)
        super().__init__(*args, **kwargs)

        if self.note:
            self.helper = FormHelper()
            self.helper.form_id = "comment-form"
            self.helper.form_class = "p-4 md:p-5"
            self.helper.form_show_labels = False
            self.helper.attrs = {
                "hx-post": reverse(
                    "photolog:comment_new", kwargs={"note_pk": self.note.pk}
                ),
                "hx-trigger": "submit",
                "hx-swap": "none",
                "autocomplete": "off",
                "novalidate": True,
            }
            self.helper.layout = Layout("message")
