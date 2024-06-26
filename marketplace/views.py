"""
In this module we created the views for the marketplace app.
Views like marketplace, vendor_detail, add_to_cart, decrease_cart, cart, 
delete_cart, search, and checkout are created.

"""
from datetime import date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Prefetch
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance

from vendor.models import OpeningHour, Vendor
from menu.models import Category, FoodItem
from accounts.models import UserProfile
from orders.forms import OrderForm

from .models import Cart
from .context_processors import get_cart_counter, get_cart_amounts


def marketplace(request):
    """
    View function for the marketplace page.

    This function retrieves a list of approved vendors from the database and renders
    the 'listings.html' template with the vendor data.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.
    """
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        "vendors": vendors,
        "vendor_count": vendor_count,
    }
    return render(request, "marketplace/listings.html", context)


def vendor_detail(request, vendor_slug):
    """
    View function that displays the details of a vendor.

    Args:
        request (HttpRequest): The HTTP request object.
        vendor_slug (str): The slug of the vendor.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    Raises:
        Http404: If the vendor with the specified slug does not exist.
    """
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch("fooditems", queryset=FoodItem.objects.filter(is_available=True))
    )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by(
        "day", "from_hour"
    )

    # Check current day's opening hours.
    today_date = date.today()
    today = today_date.isoweekday()

    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        "vendor": vendor,
        "categories": categories,
        "cart_items": cart_items,
        "opening_hours": opening_hours,
        "current_opening_hours": current_opening_hours,
    }
    return render(request, "marketplace/vendor_detail.html", context)


def add_to_cart(request, food_id):
    """
    Add a food item to the user's cart.

    Args:
        request (HttpRequest): The HTTP request object.
        food_id (int): The ID of the food item to be added to the cart.

    Returns:
        JsonResponse: A JSON response containing the status of 
        the operation and additional information.

    Raises:
        None

    """
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chk_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the cart quantity
                    chk_cart.quantity += 1
                    chk_cart.save()
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Increased the cart quantity",
                            "cart_counter": get_cart_counter(request),
                            "qty": chk_cart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
                except:
                    chk_cart = Cart.objects.create(
                        user=request.user, fooditem=fooditem, quantity=1
                    )
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Added the food to the cart",
                            "cart_counter": get_cart_counter(request),
                            "qty": chk_cart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
            except:
                return JsonResponse(
                    {"status": "Failed", "message": "This food does not exist!"}
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid request!"})

    else:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue"}
        )


def decrease_cart(request, food_id):
    """
    Decreases the quantity of a food item in the user's cart.

    Args:
        request (HttpRequest): The HTTP request object.
        food_id (int): The ID of the food item to decrease the quantity for.

    Returns:
        JsonResponse: A JSON response containing the status of 
        the operation and additional information.

    Raises:
        None
    """
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chk_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chk_cart.quantity > 1:
                        # decrease the cart quantity
                        chk_cart.quantity -= 1
                        chk_cart.save()
                    else:
                        chk_cart.delete()
                        chk_cart.quantity = 0
                    return JsonResponse(
                        {
                            "status": "Success",
                            "cart_counter": get_cart_counter(request),
                            "qty": chk_cart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
                except:
                    return JsonResponse(
                        {
                            "status": "Failed",
                            "message": "You do not have this item in your cart!",
                        }
                    )
            except:
                return JsonResponse(
                    {"status": "Failed", "message": "This food does not exist!"}
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid request!"})

    else:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue"}
        )


@login_required(login_url="login")
def cart(request):
    """
    View function for the cart page.

    Retrieves the cart items for the logged-in user and renders the cart.html template.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML response containing the cart items.

    """
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    context = {
        "cart_items": cart_items,
    }
    return render(request, "marketplace/cart.html", context)


def delete_cart(request, cart_id):
    """
    Deletes a cart item for the authenticated user.

    Args:
        request (HttpRequest): The HTTP request object.
        cart_id (int): The ID of the cart item to be deleted.

    Returns:
        JsonResponse: A JSON response indicating the status of the deletion operation.
            If the deletion is successful, the response will contain the following keys:
                - "status": "Success"
                - "message": "Cart item has been deleted!"
                - "cart_counter": The updated cart counter for the user
                - "cart_amount": The updated cart amount for the user
            If the cart item does not exist, the response will contain the following keys:
                - "status": "Failed"
                - "message": "Cart Item does not exist!"
            If the request is invalid, the response will contain the following keys:
                - "status": "Failed"
                - "message": "Invalid request!"
    """
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            try:
                # Check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Cart item has been deleted!",
                            "cart_counter": get_cart_counter(request),
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
            except:
                return JsonResponse(
                    {"status": "Failed", "message": "Cart Item does not exist!"}
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid request!"})


def search(request):
    """
    Search for vendors based on user's search criteria.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the search results.

    Raises:
        None

    """
    if not "address" in request.GET:
        return redirect("marketplace")
    else:
        address = request.GET["address"]
        latitude = request.GET["lat"]
        longitude = request.GET["lng"]
        radius = request.GET["radius"]
        keyword = request.GET["keyword"]

        # get vendor ids that has the food item the user is looking for
        fetch_vendors_by_fooditems = FoodItem.objects.filter(
            food_title__icontains=keyword, is_available=True
        ).values_list("vendor", flat=True)

        vendors = Vendor.objects.filter(
            Q(id__in=fetch_vendors_by_fooditems)
            | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)
        )
        if latitude and longitude and radius:
            pnt = GEOSGeometry("POINT(%s %s)" % (longitude, latitude))

            vendors = (
                Vendor.objects.filter(
                    Q(id__in=fetch_vendors_by_fooditems)
                    | Q(
                        vendor_name__icontains=keyword,
                        is_approved=True,
                        user__is_active=True,
                    ),
                    user_profile__location__distance_lte=(pnt, D(km=radius)),
                )
                .annotate(distance=Distance("user_profile__location", pnt))
                .order_by("distance")
            )

            for v in vendors:
                v.kms = round(v.distance.km, 1)
        vendor_count = vendors.count()
        context = {
            "vendors": vendors,
            "vendor_count": vendor_count,
            "source_location": address,
        }

        return render(request, "marketplace/listings.html", context)


@login_required(login_url="login")
def checkout(request):
    """
    Renders the checkout page with the order form and cart items.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered checkout page.

    Raises:
        None
    """
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("marketplace")

    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "phone": request.user.phone_number,
        "email": request.user.email,
        "address": user_profile.address,
        "country": user_profile.country,
        "state": user_profile.state,
        "city": user_profile.city,
        "pin_code": user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    context = {
        "form": form,
        "cart_items": cart_items,
    }
    return render(request, "marketplace/checkout.html", context)
