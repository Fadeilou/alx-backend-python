from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Message, Notification, MessageHistory


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk: # Check if the message already exists
        old_message = Message.objects.filter(pk=instance.pk).first()
        if old_message and old_message.content != instance.content:
            # Log the old content in MessageHistory
            MessageHistory.objects.create(message=instance, old_content=old_message.content)
            # Update edit-related fields
            instance.edited = true
            instance.edited_at = now() # Set the edit timestamp
            # Ensure edited_by is set in the view where edits are handled


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    '''
    Deletes all messages, notifications, and message histories related to the user when their account is deleted.
    '''
    # Delete all messages where the user is the sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Delete all notifications associated with the user
    Notifiication.objects.filter(user=instance).delete()
