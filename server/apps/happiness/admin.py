from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Happiness, Team, UserProfile


@admin.register(Happiness)
class HappinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'level', 'user_id')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


User = get_user_model()
admin.site.unregister(User)
@admin.register(User)
class UserProfileAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('team',)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = [UserProfileInline]
        return super().change_view(request, object_id, form_url, extra_context)

    def team(self, obj):
        return obj.userprofile.team.name if obj.userprofile.team else None

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('userprofile__team')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
