from rest_framework.response import Response
from rest_framework import status


def success_response(data, http_status=status.HTTP_200_OK):
    return Response({
        "success": True,
        "user_not_logged_in": False,
        "user_unauthorized": False,
        "data": data,
        "error": None
    }, status=http_status)


def error_response(error, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "user_not_logged_in": False,
        "user_unauthorized": False,
        "data": None,
        "error": error
    }, status=http_status)
