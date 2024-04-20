"""
This module contains custom context processors for the marketplace app.
We created two custom context processors:
    - get_cart_counter: Returns the number of items in the user's cart.
    - get_cart_amounts: Calculate the subtotal, tax, and grand total for the user's cart.
"""

from menu.models import FoodItem
from .models import Cart, Tax


def get_cart_counter(request):
    """
    Returns the number of items in the user's cart.

    Args:
        request (HttpRequest): The current HTTP request object.

    Returns:
        dict: A dictionary containing the cart count.

    """
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    return {"cart_count": cart_count}


def get_cart_amounts(request):
    """
    Calculate the subtotal, tax, and grand total for the user's cart.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: A dictionary containing the following keys:
            - "subtotal" (float): The total price of all items in the cart.
            - "tax" (float): The calculated tax amount.
            - "grand_total" (float): The total price including tax.
            - "tax_dict" (dict): A dictionary containing tax types as keys and 
            their corresponding tax percentages and amounts as values.
    """
    subtotal = 0
    tax = 0
    grand_total = 0
    tax_dict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal += (
                fooditem.price * item.quantity
            )  # subtotal = subtotal + (fooditem.price * item.quantity)

        get_tax = Tax.objects.filter(is_active=True)
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal) / 100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

        tax = sum(x for key in tax_dict.values() for x in key.values())
        grand_total = subtotal + tax
    return {
        "subtotal": subtotal,
        "tax": tax,
        "grand_total": grand_total,
        "tax_dict": tax_dict,
    }
