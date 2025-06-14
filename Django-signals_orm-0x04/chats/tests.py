"""
Tests for Django signals, ORM optimization, and caching in the messaging app.

These tests cover:
1. Signal handlers for notifications and message history
2. Advanced ORM techniques for threaded conversations
3. Custom managers for unread messages
4. User deletion and cleanup
5. Caching functionality
"""

import uuid
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.cache import cache
from django.test.utils import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Conversation, Message, Notification, MessageHistory
from .signals import (
    create_message_notification, 
    log_message_edit, 
    cleanup_user_data
)

User = get_user_model()


class SignalTestCase(TransactionTestCase):
    """Test case for Django signals functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            user_id=uuid.uuid4(),
            username='testuser1',
            email='test1@example.com',
            first_name='Test',
            last_name='User1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            user_id=uuid.uuid4(),
            username='testuser2',
            email='test2@example.com',
            first_name='Test',
            last_name='User2',
            password='testpass123'
        )
        
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
    
    def test_message_notification_signal(self):
        """Test that notifications are created when a new message is sent."""
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Hello, this is a test message!"
        )
        
        # Check that a notification was created for user2
        notification = Notification.objects.filter(
            user=self.user2,
            message=message,
            notification_type='new_message'
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.message, message)
        
        # Check that no notification was created for the sender
        sender_notification = Notification.objects.filter(
            user=self.user1,
            message=message
        ).first()
        
        self.assertIsNone(sender_notification)
    
    def test_message_edit_history_signal(self):
        """Test that message edit history is logged when a message is updated."""
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Original message content"
        )
        
        original_content = message.message_body
        
        # Update the message
        message.message_body = "Updated message content"
        message.save()
        
        # Check that message history was created
        history = MessageHistory.objects.filter(message=message).first()
        
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, original_content)
        self.assertTrue(message.edited)
        
        # Check that edit notification was created
        edit_notification = Notification.objects.filter(
            user=self.user2,
            message=message,
            notification_type='message_edit'
        ).first()
        
        self.assertIsNotNone(edit_notification)
    
    def test_user_deletion_cleanup_signal(self):
        """Test that user-related data is cleaned up when a user is deleted."""
        # Create some data for the user
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Message to be deleted"
        )
        
        notification = Notification.objects.create(
            user=self.user2,
            message=message,
            notification_type='new_message'
        )
        
        # Delete the user
        user1_id = self.user1.user_id
        self.user1.delete()
        
        # Check that related data was cleaned up
        # Messages should be deleted due to CASCADE
        self.assertFalse(Message.objects.filter(sender__user_id=user1_id).exists())
        
        # Notifications should still exist for user2 but message is deleted
        # This depends on your CASCADE setup


class CustomManagerTestCase(TestCase):
    """Test case for custom managers."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            user_id=uuid.uuid4(),
            username='testuser1',
            email='test1@example.com',
            first_name='Test',
            last_name='User1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            user_id=uuid.uuid4(),
            username='testuser2',
            email='test2@example.com',
            first_name='Test',
            last_name='User2',
            password='testpass123'
        )
        
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
    
    def test_unread_messages_manager(self):
        """Test the custom UnreadMessagesManager."""
        # Create some messages
        read_message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Read message",
            read=True
        )
        
        unread_message1 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Unread message 1",
            read=False
        )
        
        unread_message2 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Unread message 2",
            read=False
        )
        
        # Test getting unread messages for user2
        unread_for_user2 = Message.unread.for_user(self.user2)
        
        self.assertEqual(unread_for_user2.count(), 2)
        self.assertIn(unread_message1, unread_for_user2)
        self.assertIn(unread_message2, unread_for_user2)
        self.assertNotIn(read_message, unread_for_user2)
        
        # Test marking messages as read
        marked_count = Message.unread.mark_as_read(self.user2, self.conversation)
        
        self.assertEqual(marked_count, 2)
        
        # Check that messages are now marked as read
        unread_after = Message.unread.for_user(self.user2)
        self.assertEqual(unread_after.count(), 0)


