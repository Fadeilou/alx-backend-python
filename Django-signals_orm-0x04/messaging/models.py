from django.db import models
from django.contrib.auth.models import User
from .managers import UnreadMessagesManager


class UnreadMessagesManager(models.Manager):
    '''
    Custom manager to filter unread messages for a specific user.
    '''
    def for_user(self, user):
        return self.filter(receiver=user, read=False).only("id", "content", "timestamp", "sender")



class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(User, null=True, blank=True, related_name="edited_messages", on_delete=models.SET_NULL)
    read = models.BooleanField(default=False) # New field for read status
    parent_message = models.ForeignKey("self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE)

    objects = models.Manager() # Default Manager
    unread = UnreadMessageManager() # Custom manager for unread messages

    def get_all_replies(self):
        '''
        Recursively fetches all replies to this message.
        '''
        replies = list(self.replies.all())
        for reply in self.replies.all():
            replies.extend(reply.get_all_replies())
        return replies

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} - {self.content[:20]}"


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name="history", on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for Message ID {self.message.id} at {self.edited_timestamp}"


class Notification(models.Model):
    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    message = models.OneToOneField(Message, related_name="notification", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} - Read: {self.read}"
