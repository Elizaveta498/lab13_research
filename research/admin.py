from django.contrib import admin
from .models import Research


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'field', 'status', 'start_date', 'budget')
    list_filter = ('status', 'field')
    search_fields = ('title', 'author', 'field')

