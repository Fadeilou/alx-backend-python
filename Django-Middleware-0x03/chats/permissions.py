from rest_framework.permissions import BasePermission


class IsAuthenticatedUser(BasePermission):
    '''
    Allow access only to authenticated uers.
    '''
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsParticipant(BasePermission):
    '''
    Custom permission to ensure the user is a participant of the conversationl
    '''
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant of the conversation
        return request.user in obj.participants.all()
