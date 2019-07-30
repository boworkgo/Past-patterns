from django.contrib import admin

from .models import Event


class EventAdmin(admin.ModelAdmin):
    fieldsets = [("Necessary", {"fields": ["title", "text"]})]
    list_display = ("title", "pub_date", "was_important")
    list_filter = ["pub_date"]
    search_fields = ["title", "text"]


admin.site.register(Event, EventAdmin)
