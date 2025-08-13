import django_filters
from .models import Message, Conversation

class MessageFilter(django_filters.FilterSet):
    # Filter by messages within a time range
    sent_at_after = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr='gte')
    sent_at_before = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr='lte')

    # Filter by conversation participants (assuming 'user' is a field in ConversationParticipant)
    # This might need adjustment based on the actual model structure
    conversation__participants__user = django_filters.CharFilter(
        field_name="conversation__participants__user__user_id",
        lookup_expr='exact',
        help_text="Filter by user ID of a participant in the conversation."
    )

    class Meta:
        model = Message
        fields = ['sent_at_after', 'sent_at_before', 'conversation__participants__user']