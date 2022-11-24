from django.urls import path
from .views import add_feedback, mark_as_complete, feedback_details

app_name = 'feedback'

urlpatterns = [
    # Send feedback message
    path('send/', add_feedback, name='send'),
    # Feedback message details
    path('feedback/details/<int:message_id>/', feedback_details, name='details'),
    # Mark feedback message as complete
    path('feedback/mark_as_complete/', mark_as_complete, name='mark_as_complete'),
]
