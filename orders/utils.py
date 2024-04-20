"""
Here, we will define some utility functions that will be used in the orders app.
"""
import datetime
import simplejson as json


def generate_order_number(pk):
    """
    Generate an order number by combining the current datetime and the primary key.

    Args:
        pk (int): The primary key of the order.

    Returns:
        str: The generated order number.

    """
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S') #20220616233810 + pk
    order_number = current_datetime + str(pk)
    return order_number


def order_total_by_vendor(order, vendor_id):
    """
    Calculate the total order amount for a specific vendor.

    Args:
        order (Order): The order object.
        vendor_id (int): The ID of the vendor.

    Returns:
        dict: A dictionary containing the subtotal, tax dictionary, and grand total.

    Example:
        order = Order.objects.get(id=1)
        vendor_id = 2
        result = order_total_by_vendor(order, vendor_id)
        print(result)
        # Output: {'subtotal': 50.0, 'tax_dict': {'CGST': {'9.00': '6.03'}, 'SGST': {'7.00': '4.69'}}, 'grand_total': 60.72}
    """
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor_id))
    subtotal = 0
    tax = 0
    tax_dict = {}

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
        'subtotal': subtotal,
        'tax_dict': tax_dict, 
        'grand_total': grand_total,
    }

    return context
