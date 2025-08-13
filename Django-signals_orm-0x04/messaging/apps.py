from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'


    def ready(self):
        import messaging.signals


class DjangoChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "DjangoChat"

    def ready(self):
        import DjangoChat.signals # Register the signals
