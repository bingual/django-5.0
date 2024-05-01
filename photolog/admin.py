from django.contrib import admin

from photolog.models import Note, Photo, Comment


# Register your models here.
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    pass


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
