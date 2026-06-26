from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from portal.models import User, StudentProfile, Subject, Result

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser']

# Register all models so they appear in Django Admin
admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile)
admin.site.register(Subject)
admin.site.register(Result)
