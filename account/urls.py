from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView,
    UserViewSet,
    UserProfileView,
    PasswordChangeView,
    ActivityLogListView
)

app_name = 'account'


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', PasswordChangeView.as_view(), name='change_password'),

    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),

    # Management (Create/List Users)
    path('', include(router.urls)),

    # Logs
    path('activity-logs/', ActivityLogListView.as_view(), name='activity_logs'),
]