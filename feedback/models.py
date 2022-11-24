from django.db import models
from account.models import Account


class FeedbackModel(models.Model):

    SUBJECT_CHOICES = (
        ('Issue', 'Issue'),
        ('Question', 'Question'),
        ('Feedback', 'Feedback')
    )

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, choices=SUBJECT_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def mark_as_complete(self):
        # Mark current message as complete
        self.is_active = False
        self.save()
