from django.urls import path
from .views import (AppListView, AppDetailView, UserListView, UserDetailView,
                    RoleListView, RoleDetailView, AppPermissionListView,
                    AppPermissionDetailView, LoginView)

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('apps/', AppListView.as_view()),
    path('apps/<int:pk>/', AppDetailView.as_view()),
    path('users/', UserListView.as_view()),
    path('users/<int:pk>/', UserDetailView.as_view()),
    path('roles/', RoleListView.as_view()),
    path('roles/<int:pk>/', RoleDetailView.as_view()),
    path('permissions/', AppPermissionListView.as_view()),
    path('permissions/<int:pk>/', AppPermissionDetailView.as_view()),
]
