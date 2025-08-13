from rest_framework import serializers
from .models import User, Message, Conversation


class UserSerializers(serializers.ModelSerializer):
    # Explicity use CharField for the username
    username = serializers.CharField(read_only=True)


    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    # Use serializerMethodField for sender details
    sender = serializers.SerializerMethodField()


    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at']

    def get_sender(self, obj):
        '''
        Return a string combining the sender's first and last names.
        '''
        return f"{obj.sender.first_name} {obj.sender.last_name}"


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializers(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    # Field to calculate participant count
    participant_count = serializers.SerializerMethodField()


    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']

    def get_participant_count(self, obj):
        '''
        Return the count of participants in the conversation.
        '''
        return obj.participants.count()

    def validate(self, data):
        '''
        Validate the number of participants in the conversation.
        '''
        if 'participants' in data and len(data['participants']) < 2:
            raise serializers.ValidationError("A conversation must have at least two participants.")
        return data
