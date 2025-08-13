from django.db import models


class UnreadMessagesManager(models.Manager):
    '''
    custom manager to filter unread messages for a specific user.
    '''
    def for_user(self, user):
        '''
        Returns unread messages for the given user.
        '''
        return self.filter(receiver=user, read=False).only("id", "content", "timestamp", "sender")
