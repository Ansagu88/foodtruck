"""
This module contains the view functions for the customer pages.
Views in this module handle the customer profile page and the user's orders.
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import simplejson as json

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from orders.models import Order, OrderedFood


@login_required(login_url='login')
def cprofile(request):
    """
    View function for the customer profile page.

    This view allows authenticated users to update their profile information.
    It handles both GET and POST requests. If the request method is POST,
    it validates the submitted forms and saves the updated profile and user information.
    If the forms are not valid, it prints the form errors.
    If the request method is GET, it initializes the profile and user forms 
    with the current user's data.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - A rendered HTML template with the profile and user forms and the current user's 
    profile information.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile_form': profile_form,
        'user_form' : user_form,
        'profile': profile,
    }
    return render(request, 'customers/cprofile.html', context)


def my_orders(request):
    """
    View function to display the orders made by the current user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template 
        with the user's orders.
    """
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'customers/my_orders.html', context)


def order_detail(request, order_number):
    """
    View function to display the details of a specific order.

    Args:
        request (HttpRequest): The HTTP request object.
        order_number (str): The order number of the order to be displayed.

    Returns:
        HttpResponse: The HTTP response object containing the rendered order detail template.

    Raises:
        Redirect: If the order with the specified order number is not found or is not yet ordered, 
                  the user is redirected to the customer page.
    """
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'customers/order_detail.html', context)
    except:
        return redirect('customer')
    