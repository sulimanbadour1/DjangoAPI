from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MenuItem, Cart, MenuItem, Order, OrderItem
from .serializers import (
    MenuItemSerializer,
    UserSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
)
from rest_framework.views import APIView
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.throttling import ScopedRateThrottle


class IsManager(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name="Manager").exists() or request.user.is_staff
        )


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "category",
        "featured",
    ]  # Enables filtering by 'category' and 'featured'
    search_fields = ["title"]  # Enables searching by 'title'
    ordering_fields = ["title", "price"]  # Enables ordering by 'title' and 'price'
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "menuitems"


class GroupUsersView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get_users_in_group(self, group_name):
        group = Group.objects.get(name=group_name)
        users = group.user_set.all()
        return users

    def post_user_to_group(self, request, group_name):
        user_id = request.data.get("id")
        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(name=group_name)
            group.user_set.add(user)
            return Response(
                {"status": f"User added to {group_name} group"},
                status=status.HTTP_201_CREATED,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Group.DoesNotExist:
            return Response(
                {"error": f"{group_name} group not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete_user_from_group(self, request, userId, group_name):
        try:
            user = User.objects.get(id=userId)
            group = Group.objects.get(name=group_name)
            if user in group.user_set.all():
                group.user_set.remove(user)
                return Response({"status": f"User removed from {group_name} group"})
            else:
                return Response(
                    {"error": f"User not in {group_name} group"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Group.DoesNotExist:
            return Response(
                {"error": f"{group_name} group not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class ManagerUsersView(GroupUsersView):
    def get(self, request):
        users = self.get_users_in_group("Manager")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        return self.post_user_to_group(request, "Manager")


class ManagerUserDetailView(GroupUsersView):
    def delete(self, request, userId):
        return self.delete_user_from_group(request, userId, "Manager")


class DeliveryCrewUsersView(GroupUsersView):
    def get(self, request):
        users = self.get_users_in_group("Delivery Crew")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        return self.post_user_to_group(request, "Delivery Crew")


class DeliveryCrewUserDetailView(GroupUsersView):
    def delete(self, request, userId):
        return self.delete_user_from_group(request, userId, "Delivery Crew")


class CartItemsView(APIView):

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        menu_item_id = request.data.get("menuitem")
        quantity = request.data.get("quantity", 1)
        if not menu_item_id:
            return Response({"error": "MenuItem ID is required"}, status=400)
        menu_item = get_object_or_404(MenuItem, id=menu_item_id)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menuitem=menu_item,
            defaults={"quantity": quantity, "unit_price": menu_item.price},
        )
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()
        return Response({"status": "Menu item added to cart"}, status=201)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({"status": "Cart cleared"}, status=200)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "orders"
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = [
        "status",
        "delivery_crew",
    ]  # Filtering by 'status' and 'delivery_crew'
    ordering_fields = ["date", "total"]  # Ordering by 'date' and 'total'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Manager").exists() or user.is_staff:
            return Order.objects.all()
        elif user.groups.filter(name="Delivery Crew").exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)
