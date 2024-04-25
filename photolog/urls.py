from django.urls import path
from . import views

app_name = "photolog"

urlpatterns = [
    path("", views.index, name="index"),
    path("note/<int:pk>", views.note_detail, name="note_detail"),
    path("note/new/", views.note_new, name="note_new"),
    path("note/<int:pk>/edit", views.note_edit, name="note_edit"),
]
