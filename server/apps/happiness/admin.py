from django.contrib import admin

from .models import Happiness


@admin.register(Happiness)
class HappinessAdmin(admin.ModelAdmin):
    pass
