""""
In this models module we have the following classes:
- Payment: Represents a payment made by a user for an order.
- Order: Represents an order placed by a customer.
- OrderedFood: Represents an ordered food item.
this classes are used to store the payment, order and ordered food 
details in the database.

"""
import json
from django.db import models
from accounts.models import User
from menu.models import FoodItem
from vendor.models import Vendor


request_object = ""


class Payment(models.Model):
    """
    Represents a payment made by a user for an order.

    Attributes:
        user (User): The user who made the payment.
        transaction_id (str): The unique identifier for the payment transaction.
        payment_method (str): The method used for the payment (e.g., PayPal).
        amount (str): The amount of the payment.
        status (str): The status of the payment.
        created_at (datetime): The date and time when the payment was created.
    """

    PAYMENT_METHOD = (
        ("PayPal", "PayPal"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id


class Order(models.Model):
    """
    Represents an order placed by a customer.

    Attributes:
        user (ForeignKey): The user who placed the order.
        payment (ForeignKey): The payment associated with the order.
        vendors (ManyToManyField): The vendors involved in fulfilling the order.
        order_number (CharField): The unique identifier for the order.
        first_name (CharField): The first name of the customer.
        last_name (CharField): The last name of the customer.
        phone (CharField): The phone number of the customer.
        email (EmailField): The email address of the customer.
        address (CharField): The address for delivery.
        country (CharField): The country for delivery.
        state (CharField): The state for delivery.
        city (CharField): The city for delivery.
        pin_code (CharField): The PIN code for delivery.
        total (FloatField): The total amount of the order.
        tax_data (JSONField): The tax data associated with the order.
        total_data (JSONField): The total data associated with the order.
        total_tax (FloatField): The total tax amount for the order.
        payment_method (CharField): The payment method used for the order.
        status (CharField): The status of the order.
        is_ordered (BooleanField): Indicates if the order has been placed.
        created_at (DateTimeField): The date and time when the order was created.
        updated_at (DateTimeField): The date and time when the order was last updated.
    """

    STATUS = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    vendors = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)
    total = models.FloatField()
    tax_data = models.JSONField(
        blank=True,
        help_text="Data format: {'tax_type':{'tax_percentage':'tax_amount'}}",
        null=True,
    )
    total_data = models.JSONField(blank=True, null=True)
    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default="New")
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Concatenate first name and last name
    @property
    def name(self):
        """
        Returns:
            str: The full name of the customer.
        """
        return f"{self.first_name} {self.last_name}"

    def order_placed_to(self):
        """
        Returns a string representation of the vendors to whom the order is placed.

        Returns:
            str: A comma-separated string of vendor names.
        """
        return ", ".join([str(i) for i in self.vendors.all()])

    def get_total_by_vendor(self):
        """
        Calculates the total amount for a specific vendor.

        Returns:
            dict: A dictionary containing the subtotal, 
            tax dictionary, and grand total.
        """
        vendor = Vendor.objects.get(user=request_object.user)
        subtotal = 0
        tax = 0
        tax_dict = {}
        if self.total_data:
            total_data = json.loads(self.total_data)
            data = total_data.get(str(vendor.id))

            for key, val in data.items():
                subtotal += float(key)
                val = val.replace("'", '"')
                val = json.loads(val)
                tax_dict.update(val)

                # calculate tax
                # {'CGST': {'9.00': '6.03'}, 'SGST': {'7.00': '4.69'}}
                for i in val:
                    for j in val[i]:
                        tax += float(val[i][j])
        grand_total = float(subtotal) + float(tax)
        context = {
            "subtotal": subtotal,
            "tax_dict": tax_dict,
            "grand_total": grand_total,
        }

        return context

    def __str__(self):
        return self.order_number


class OrderedFood(models.Model):
    """
    Represents an ordered food item.

    Attributes:
        order (Order): The order to which this food item belongs.
        payment (Payment): The payment associated with this food item (can be null).
        user (User): The user who placed the order.
        fooditem (FoodItem): The food item that was ordered.
        quantity (int): The quantity of the ordered food item.
        price (float): The price of the ordered food item.
        amount (float): The total amount for this ordered food item.
        created_at (datetime): The date and time when this ordered food item was created.
        updated_at (datetime): The date and time when this ordered food item was last updated.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fooditem.food_title
