from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"menu-items", views.MenuItemViewSet)
router.register(r"orders", views.OrderViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
    path(
        "groups/manager/users", views.ManagerUsersView.as_view(), name="manager-users"
    ),
    path(
        "groups/manager/users/<int:userId>",
        views.ManagerUserDetailView.as_view(),
        name="manager-user-detail",
    ),
    path(
        "groups/delivery-crew/users",
        views.DeliveryCrewUsersView.as_view(),
        name="delivery-crew-users",
    ),
    path(
        "groups/delivery-crew/users/<int:userId>",
        views.DeliveryCrewUserDetailView.as_view(),
        name="delivery-crew-user-detail",
    ),
    path("cart/menu-items", views.CartItemsView.as_view(), name="cart-items"),
]
