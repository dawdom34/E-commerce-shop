from django import forms
from .models import FeedbackModel


class FeedbackForm(forms.ModelForm):
    subject = forms.CharField(max_length=255)
    message = forms.TextInput()

    class Meta:
        model = FeedbackModel
        fields = ['subject', 'message']
