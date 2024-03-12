from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"menu-items", views.MenuItemViewSet)

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
]
