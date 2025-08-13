from django_filters import rest_framework as filters
from .models import Message
import django_filters

class MessageFilter(filters.FilterSet):
    sent_after = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_before = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    sender = django_filters.UUIDFilter(field_name='sender__user_id')

    class Meta:
        model = Message
        fields = []
