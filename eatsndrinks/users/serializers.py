from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "first_name", "last_name"]
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure the password is write-only
        }
    def validate_password(self, value):
        # Example validation: Check if password meets a minimum length
        if len(value) < 8:
            raise serializers.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        # You can add more complex validations if needed
        return value
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField( error_messages={
            'blank': 'Tên người dùng không được để trống.',
            }   
        )
    password = serializers.CharField(write_only=True)
    def validate_username(self, value):
        """
        Check if the username is not empty. Custom validation message.
        """
        if not value:
            raise serializers.ValidationError("Tên người dùng không được để trống.")
        return value

    def validate_password(self, value):
        """
        Check if the password meets a minimum length. Custom validation message.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        return value

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "phone_number", "address", "date_of_birth", "password", "is_active"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False}
        }

    def validate_password(self, value):
        if value and len(value) < 8:
            raise serializers.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)