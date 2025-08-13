from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid


class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]

    # Custom primary key renamed to user_id
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='User ID'
    )

    # Override groups and permissions with custom related_name
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_set",  # Unique related name
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",  # Unique related name
        related_query_name="custom_user",
    )

    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    password = models.CharField(max_length=128)  # Matches Django's AbstractUser

    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        blank=False,
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    username = None  # Remove username field, use email instead

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Removes email from REQUIRED_FIELDS

    def __str__(self):
        return self.email


class Conversation(models.Model):
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Conversation ID'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(
        User,
        through='ConversationParticipant',
        related_name='conversations'
    )

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='participants_info'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversation_participations'
    )

    class Meta:
        unique_together = ('conversation', 'user')

    def __str__(self):
        return f"{self.user.email} in {self.conversation.conversation_id}"


class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Message ID'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages_sent'
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
        return f"Message {self.message_id} by {self.sender.email}"
