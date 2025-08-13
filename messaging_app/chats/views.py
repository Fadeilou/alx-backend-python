from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User, Conversation, Message, ConversationParticipant
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsOwnerOrParticipant
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import MessageFilter
import django_filters.rest_framework


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    http_method_names = ['get', 'post']  # Only allow list and create
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def permission_denied(self, request, message=None):
        return Response({"detail": message or "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        # Get conversations where the current user is a participant
        return self.request.user.conversations.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()

        # Add participants from request and current user
        participant_ids = set(request.data.get('participants', []))
        participant_ids.add(str(request.user.user_id))

        # Create conversation participants
        for user_id in participant_ids:
            user = get_object_or_404(User, user_id=user_id)
            ConversationParticipant.objects.get_or_create(
                conversation=conversation,
                user=user
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    http_method_names = ['get', 'post']  # Only allow list and create
    ordering = ['sent_at']
    ordering_fields = ['sent_at']
    filter_backends = [filters.OrderingFilter, django_filters.rest_framework.DjangoFilterBackend]
    pagination_class = MessagePagination
    filterset_class = MessageFilter

    def permission_denied(self, request, message=None):
        return Response({"detail": message or "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        return Message.objects.filter(
            conversation__conversation_id=self.kwargs['conversation_id']
        )

    def perform_create(self, serializer):
        # Automatically set sender and conversation
        conversation = get_object_or_404(
            Conversation,
            conversation_id=self.kwargs['conversation_id']
        )
        serializer.save(
            sender=self.request.user,
            conversation=conversation
        )
