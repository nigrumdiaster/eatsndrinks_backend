from django.db import models
from django.conf import settings
from django.utils import timezone

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Chat Session {self.session_id} - {self.user.username if self.user else 'Anonymous'}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
        ('system', 'System Message'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)  # Store additional data like recommended products
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class ProductRecommendation(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='recommendations')
    product = models.ForeignKey('catalogue.Product', on_delete=models.CASCADE)
    confidence_score = models.FloatField(default=0.0)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recommendation: {self.product.name} (Score: {self.confidence_score})"

class ChatbotConfig(models.Model):
    """Configuration for chatbot behavior"""
    name = models.CharField(max_length=100, unique=True)
    openai_api_key = models.CharField(max_length=255, blank=True)
    model_name = models.CharField(max_length=50, default='gpt-3.5-turbo')
    max_tokens = models.IntegerField(default=1000)
    temperature = models.FloatField(default=0.7)
    system_prompt = models.TextField(default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Chatbot Config: {self.name}"
