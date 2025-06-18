from rest_framework import serializers
from .models import ChatSession, ChatMessage, ProductRecommendation, ChatbotConfig
from catalogue.serializers import ProductSerializer

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'session_id', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductRecommendationSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = ProductRecommendation
        fields = ['id', 'product', 'confidence_score', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    recommendations = ProductRecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_type', 'content', 'timestamp', 'metadata', 'recommendations']
        read_only_fields = ['id', 'timestamp']

class ChatbotConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotConfig
        fields = ['id', 'name', 'model_name', 'max_tokens', 'temperature', 'system_prompt', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    session_id = serializers.CharField(max_length=255, required=False)
    user_id = serializers.IntegerField(required=False)

class ChatResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    session_id = serializers.CharField()
    recommendations = ProductRecommendationSerializer(many=True, read_only=True)
    metadata = serializers.JSONField(default=dict) 