from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token

from promptify_app.models import Chat, ChatMessage, CustomUser


class ChatSerializer(serializers.ModelSerializer):
	class Meta:
		model = Chat 
		fields = "__all__"


# class ChatMessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ChatMessage 
#         fields = ["id", "role", "content", "created_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = ChatMessage 
		fields = ["role", "content"]


class UserRegistrationSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, validators=[validate_password])
	password_confirm = serializers.CharField(write_only=True)

	class Meta:
		model = CustomUser
		fields = ('email_address', 'password', 'password_confirm', 'first_name', 'last_name')

	def validate(self, attrs):
		if attrs['password'] != attrs['password_confirm']:
			raise serializers.ValidationError("Passwords don't match")
		return attrs

	def create(self, validated_data):
		validated_data.pop('password_confirm')

		print('validated_data:', validated_data)

		user = CustomUser.objects.create_user(**validated_data)

		Token.objects.create(user=user)

		return user


class UserLoginSerializer(serializers.Serializer):
	email_address = serializers.EmailField()
	password = serializers.CharField(write_only=True)
	
	def validate(self, attrs):
		email_address = attrs.get('email_address')
		password = attrs.get('password')
		
		if email_address and password:
			user = authenticate(username=email_address, password=password)

			if not user:
				raise serializers.ValidationError('Invalid credentials')

			if not user.is_active:
				raise serializers.ValidationError('User account is disabled')
			attrs['user'] = user
		else:
			raise serializers.ValidationError('Must include email address and password')

		return attrs


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ('id', 'email_address', 'first_name', 'last_name', 'date_joined')
		read_only_fields = ('id', 'date_joined')