from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView

from photolog.forms import NoteCreateForm
from photolog.models import Note, Photo


def index(request):

    note_qs = Note.objects.all().select_related("author").prefetch_related("photo_set")

    return render(
        request,
        "photolog/index.html",
        {
            "note_list": note_qs,
        },
    )


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteCreateForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "기록 생성"}

    def form_valid(self, form):
        self.object = form.save(commit=False)  # noqa

        new_note = self.object
        new_note.author = self.request.user
        new_note.save()

        photo_file_list = form.cleaned_data.get("photos")
        if photo_file_list:
            Photo.create_photos(new_note, photo_file_list)

        messages.success(self.request, "새 기록을 저장했습니다.")

        return redirect(self.get_success_url())


note_new = NoteCreateView.as_view()


class NoteDetailView(DetailView):
    model = Note


note_detail = NoteDetailView.as_view()
