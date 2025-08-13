from rest_framework import permissions
from .models import ConversationParticipant

class IsOwnerOrParticipant(permissions.BasePermission):
    """User can only access their own messages or conversations they participate in"""
    
    def has_object_permission(self, request, view, obj):
        # For messages
        if hasattr(obj, 'sender'):
            return obj.sender == request.user
        
        # For conversations
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        return False


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow conversation participants to interact with messages
    and conversation details
    """

    def has_permission(self, request, view):
        # Allow only authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For messages - check if user is in conversation participants
        if hasattr(obj, 'conversation'):
            return ConversationParticipant.objects.filter(
                conversation=obj.conversation,
                user=request.user
            ).exists() and request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

        # For conversations directly
        if isinstance(obj, Conversation):
            return ConversationParticipant.objects.filter(
                conversation=obj,
                user=request.user
            ).exists() and request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

        return False
