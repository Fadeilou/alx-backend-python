from django.urls import path
from . import views

urlpatterns = [
    path("delete_user/", views.delete_user, name="delete_user"),
    path("unread_messages/", views.unread_messages_view, name="unread_messages")
]
