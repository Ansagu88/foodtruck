"""
This view module contains the home view which renders the home page with a list 
of vendors based on the user's current location.

The get_or_set_current_location function retrieves the current location coordinates

"""

from django.shortcuts import render

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance

from vendor.models import Vendor


def get_or_set_current_location(request):
    """
    Retrieves the current location coordinates from the request session or request GET parameters.
    If the coordinates are found in the session, they are returned.
    If the coordinates are found in the GET parameters, they are stored in the session and returned.
    If no coordinates are found, None is returned.

    Args:
        request (HttpRequest): The request object containing session and GET parameters.

    Returns:
        tuple: A tuple containing the longitude and latitude coordinates (lng, lat) if found, 
        otherwise None.
    """
    if "lat" in request.session:
        lat = request.session["lat"]
        lng = request.session["lng"]
        return lng, lat
    elif "lat" in request.GET:
        lat = request.GET.get("lat")
        lng = request.GET.get("lng")
        request.session["lat"] = lat
        request.session["lng"] = lng
        return lng, lat
    else:
        return None


def home(request):
    """
    Renders the home page with a list of vendors based on the user's current location.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered home page.

    Raises:
        None
    """
    if get_or_set_current_location(request) is not None:

        pnt = GEOSGeometry("POINT(%s %s)" % (get_or_set_current_location(request)))

        vendors = (
            Vendor.objects.filter(
                user_profile__location__distance_lte=(pnt, D(km=1000))
            )
            .annotate(distance=Distance("user_profile__location", pnt))
            .order_by("distance")
        )

        for v in vendors:
            v.kms = round(v.distance.km, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        "vendors": vendors,
    }

    return render(request, "home.html", context)
