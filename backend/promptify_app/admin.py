from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from promptify_app.models import Chat, ChatMessage, CustomUser

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )



@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    model = Chat 
    list_display = ("id", "title", "created_at")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    models = ChatMessage 
    list_display = ("id", "role", "content", "created_at")
