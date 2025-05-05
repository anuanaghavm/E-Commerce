from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        return {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'user': user  # 👈 used for JWT
        }

class ForgotPasswordSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        name = data.get('name')
        email = data.get('email')
        try:
            user = User.objects.get(name=name, email=email)
            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found with given name and email.")
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        current_password = data.get('current_password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email.")

        if not user.check_password(current_password):
            raise serializers.ValidationError("Current password is incorrect.")

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user
