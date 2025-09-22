from openai import OpenAI
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from promptify_app.models import Chat, ChatMessage, CustomUser
from promptify_app.serializers import (
  ChatMessageSerializer, ChatSerializer, 
  UserRegistrationSerializer, UserLoginSerializer,
	UserSerializer
)

from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
import secrets
import logging

logger = logging.getLogger(__name__)

# Create your views here.
client = OpenAI()


now = timezone.now()
today = now.date()
yesterday = today - timedelta(days=1)
seven_days_ago = today - timedelta(days=7)
thirty_days_ago = today - timedelta(days=30)


def createChatTitle(user_message):
	try:
		response = client.chat.completions.create(
			model="gpt-4o-mini",
			messages=[
				{"role": "assistant", "content": "Give a short, descriptive title for this conversation in not more than 5 words."},
				{"role": "user", "content": user_message}
			]
		)

		title = response.choices[0].message.content.strip()
	except Exception: 
		title = user_message[:50]
	return title


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prompt_gpt(request):
	chat_id = request.data.get("chat_id")
	content = request.data.get("content")

	if not chat_id:
		return Response({"error": "Chat ID was not provided."}, status=400)

	if not content:
		return Response({"error": "There was no prompt passed."}, status=400)

	chat, created = Chat.objects.get_or_create(id=chat_id, defaults={'user': request.user})

	if not created and chat.user != request.user:
		return Response({"error": "You don't have permission to access this chat."}, status=403)
	
	chat.title = createChatTitle(content)
	chat.save()

	ChatMessage.objects.create(role="user", chat=chat, content=content)

	chat_messages = chat.messages.order_by("created_at")[:10]

	openai_messages = [{"role": message.role, "content": message.content} for message in chat_messages]

	if not any(message["role"]=="assistant" for message in openai_messages):
		openai_messages.insert(0, {"role": "assistant", "content": "You are a helpful assistant."})

	try:
		response = client.chat.completions.create(
			model="gpt-4o-mini",
			messages=openai_messages
		)

		openai_reply = response.choices[0].message.content
	except Exception as e:
		return Response({"error": f"An error from Openai {str(e)}"}, status=500)

	ChatMessage.objects.create(role="assistant", content=openai_reply, chat=chat)

	return Response({"reply": openai_reply}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_chat_messages(request, pk):
	chat = get_object_or_404(Chat, id=pk, user=request.user)
	chatmessages = chat.messages.all()
	serializer = ChatMessageSerializer(chatmessages, many=True)
	return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def todays_chat(request):
	chats = Chat.objects.filter(user=request.user, created_at__date=today).order_by("-created_at")[:10]
	serializer = ChatSerializer(chats, many=True)
	return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def yesterdays_chat(request):
	chats = Chat.objects.filter(user=request.user, created_at__date=yesterday).order_by("-created_at")[:10]
	serializer = ChatSerializer(chats, many=True)
	return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def seven_days_chat(request):
	chats = Chat.objects.filter(user=request.user, created_at__lt=yesterday, created_at__gte=seven_days_ago).order_by("-created_at")[:10]
	serializer = ChatSerializer(chats, many=True)
	return Response(serializer.data)


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
	print('request.data:', request.data)

	serializer = UserRegistrationSerializer(data=request.data)

	print('serializer.is_valid():', serializer.is_valid())

	if serializer.is_valid():
		user = serializer.save()
		token, created = Token.objects.get_or_create(user=user)
		user_serializer = UserSerializer(user)

		# send_verification_code(request)

		return Response({
			'user': user_serializer.data,
			'token': token.key
		}, status=status.HTTP_201_CREATED)

	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
	serializer = UserLoginSerializer(data=request.data)
	if serializer.is_valid():
		user = serializer.validated_data['user']
		token, created = Token.objects.get_or_create(user=user)
		user_serializer = UserSerializer(user)
		return Response({
			'user': user_serializer.data,
			'token': token.key
		}, status=status.HTTP_200_OK)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
	try:
		request.user.auth_token.delete()
		return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
	except:
		return Response({'error': 'Error logging out'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
  serializer = UserSerializer(request.user)
  return Response(serializer.data, status=status.HTTP_200_OK)

# Nonce
def generate_activation_token():
  # Generates a URL-safe, 32-byte random token
	# (can adjust length).
  return secrets.token_urlsafe(32)

class ActivationToken(models.Model):
	# OneToOneField links token to a single user.
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE
	)

	# The unique activation token.
	activation_token = models.CharField(max_length=64, unique=True)

	created_at = models.DateTimeField(auto_now_add=True)

	# expires_at defines token expiration time.
	expires_at = models.DateTimeField()

	# used flags whether token has been consumed.
	used = models.BooleanField(default=False)

	def is_expired(self):
		return timezone.now() > self.expires_at

	def mark_used(self):
		self.used = True
		self.save()

def create_activation_token_obj(user, activation_token):
	# Create the ActivationToken object.
	ActivationToken.objects.create(
		user=user,
		activation_token=activation_token,
		expires_at=timezone.now() + timedelta(hours=24),
		# Default setting.
		used=False
	)
	print('Activation token object created.')

def create_user_if_not_exists(email_address, activation_token):
	User = get_user_model()

	# Try to find the user
	user = User.objects.filter(email_address=email_address).first()

	if user:
		if user.is_active:
			print('The user already exists and has an active account.')
			return
		else:
			print('The user exists, but their account is not active.')
	else:
		print('New User object created')

		# Create a new user if not found
		user = User.objects.create_user(
			email_address=email_address
		)

		user.save()

	# Only reach here if user is not active (either found or just created)
	create_activation_token_obj(user, activation_token)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_code(request):
	"""
	Endpoint to send a verification email to the user.
	Expects JSON payload with 'emailAddress' key.
	"""

	activation_token = str(generate_activation_token())

	try:
		data = request.data

		print('data:', data)

		email_address = data.get('emailAddress')

		if not email_address:
			logger.warning("Verification email request missing 'email' field.")

			return JsonResponse(
				{'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST
			)

		email_body = (
			f'<p style="font-size: 1.2rem;">'
			f'Click on the subsequent link to confirm your Cognitia sign up: <br>'
			f'http://localhost:5173/confirm-email/{activation_token}'
			f'</p>'
		)

		# Compose the email.
		email = EmailMessage(
			subject='Sign in to Cognitia',
			body=email_body,
			from_email='team.cognitia.ai@gmail.com',
			to=[email_address],
			headers={'X-Custom-Header': 'CognitiaVerification'}
		)

		# This way the font size of values assigned
		# to body can be larger.
		email.content_subtype = "html"

		# Send the email asynchronously in production
		# (example: using Celery).
		email.send(fail_silently=False)

		create_user_if_not_exists(email_address, activation_token)

		logger.info(f"Sent verification email to {email_address}")

		return JsonResponse(
			{'message': 'Verification email sent successfully'},
			status=status.HTTP_200_OK
		)

	except Exception as exc:
		logger.error(f"Error sending verification email: {exc}", exc_info=True)

		return JsonResponse(
			{'error': 'Internal server error. Please try again later.'},
			status=status.HTTP_500_INTERNAL_SERVER_ERROR
		)