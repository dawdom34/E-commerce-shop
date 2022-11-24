from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json

from account.models import Cart

from .forms import FeedbackForm
from .models import FeedbackModel


@login_required(login_url='login')
def add_feedback(request):
    """
    Send a feedback message
    """
    user = request.user
    context = {}

    if request.method == 'GET':
        # Number of products in cart
        cart = Cart.objects.get(user=user, transaction_completed=False)
        counter = sum([product.quantity for product in cart.products.all()])

        # Define form
        form = FeedbackForm()
        context['form'] = form
        context['c'] = counter
    elif request.method == 'POST':
        form = FeedbackForm(request.POST)
        # Number of products in cart
        cart = Cart.objects.get(user=user, transaction_completed=False)
        counter = sum([product.quantity for product in cart.products.all()])
        if form.is_valid():
            n = form.save(commit=False)
            n.user = user
            n.save()
            return redirect('shop:home')
        context['form'] = form
        context['c'] = counter
    return render(request, 'feedback/feedback.html', context)


@login_required(login_url='login')
def feedback_details(request, *args, **kwargs):
    """
    View details about feedback message
    """
    context = {}
    user = request.user
    if user.is_staff:
        message_id = kwargs.get('message_id')
        try:
            message = FeedbackModel.objects.get(id=message_id)
        except FeedbackModel.DoesNotExist:
            return HttpResponse('Feedback object does not exist.')
        context['message'] = message
    return render(request, 'feedback/feedback_details.html', context)


@login_required(login_url='login')
def mark_as_complete(request):
    """
    Mark feedback message as complete
    """
    user = request.user
    payload = {}
    if user.is_staff and request.method == 'POST':
        # Get message id from request
        message_id = request.POST.get('message_id')
        # Check if message exist and mark as complete
        try:
            message = FeedbackModel.objects.get(id=message_id)
            message.mark_as_complete()
            payload['response'] = 'Success.'
        except FeedbackModel.DoesNotExist:
            payload['response'] = 'Feedback message does not exist.'
    else:
        payload['response'] = 'Access denied'
    return HttpResponse(json.dumps(payload))
