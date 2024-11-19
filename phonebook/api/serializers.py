from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

from rest_framework import serializers
from django.contrib.auth import get_user_model


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        # Try to authenticate the user
        user = get_user_model().objects.filter(phone_number=phone_number).first()
        
        if not user:
            raise serializers.ValidationError("User with this phone number does not exist.")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")

        # If the user is authenticated, generate tokens
        tokens = RefreshToken.for_user(user)
        return {
            'access': str(tokens.access_token),
            'refresh': str(tokens),
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  # Your custom user model
        fields = ['id', 'name', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Ensures password is not returned in responses

    def create(self, validated_data):
        password = validated_data.pop('password')  # Remove password from validated data
        user = CustomUser(**validated_data)  # Create user instance without password
        user.set_password(password)  # Hash the password before saving
        user.save()  # Save the user with the hashed password
        return user