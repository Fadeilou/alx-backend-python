from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'date_of_birth', 'created_at']
        read_only_fields = ['user_id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model with sender details."""
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'sender_id', 'conversation', 
                 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']
    
    def create(self, validated_data):
        # Remove sender_id from validated_data and use it to set sender
        sender_id = validated_data.pop('sender_id')
        try:
            sender = User.objects.get(user_id=sender_id)
            validated_data['sender'] = sender
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid sender_id")
        
        return super().create(validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with participants and messages."""
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'participant_ids', 
                 'messages', 'last_message', 'created_at', 'updated_at']
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """Get the most recent message in the conversation."""
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = super().create(validated_data)
        
        # Add participants to the conversation
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
        
        return conversation


class ConversationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing conversations."""
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'last_message', 
                 'message_count', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """Get the most recent message in the conversation."""
        last_message = obj.messages.last()
        if last_message:
            return {
                'message_body': last_message.message_body,
                'sender': last_message.sender.first_name + ' ' + last_message.sender.last_name,
                'sent_at': last_message.sent_at
            }
        return None
    
    def get_message_count(self, obj):
        """Get the total number of messages in the conversation."""
        return obj.messages.count()
