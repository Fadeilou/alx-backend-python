from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.db import models
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, 
    ConversationListSerializer,
    MessageSerializer, 
    UserSerializer
)
from .permissions import IsParticipantOfConversation, IsAuthenticatedParticipant, CanCreateMessage
from .filters import MessageFilter, ConversationFilter, UserFilter
from .pagination import MessagePagination, ConversationPagination, UserPagination

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing and retrieving users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'created_at']
    ordering = ['username']
    pagination_class = UserPagination


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversations."""
    permission_classes = [IsParticipantOfConversation]
    lookup_field = 'conversation_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['participants__username', 'participants__email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    pagination_class = ConversationPagination
    
    def get_queryset(self):
        """Return conversations for the current user."""
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new conversation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Add the current user to participants if not already included
        participant_ids = request.data.get('participant_ids', [])
        if str(request.user.user_id) not in [str(pid) for pid in participant_ids]:
            participant_ids.append(str(request.user.user_id))
        
        # Check if conversation already exists with these participants
        if len(participant_ids) == 2:
            existing_conversation = Conversation.objects.filter(
                participants__user_id__in=participant_ids
            ).annotate(
                participant_count=models.Count('participants')
            ).filter(participant_count=2)
            
            for conv in existing_conversation:
                if set(conv.participants.values_list('user_id', flat=True)) == set(participant_ids):
                    return Response(
                        ConversationSerializer(conv).data,
                        status=status.HTTP_200_OK
                    )
        
        # Create new conversation
        validated_data = serializer.validated_data.copy()
        validated_data['participant_ids'] = participant_ids
        conversation = serializer.create(validated_data)
        
        return Response(
            ConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """Add a participant to the conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response(
                {'message': f'User {user.email} added to conversation'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, conversation_id=None):
        """Remove a participant from the conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(user_id=user_id)
            if user == request.user:
                return Response(
                    {'error': 'Cannot remove yourself from conversation'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            conversation.participants.remove(user)
            return Response(
                {'message': f'User {user.email} removed from conversation'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages."""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedParticipant]
    lookup_field = 'message_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body', 'sender__username', 'sender__email']
    ordering_fields = ['sent_at', 'message_body']
    ordering = ['-sent_at']
    pagination_class = MessagePagination
    
    def get_queryset(self):
        """Return messages for conversations the user participates in."""
        user_conversations = Conversation.objects.filter(
            participants=self.request.user
        )
        return Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation')
    
    def create(self, request, *args, **kwargs):
        """Create a new message."""
        # Automatically set the sender to the current user
        data = request.data.copy()
        data['sender_id'] = str(request.user.user_id)
        
        # Validate that the user is a participant in the conversation
        conversation_id = data.get('conversation')
        if conversation_id:
            try:
                conversation = Conversation.objects.get(
                    conversation_id=conversation_id,
                    participants=request.user
                )
            except Conversation.DoesNotExist:
                return Response(
                    {'error': 'You are not a participant in this conversation'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        
        # Update conversation's updated_at timestamp
        conversation.save()
        
        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        """Get messages for a specific conversation."""
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response(
                {'error': 'conversation_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(
                conversation_id=conversation_id,
                participants=request.user
            )
            messages = self.get_queryset().filter(conversation=conversation)
            page = self.paginate_queryset(messages)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found or you are not a participant'},
                status=status.HTTP_404_NOT_FOUND
            )
