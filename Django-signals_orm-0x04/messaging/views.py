from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now
from .models import Message
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def edit_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id)

    if request.method == "POST":
        new_content = request.POST.get("content")
        if new_content and new_content != message.content:
            message.content = new_content
            message.edited_by = request.user # Track the user who made the edit
            message.edited_at = now() # Update the edit timestamp
            message.save()
        
        return redirect("view_message", message_id=message_id)
    return render(request, "edit_messasge.html", {"message": message})


@login_required
def delete_user(request):
    '''
    Deletes the currently logged-in user's account and cleans up related data.
    '''
    user = request.user
    user.delete() # Triggers the post_delete signal
    return redirect("home") # Redirect to the homepage after deletion


def conversation_view(request):
    '''
    Display messages in a threaded conversation format.
    '''
    # Retrieve all root messages(parent_message=None) and their replies
    messages = Message.objects.filter(parent_message=None).select_related(
        "sender", "receiver"
    ).prefetch_related("replies__sender", "replies__receiver")

    return render(request,"conversation.html", {"messages": messages})


@login_required
def user_conversation_view(request):
    '''
    Display the conversation for the logged-in user, including messages they sent and replies, optimized with select_related and prefetch_related.
    '''
    # Filter messages by the logged-in user as the sender
    messages = Message.objects.filter(sender=request.user, parent_message=None).select_related(
        "receiver"
    ).prefetch_related(
        "replies__sender", # Prefetch sender details of replies
        "replies__receiver" # Prefetch receiver details of replies
    )

    return render(request, "user_converstation.html", {"messages": messages})


@login_required
def unread_messages_view(request):
    '''
    Displays unread messages for the logged-in user.
    '''
    unread_messages = Message.unread.unread_for_user(request.user) # Use cutom manager
    # Use the custom manager to filter unread messages and explicitly apply .only()
    unread_messages = Message.unread.filter(receiver=request.user, read=False).only("id", "content", "timestamp", "sender")

    return render(request, "unread_messages.html", {"unread_messages": unread_messages})


@login_required
@cache_page(60) # Cache the view for 60 seconds
def conversation_view(request, conversation_id):
    '''
    Displays a list of messages in a conversatioin
    '''
    messages = Message.objects.filter(conversation_id=conversation_id).order_by("timestamp")
    return render(request, "conversation.html", {"messages": messages})
