from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ConversationViewSet, MessageViewSet
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter

# Initialize the router and register the viewsets
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')


# Create nested router for messages
messages_router = NestedDefaultRouter(
    router, r'conversations', lookup='conversation'
)
messages_router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(messages_router.urls)),
]
