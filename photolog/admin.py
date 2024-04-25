from django.contrib import admin

from photolog.models import Note, Photo


# Register your models here.
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    pass


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass
