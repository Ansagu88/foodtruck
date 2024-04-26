"""
In this module the views for the accounts app are defined.
Views are used to handle the logic for the user authentication and account management.
We have views for user registration, login, logout, accounts, account activation, dashboards, 
forgot password and password reset.
"""
from datetime import datetime
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import slugify

from vendor.forms import VendorForm
from vendor.models import Vendor

from orders.models import Order

from .forms import UserForm
from .models import User, UserProfile, Subscriber
from .utils import detect_user, send_verification_email


# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    """
    Checks if the user has the role of a vendor.

    Args:
        user (User): The user object to check.

    Returns:
        bool: True if the user has the role of a vendor, False otherwise.

    Raises:
        PermissionDenied: If the user does not have the role of a vendor.
    """
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    """
    Checks if the user has the role of a customer.

    Args:
        user: The user object to check.

    Returns:
        True if the user has the role of a customer.

    Raises:
        PermissionDenied: If the user does not have the role of a customer.
    """
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def register_user(request):
    """
    Register a new user.

    If the user is already authenticated, a warning message is displayed and
      the user is redirected to the dashboard.
    If the request method is POST, the user registration form is validated and 
      a new user is created.
    The user is then sent a verification email and a success message is displayed.
    If the form is invalid, the errors are printed to the console.
    If the request method is not POST, an empty user registration form is displayed.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("dashboard")
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.CUSTOMER
            user.save()

            # Send verification email
            mail_subject = "Please activate your account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, "Your account has been registered sucessfully!")
            messages.success(request, "Please check your Email for activate your account!")
            return redirect("registerUser")
        else:
            print("invalid form")
            print(form.errors)
    else:
        form = UserForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/registerUser.html", context)


def register_vendor(request):
    """
    Register a vendor.

    This function handles the registration process for a vendor. 
    If the user is already authenticated,
    they are redirected to the "myAccount" page. If the request method is POST, 
    the user's registration data is validated and a new user and vendor are created.
     An activation email is sent to the user
    for account verification. If the form is invalid, the errors are printed.
    If the request method is not POST, the registration form and vendor form are initialized.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - If the user is already authenticated, redirects to the "myAccount" page.
    - If the request method is POST and the form is valid, redirects to the "registerVendor" page.
    - If the request method is POST and the form is invalid, prints the form errors.
    - If the request method is not POST, renders the 
    "accounts/registerVendor.html" template with the
      registration form and vendor form.

    """
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("myAccount")
    elif request.method == "POST":
        # store the data and create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid:
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data["vendor_name"]
            vendor.vendor_slug = slugify(vendor_name) + "-" + str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # Send verification email
            mail_subject = "Please activate your account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(
                request,
                "Your account has been registered sucessfully! Please wait for the approval.",
            )
            return redirect("registerVendor")
        else:
            print("invalid form")
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        "form": form,
        "v_form": v_form,
    }

    return render(request, "accounts/registerVendor.html", context)


