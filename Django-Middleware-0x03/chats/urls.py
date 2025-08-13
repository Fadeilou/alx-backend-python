from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ConversationViewSet, MessageViewSet
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from . import views


# Initialize the router
router = routers.DefaultRouter()

# Register the viewsets
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')


conversation_router = nested_routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversation_router.register(r'messages', views.MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(conversation_router.urls)),
]
