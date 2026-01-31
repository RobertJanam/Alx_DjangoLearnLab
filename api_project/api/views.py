"""
Authentication and Permissions Guide:
====================================

1. TOKEN AUTHENTICATION:
   - Get token: POST /api/api-token-auth/ with username/password
   - Use token: Add header: "Authorization: Token YOUR_TOKEN_HERE"

2. PERMISSION LEVELS:
   - BookList: Requires authentication to view
   - BookViewSet:
        - List/Retrieve: Public (AllowAny) or Authenticated (depending on config)
        - Create/Update/Delete: Admin users only

3. AVAILABLE PERMISSION CLASSES:
   - AllowAny: No restrictions
   - IsAuthenticated: Must be logged in
   - IsAdminUser: Must be staff user
   - IsAuthenticatedOrReadOnly: Read for all, write for authenticated
   - DjangoModelPermissions: Tied to Django's permission system

4. CUSTOM PERMISSIONS:
   - See IsAdminOrReadOnly class for example
   - Override has_permission() or has_object_permission() methods
"""

from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import Book
from .serializers import BookSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class BookList(generics.ListAPIView):

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

class BookViewSet(viewsets.ModelViewSet):

    queryset = Book.objects.all()
    serializer_class = BookSerializer

    permission_classes = [IsAdminOrReadOnly]

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]