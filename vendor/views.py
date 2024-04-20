"""
Here we define the views for the vendor app.

"""

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify

from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from orders.models import Order, OrderedFood
from accounts.forms import UserProfileForm
from accounts.views import check_role_vendor
from accounts.models import UserProfile

from .models import OpeningHour, Vendor
from .forms import VendorForm, OpeningHourForm


def get_vendor(request):
    """
    Retrieve the vendor associated with the given user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Vendor: The vendor object associated with the user.

    Raises:
        Vendor.DoesNotExist: If no vendor is found for the user.
    """
    vendor = Vendor.objects.get(user=request.user)
    return vendor


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vprofile(request):
    """
    View function for the vendor profile page.

    This view allows a vendor to update their profile settings.
    It requires the user to be logged in and have the role of a vendor.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    Raises:
        Http404: If the UserProfile or Vendor objects are not found.

    """
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Settings updated.")
            return redirect("vprofile")
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        "profile_form": profile_form,
        "vendor_form": vendor_form,
        "profile": profile,
        "vendor": vendor,
    }

    return render(request, "vendor/vprofile.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def menu_builder(request):
    """
    View function for the menu builder page.

    This view displays the menu builder page for a vendor. 
    It requires the user to be logged in and have the role of a vendor.
    The function retrieves the vendor object associated with the request, 
    fetches the categories belonging to the vendor, and orders them by creation date.
    The categories are then passed to the template context and 
    rendered with the 'vendor/menu_builder.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.
    """
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by("created_at")
    context = {
        "categories": categories,
    }
    return render(request, "vendor/menu_builder.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    """
    View function to display food items by category for a vendor.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int, optional): The primary key of the category. Defaults to None.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.
    """
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        "fooditems": fooditems,
        "category": category,
    }
    return render(request, "vendor/fooditems_by_category.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_category(request):
    """
    View function for adding a category.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        None
    """
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data["category_name"]
            category = form.save(commit=False)
            category.vendor = get_vendor(request)

            category.save()  # here the category id will be generated
            category.slug = (
                slugify(category_name) + "-" + str(category.id)
            )  # chicken-15
            category.save()
            messages.success(request, "Category added successfully!")
            return redirect("menu_builder")
        else:
            print(form.errors)

    else:
        form = CategoryForm()
    context = {
        "form": form,
    }
    return render(request, "vendor/add_category.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    """
    Edit a category.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int, optional): The primary key of the category to be edited. Defaults to None.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        Http404: If the category with the specified primary key does not exist.
    """
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data["category_name"]
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("menu_builder")
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
        "form": form,
        "category": category,
    }
    return render(request, "vendor/edit_category.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    """
    Deletes a category from the database.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int, optional): The primary key of the category to be deleted. Defaults to None.

    Returns:
        HttpResponseRedirect: A redirect response to the menu_builder view.

    Raises:
        Http404: If the category with the given primary key does not exist.
    """
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category has been deleted successfully!")
    return redirect("menu_builder")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_food(request):
    """
    View function for adding a food item.

    This view function handles the logic for adding a new food item to the system.
    It requires the user to be logged in and have the role of a vendor.
    The function handles both GET and POST requests.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - If the request method is POST and the form is valid, the function saves 
    the food item and redirects to the food items list page filtered by category.
    - If the request method is GET, the function renders the add food 
    form with the category field filtered by the vendor.

    """
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data["food_title"]
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, "Food Item added successfully!")
            return redirect("fooditems_by_category", food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # modify this form
        form.fields["category"].queryset = Category.objects.filter(
            vendor=get_vendor(request)
        )
    context = {
        "form": form,
    }
    return render(request, "vendor/add_food.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    """
    Edit a food item.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int, optional): The primary key of the food item to be edited. Defaults to None.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        Http404: If the food item with the given primary key does not exist.

    """
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data["food_title"]
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, "Food Item updated successfully!")
            return redirect("fooditems_by_category", food.category.id)
        else:
            print(form.errors)

    else:
        form = FoodItemForm(instance=food)
        form.fields["category"].queryset = Category.objects.filter(
            vendor=get_vendor(request)
        )
    context = {
        "form": form,
        "food": food,
    }
    return render(request, "vendor/edit_food.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    """
    Deletes a food item.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int, optional): The primary key of the food item to be deleted. Defaults to None.

    Returns:
        HttpResponseRedirect: Redirects to the food items page filtered by category.

    Raises:
        Http404: If the food item with the given primary key does not exist.
    """
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, "Food Item has been deleted successfully!")
    return redirect("fooditems_by_category", food.category.id)


def opening_hours(request):
    """
    View function to display and handle opening hours for a vendor.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    """
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        "form": form,
        "opening_hours": opening_hours,
    }
    return render(request, "vendor/opening_hours.html", context)


def add_opening_hours(request):
    """
    Add opening hours for a vendor.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the status and relevant data.

    Raises:
        IntegrityError: If the opening hour already exists for the specified day.

    """
    # handle the data and save them inside the database
    if request.user.is_authenticated:
        if (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            and request.method == "POST"
        ):
            day = request.POST.get("day")
            from_hour = request.POST.get("from_hour")
            to_hour = request.POST.get("to_hour")
            is_closed = request.POST.get("is_closed")

            try:
                hour = OpeningHour.objects.create(
                    vendor=get_vendor(request),
                    day=day,
                    from_hour=from_hour,
                    to_hour=to_hour,
                    is_closed=is_closed,
                )
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {
                            "status": "success",
                            "id": hour.id,
                            "day": day.get_day_display(),
                            "is_closed": "Closed",
                        }
                    else:
                        response = {
                            "status": "success",
                            "id": hour.id,
                            "day": day.get_day_display(),
                            "from_hour": hour.from_hour,
                            "to_hour": hour.to_hour,
                        }
                return JsonResponse(response)
            except IntegrityError as e:
                response = {
                    "status": "failed",
                    "message": from_hour
                    + "-"
                    + to_hour
                    + " already exists for this day!",
                }
                return JsonResponse(response)
        else:
            HttpResponse("Invalid request")


def remove_opening_hours(request, pk=None):
    """
    Remove the opening hours for a specific vendor.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int, optional): The primary key of the opening hour to be removed. Defaults to None.

    Returns:
        JsonResponse: A JSON response indicating the status of the 
        operation and the ID of the removed opening hour.
    """
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({"status": "success", "id": pk})


def order_detail(request, order_number):
    """
    View function to display the details of an order.

    Args:
        request (HttpRequest): The HTTP request object.
        order_number (str): The order number of the order to be displayed.

    Returns:
        HttpResponse: The HTTP response object containing the rendered order detail template.

    Raises:
        Redirect: If the order does not exist or is not yet confirmed, redirects to the vendor page.
    """
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(
            order=order, fooditem__vendor=get_vendor(request)
        )

        context = {
            "order": order,
            "ordered_food": ordered_food,
            "subtotal": order.get_total_by_vendor()["subtotal"],
            "tax_data": order.get_total_by_vendor()["tax_dict"],
            "grand_total": order.get_total_by_vendor()["grand_total"],
        }
    except:
        return redirect("vendor")
    return render(request, "vendor/order_detail.html", context)


def my_orders(request):
    """
    View function to display the orders associated with the current vendor.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template with the orders.

    Raises:
        Vendor.DoesNotExist: If the vendor associated with the current user does not exist.

    """
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by(
        "created_at"
    )

    context = {
        "orders": orders,
    }
    return render(request, "vendor/my_orders.html", context)
