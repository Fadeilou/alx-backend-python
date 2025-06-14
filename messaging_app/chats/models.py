from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid


class User(AbstractUser):
    """Extended User model with additional fields for messaging functionality."""
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    password = models.CharField(max_length=128)  # Explicitly define password field
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    """Model to track conversations between users."""
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = ", ".join([str(user) for user in self.participants.all()[:2]])
        participant_count = self.participants.count()
        if participant_count > 2:
            participant_names += f" and {participant_count - 2} others"
        return f"Conversation: {participant_names}"


class Message(models.Model):
    """Model for individual messages within conversations."""
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sent_at']
    
    def __str__(self):
        return f"Message from {self.sender} at {self.sent_at}: {self.message_body[:50]}..."
