from django.urls import path
from . import views

app_name = "photolog"

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.note_new, name="note_new"),
    path("<int:pk>/", views.note_detail, name="note_detail"),
    path("<int:pk>/edit/", views.note_edit, name="note_edit"),
    path("<int:pk>/delete/", views.note_delete, name="note_delete"),
    path("<int:note_pk>/comments/", views.comment_list, name="comment_list"),
    path("<int:note_pk>/comments/new/", views.comment_new, name="comment_new"),
    path(
        "<int:note_pk>/comments/<int:pk>/delete/",
        views.comment_delete,
        name="comment_delete",
    ),
    path("test/", views.test, name="test"),
]
