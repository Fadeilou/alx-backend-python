from django.shortcuts import render
from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, ConversationCreateSerializer, MessageSerializer, MessageCreateSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from .rest_framework.pagination import PageNumberPagination


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.prefetch_related('participants', 'messages').all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['participants__user_id', 'created_at']
    ordering_fields = ['created_at']

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        '''
        Create a new conversation with specified participants.
        '''
        serliazer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = seiralizer.save()
        return Response(ConversationSerializer(conversation).data, status=status                        .HTTP_201_CREATED)

    def get_queryset(self):
        # Only show conversations where the user is a participant
        return Conversation.objects.filter(participants=self.request.user)


class MessagePagination(PageNumberPagination):
    page_size = 20 # Fetch 20 messages per page



class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related('conversation', 'sender').all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sender__user_id', 'send_at']
    ordering_fields = ['sent_at']

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def list(self, request, *args, **kwargs):
        '''
        List messages for a specific conversation.
        '''
        conversation_id = self.kwargs.get('conversation_pk')
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        '''
        Send a new message to an existing conversation.
        '''
        conversation_id = self.kwargs.get('conversation_pk')
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user, conversation=conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_query_set(self):
        # Only show messages in conversations the user participates in
        return Message.objects.filter(conversation_participants=self.request.user)

    def perform_create(self, serializer):
        '''
        Ensure the user is a participant of the conversation when
        sending a message
        '''
        conversation = serializer.validated_data['conversation']
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a participant of this conversation.")
        serializer.save(sender=self.request.user)
