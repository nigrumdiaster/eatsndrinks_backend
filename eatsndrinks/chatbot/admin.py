from django.contrib import admin
from .models import ChatSession, ChatMessage, ProductRecommendation, ChatbotConfig

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp', 'session']
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(ProductRecommendation)
class ProductRecommendationAdmin(admin.ModelAdmin):
    list_display = ['message', 'product', 'confidence_score', 'created_at']
    list_filter = ['confidence_score', 'created_at']
    search_fields = ['product__name', 'reason']
    readonly_fields = ['created_at']

@admin.register(ChatbotConfig)
class ChatbotConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_name', 'max_tokens', 'temperature', 'is_active']
    list_filter = ['is_active', 'model_name']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('openai_api_key',)
        return self.readonly_fields
