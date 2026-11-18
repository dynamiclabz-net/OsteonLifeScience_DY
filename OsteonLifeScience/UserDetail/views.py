from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, status

from .serializers import UserSerializer

from utils.decorators import handle_exceptions, check_authentication
from utils.responses import success_response, error_response


class AuthViewSet(viewsets.ViewSet):

    @handle_exceptions
    @check_authentication()
    def list(self, request):
        """GET - details of the logged in user"""
        return success_response({'user': UserSerializer(request.user).data})

    @handle_exceptions
    def create(self, request):
        """POST - login with username + password"""
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return error_response("username and password are required.")

        user = authenticate(request, username=username, password=password)
        if not user:
            return error_response("Invalid credentials.", status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return success_response({'user': UserSerializer(user).data})

    @handle_exceptions
    @check_authentication()
    def destroy(self, request, pk=None):
        """DELETE - logout"""
        logout(request)
        return success_response({'logged_out': True})
