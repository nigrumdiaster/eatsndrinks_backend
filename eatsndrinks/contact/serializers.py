from .models import Contact
from rest_framework import serializers

# Serializer
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['created_at']

    # def update(self, instance, validated_data):
    #     # Allow only 'is_replied' to be updated
    #     if 'is_replied' in validated_data:
    #         instance.is_replied = validated_data['is_replied']
    #         instance.save()
    #     return instance