def activate(request, uidb64, token):
    """
    Activate the user account.

    Args:
        request (HttpRequest): The HTTP request object.
        uidb64 (str): The base64 encoded user ID.
        token (str): The activation token.

    Returns:
        HttpResponseRedirect: Redirects to the "myAccount" page if the user is
        successfully activated, otherwise redirects back to the "myAccount" page with an error 
        message.

    Raises:
        None

    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulation! Your account is activated.")
        return redirect("myAccount")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("myAccount")


def login(request):
    """
    Logs in a user.

    If the user is already authenticated, a warning message is displayed and the user is redirected
    to their account page.
    If the request method is POST, the email and password are extracted 
    from the request's POST data.
    The user is then authenticated using the extracted email and password.
    If the authentication is successful, the user is logged in, a success message is displayed, 
    and the user is redirected to their account page.
    If the authentication fails, an error message is displayed and the user is redirected 
    back to the login page.
    If the request method is not POST, the login page is rendered.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.

    """
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("myAccount")
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("myAccount")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login")
    return render(request, "accounts/login.html")


def logout(request):
    """
    Logs out the user and redirects to the login page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponseRedirect: Redirects to the login page.
    """
    auth.logout(request)
    messages.info(request, "You are logged out.")
    return redirect("login")


@login_required(login_url="login")
def my_account(request):
    """
    View function for the 'myAccount' page.

    This view requires the user to be logged in. If the user is not logged in,
    they will be redirected to the login page. Otherwise, the user's account
    information is retrieved and the appropriate redirect URL is determined
    based on the user's role. The user is then redirected to the determined URL.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: The redirect response to the determined URL.
    """
    user = request.user
    redirecturl = detect_user(user)
    return redirect(redirecturl)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def cust_dashboard(request):
    """
    View function for the customer dashboard.

    This view displays the customer's dashboard, which includes their orders and recent orders.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML template with the customer dashboard.

    """
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders[:5]
    context = {
        "orders": orders,
        "orders_count": orders.count(),
        "recent_orders": recent_orders,
    }
    return render(request, "accounts/custDashboard.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    """
    View function for the vendor dashboard.

    This view displays the vendor's dashboard, which includes information about 
    their orders and revenue.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered vendor dashboard template.
    """
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by(
        "created_at"
    )
    recent_orders = orders[:10]

    # current month's revenue
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(
        vendors__in=[vendor.id], created_at__month=current_month
    )
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()["grand_total"]

    # total revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()["grand_total"]
    context = {
        "orders": orders,
        "orders_count": orders.count(),
        "recent_orders": recent_orders,
        "total_revenue": total_revenue,
        "current_month_revenue": current_month_revenue,
    }
    return render(request, "accounts/vendorDashboard.html", context)


def forgot_password(request):
    """
    View function for handling the forgot password functionality.

    If the request method is POST, it retrieves the email from the request data.
    If a user with the provided email exists, it sends a reset password email to the user.
    Otherwise, it displays an error message indicating that the account does not exist.

    Returns:
        If the request method is POST and a reset password email is sent successfully,
        it redirects the user to the login page after displaying a success message.
        If the account does not exist, it redirects the user back to the forgot password page
        after displaying an error message.
        For any other request method, it renders the forgot password page.

    """
    if request.method == "POST":
        email = request.POST["email"]

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = "Reset Your Password"
            email_template = "accounts/emails/reset_password_email.html"
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(
                request, "Password reset link has been sent to your email address."
            )
            return redirect("login")
        else:
            messages.error(request, "Account does not exist")
            return redirect("forgot_password")
    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    """
    Validates the user's reset password request.

    Args:
        request (HttpRequest): The HTTP request object.
        uidb64 (str): The base64 encoded user ID.
        token (str): The token for password reset.

    Returns:
        HttpResponseRedirect: Redirects to the appropriate page based on the validation result.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.info(request, "Please reset your password")
        return redirect("reset_password")
    else:
        messages.error(request, "This link has expired!")
        return redirect("myAccount")


def reset_password(request):
    """
    Reset the password for a user.

    This function handles the logic for resetting the password of a user. It expects a POST request
    with the new password and confirm password fields. If the passwords match, it updates the user's
    password and sets the user as active. If the passwords do not match, 
    it displays an error message.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            pk = request.session.get("uid")
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Password do not match!")
            return redirect("reset_password")
    return render(request, "accounts/reset_password.html")


def subscribe(request):
    """
    View function to handle subscription requests.

    If the request method is POST, it expects an email parameter in the request.POST data.
    If the email parameter is provided, it creates a new Subscriber object with the email.
    If the email parameter is not provided, it displays an 
    error message and redirects to"subscribe" page.
    After successful registration, it displays a success message and redirects to the "home" page.

    If the request method is not POST, it redirects to the "subscribe" page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            Subscriber.objects.get_or_create(email=email)
            messages.success(request, "Your email was registered successfully!")
            return redirect("home")
        else:
            messages.error(request, "Email is required")
            return redirect("subscribe")
    else:
        return redirect("subscribe")
