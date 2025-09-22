import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.


class CustomUserManager(BaseUserManager):
	def create_user(
		self, email_address, password=None, first_name=None, last_name=None
	):
		if not email_address:
			raise ValueError('An email address must be set')

		email_address = self.normalize_email(email_address)

		user = self.model(
			email_address=email_address,
			first_name=first_name,
			last_name=last_name
		)

		if password:
			user.set_password(password)
		else:
			# For users without passwords (Google sign-in).
			user.set_unusable_password()

		user.save(using=self._db)

		return user

	def create_superuser(
		self, email_address, password, first_name=None, last_name=None
	):
		user = self.create_user(
			email_address=email_address,
			password=password,
			first_name=first_name,
			last_name=last_name
		)

		user.is_superuser = True
		user.is_staff = True
		user.save(using=self._db)

		return user


class CustomUser(AbstractUser):
	email_address = models.EmailField(unique=True)

	USERNAME_FIELD = 'email_address'
	REQUIRED_FIELDS = ['first_name', 'last_name']

	objects = CustomUserManager()

	def __str__(self):
		return self.email_address


class Chat(models.Model):
	id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

	# Associate this Chat model with CustomUser.
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="chats")

	title = models.CharField(max_length=255, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title or f"Session {self.id}"


class ChatMessage(models.Model):
	ROLES = (
		("assistant", "assistant"),
		("user", "user")
	)

	chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
	role = models.CharField(max_length=15, choices=ROLES)
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.role}: {self.content[:50]}"