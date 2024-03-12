from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MenuItem
from .serializers import MenuItemSerializer, UserSerializer
from rest_framework.views import APIView
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class IsManager(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name="Manager").exists() or request.user.is_staff
        )


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):

        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsManager]
        return [permission() for permission in permission_classes]

    # The methods below are optional, they provide a place to add custom behavior or modify existing ones
    def list(self, request, *args, **kwargs):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = self.queryset
        # Example of filtering (optional)
        # username = request.query_params.get('username')
        # if username is not None:
        #     queryset = queryset.filter(purchaser__username=username)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # Custom logic for POST could be added here
        return super().create(request, *args, **kwargs)

    # Define other methods as needed (update, partial_update, destroy)


class ManagerUsersView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        manager_group = Group.objects.get(name="Manager")
        users = manager_group.user_set.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_id = request.data.get("id")
        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(id=user_id)
            manager_group = Group.objects.get(name="Manager")
            manager_group.user_set.add(user)
            return Response(
                {"status": "User added to manager group"},
                status=status.HTTP_201_CREATED,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ManagerUserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, userId):
        try:
            user = User.objects.get(id=userId)
            manager_group = Group.objects.get(name="Manager")
            if user in manager_group.user_set.all():
                manager_group.user_set.remove(user)
                return Response({"status": "User removed from manager group"})
            else:
                return Response(
                    {"error": "User not in manager group"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
