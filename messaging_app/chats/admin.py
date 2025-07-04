from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for custom User model."""
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'date_of_birth', 'created_at')
        }),
    )
    readonly_fields = ('user_id', 'created_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin configuration for Conversation model."""
    list_display = ('conversation_id', 'get_participants', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('participants__email', 'participants__username')
    readonly_fields = ('conversation_id', 'created_at', 'updated_at')
    filter_horizontal = ('participants',)
    
    def get_participants(self, obj):
        return ", ".join([str(user) for user in obj.participants.all()[:3]])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for Message model."""
    list_display = ('message_id', 'sender', 'conversation', 'message_preview', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('sender__email', 'sender__username', 'message_body')
    readonly_fields = ('message_id', 'sent_at')
    
    def message_preview(self, obj):
        return obj.message_body[:50] + "..." if len(obj.message_body) > 50 else obj.message_body
    message_preview.short_description = 'Message Preview'
