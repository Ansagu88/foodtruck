"""
here we define a middleware function that sets the request object in 
the models module and executes code before and after the view.

"""

from . import models


def request_object_middleware(get_response):
    """
    Middleware function that sets the request object in the models module 
    and executes code before and after the view.

    Args:
        get_response: The callable that takes a request and returns a response.

    Returns:
        The middleware function that processes the request and returns a response.
    """

    def middleware(request):
        """
        Middleware function that is executed for each request before 
        the view (and later middleware) are called.

        Args:
            request: The request object.

        Returns:
            The response object.
        """
        models.request_object = request

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
