from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django.utils.timezone import now


class MessagingTestCase(TestCase):
    def setuUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")

    def test_notification_creation(self):
        message = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hello!")
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.read)


class MessageEditTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")
        self.message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Initial content"
        )

    def test_message_edit_logs_history(self):
        # Update message content
        self.message.content = "Edited content"
        self.message.edited_by = self.user1
        self.message.edited_at = now()
        self.message.save()

        # Check if history is created
        history = MessageHistory.objects.filter(message=self.message)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().old_content, "Initial content")
        self.assertTrue(self.message.edited)
        self.assertIsNotNone(self.message.edited_at)
        self.assertEqual(self.message.edited_by, self.user1)


class DeleteUserTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")
        self.message = Message.objects.create(sender=self.user1, receiver=self.user2, content="Test message")
        self.notification = Notification.objects.create(user=self.user2, message=self.message)

    def test_user_deletion_cleans_up_related_data(self):
        # Verify initial counts
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 1)

        # Delete user1 and check cleanup
        self.user1.delete()
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(Notification.objects.count(), 0)


class ThreadedConversationTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")

        # Create root message
        self.root_message = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        # Create replies
        self.reply1 = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="First reply", parent_message=self.root_message
        )
        self.reply2 = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Second reply", parent_message=self.root_message
        )
        self.sub_reply = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Sub-reply", parent_message=self.reply1
        )

    def test_threaded_conversation(self):
        # Test recursive retrieval of all replies
        replies = self.root_message.get_all_replies()
        self.assertEqual(len(replies), 3)  # All replies, including sub-replies

        # Test prefetching and select_related
        with self.assertNumQueries(2):  # Ensure query optimization
            messages = Message.objects.filter(parent_message=None).select_related(
                "sender", "receiver"
            ).prefetch_related("replies__sender", "replies__receiver")
            list(messages)  # Trigger evaluation


class UnreadMessagesManagerTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")

        # Create messages
        Message.objects.create(sender=self.user2, receiver=self.user1, content="Unread message 1", read=False)
        Message.objects.create(sender=self.user2, receiver=self.user1, content="Unread message 2", read=False)
        Message.objects.create(sender=self.user2, receiver=self.user1, content="Read message", read=True)

    def test_unread_messages_for_user(self):
        unread_messages = Message.unread.for_user(self.user1)
        self.assertEqual(unread_messages.count(), 2)  # Only 2 unread messages
        self.assertTrue(all(message.read is False for message in unread_messages))


from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Message

class ConversationCacheTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="password")
        self.client.login(username="user", password="password")
        self.conversation_id = 1

        # Create messages
        Message.objects.create(sender=self.user, receiver=self.user, content="Message 1", conversation_id=self.conversation_id)
        Message.objects.create(sender=self.user, receiver=self.user, content="Message 2", conversation_id=self.conversation_id)

    def test_cache_view(self):
        url = reverse("conversation_view", args=[self.conversation_id])

        # First request (not cached)
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)

        # Modify database (should not affect cached response)
        Message.objects.create(sender=self.user, receiver=self.user, content="Message 3", conversation_id=self.conversation_id)

        # Second request (cached)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response1.content, response2.content)  # Response should match due to cache
