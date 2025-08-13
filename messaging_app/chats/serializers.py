from rest_framework import serializers
from .models import User, Message, Conversation, ConversationParticipant


class UserSerializers(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)


    class Meta:
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'created_at'
        ]

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializers(read_only=True)


    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender', 
            'conversation',
            'message_body',
            'sent_at'
        ]


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()


    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'messages',
            'created_at'
        ]

    def get_participants(self, obj):
        participants = obj.participants_info.all().select_related('user')
        return UserSerializer([p.user for p in participants], many=True).data

    def get_messages(self, obj):
        messages = obj.messages.all().select_related('sender')
        return MessageSerializer(messages, many=True).data

    def validate(self, data):
        participants = self.initial_data.get('participants', [])
        if len(participants) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants")
        return data