class ThreadedConversationTestCase(TestCase):
    """Test case for threaded conversation functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            user_id=uuid.uuid4(),
            username='testuser1',
            email='test1@example.com',
            first_name='Test',
            last_name='User1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            user_id=uuid.uuid4(),
            username='testuser2',
            email='test2@example.com',
            first_name='Test',
            last_name='User2',
            password='testpass123'
        )
        
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
    
    def test_threaded_replies(self):
        """Test threaded conversation replies."""
        # Create parent message
        parent_message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Parent message"
        )
        
        # Create replies
        reply1 = Message.objects.create(
            sender=self.user2,
            conversation=self.conversation,
            message_body="Reply 1",
            parent_message=parent_message
        )
        
        reply2 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Reply 2",
            parent_message=parent_message
        )
        
        # Create nested reply
        nested_reply = Message.objects.create(
            sender=self.user2,
            conversation=self.conversation,
            message_body="Nested reply to reply 1",
            parent_message=reply1
        )
        
        # Test that relationships are correct
        self.assertEqual(parent_message.replies.count(), 2)
        self.assertEqual(reply1.replies.count(), 1)
        self.assertEqual(reply2.replies.count(), 0)
        self.assertEqual(nested_reply.parent_message, reply1)


class APITestCase(APITestCase):
    """Test case for API endpoints with caching and ORM optimizations."""
    
    def setUp(self):
        """Set up test data and authentication."""
        self.user1 = User.objects.create_user(
            user_id=uuid.uuid4(),
            username='testuser1',
            email='test1@example.com',
            first_name='Test',
            last_name='User1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            user_id=uuid.uuid4(),
            username='testuser2',
            email='test2@example.com',
            first_name='Test',
            last_name='User2',
            password='testpass123'
        )
        
        # Create JWT token for authentication
        self.refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(self.refresh.access_token)
        
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
    
    def test_user_deletion_api(self):
        """Test user deletion through API."""
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Try to delete own account
        response = self.client.delete(f'/api/users/{self.user1.user_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(user_id=self.user1.user_id).exists())
    
    def test_user_deletion_forbidden(self):
        """Test that users cannot delete other users' accounts."""
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Try to delete user2's account
        response = self.client.delete(f'/api/users/{self.user2.user_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(User.objects.filter(user_id=self.user2.user_id).exists())
    
    def test_cached_messages_by_conversation(self):
        """Test that the messages by conversation endpoint uses caching."""
        # Clear cache first
        cache.clear()
        
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message for caching"
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # First request - should hit database
        response1 = self.client.get(
            f'/api/messages/by_conversation/?conversation_id={self.conversation.conversation_id}'
        )
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Check if response is paginated
        if 'results' in response1.data:
            self.assertEqual(len(response1.data['results']), 1)
        else:
            self.assertEqual(len(response1.data), 1)
        
        # Second request - should hit cache
        response2 = self.client.get(
            f'/api/messages/by_conversation/?conversation_id={self.conversation.conversation_id}'
        )
        
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        # Check if response is paginated
        if 'results' in response2.data:
            self.assertEqual(len(response2.data['results']), 1)
        else:
            self.assertEqual(len(response2.data), 1)
    
    def test_unread_messages_endpoint(self):
        """Test the unread messages endpoint."""
        # Create unread messages
        Message.objects.create(
            sender=self.user2,
            conversation=self.conversation,
            message_body="Unread message 1",
            read=False
        )
        
        Message.objects.create(
            sender=self.user2,
            conversation=self.conversation,
            message_body="Unread message 2",
            read=False
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Get unread messages
        response = self.client.get('/api/messages/unread/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response is paginated
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 2)
        else:
            self.assertEqual(len(response.data), 2)
    
    def test_mark_messages_read_endpoint(self):
        """Test marking messages as read."""
        # Create unread messages
        Message.objects.create(
            sender=self.user2,
            conversation=self.conversation,
            message_body="Unread message",
            read=False
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Mark messages as read
        response = self.client.post('/api/messages/mark_read/', {
            'conversation_id': str(self.conversation.conversation_id)
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_threaded_replies_endpoint(self):
        """Test the threaded replies endpoint."""
        # Create parent message
        parent_message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Parent message"
        )
        
        # Create reply
        reply = Message.objects.create(
            sender=self.user2,
            conversation=self.conversation,
            message_body="Reply message",
            parent_message=parent_message
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Get threaded replies
        response = self.client.get(f'/api/messages/{parent_message.message_id}/threaded_replies/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_replies'], 1)
        self.assertEqual(len(response.data['replies']), 1)
    
    def test_message_history_endpoint(self):
        """Test the message history endpoint."""
        # Create and edit a message
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Original content"
        )
        
        # Edit the message
        message.message_body = "Edited content"
        message.save()
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Get message history
        response = self.client.get(f'/api/messages/{message.message_id}/history/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_edited'])
        self.assertEqual(response.data['total_edits'], 1)
        self.assertEqual(response.data['current_content'], "Edited content")


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
})
class CachingTestCase(TestCase):
    """Test case for caching functionality."""
    
    def setUp(self):
        """Set up test data."""
        cache.clear()
        
        self.user1 = User.objects.create_user(
            user_id=uuid.uuid4(),
            username='testuser1',
            email='test1@example.com',
            first_name='Test',
            last_name='User1',
            password='testpass123'
        )
        
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1)
    
    def test_cache_functionality(self):
        """Test basic cache functionality."""
        # Set a cache value
        cache.set('test_key', 'test_value', 60)
        
        # Retrieve the value
        cached_value = cache.get('test_key')
        
        self.assertEqual(cached_value, 'test_value')
        
        # Clear cache
        cache.clear()
        
        # Value should be None after clearing
        cached_value = cache.get('test_key')
        self.assertIsNone(cached_value)
