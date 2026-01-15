from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from .models import User, ActivityLog
from .serializers import (
    UserCreateSerializer,
    UserListSerializer,
    UserUpdateSerializer,
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer
)
from .permissions import CanManageUsers


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Users to be viewed or edited.
    """
    permission_classes = [IsAuthenticated, CanManageUsers]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()

        user = self.request.user

        if not user.is_authenticated:
            return User.objects.none()

        if user.role == 'ADMIN':
            return User.objects.all()

        if user.role == 'MANAGER':
            return User.objects.filter(gym_branch=user.gym_branch)

        if user.role == 'TRAINER':
            return User.objects.filter(gym_branch=user.gym_branch, role='MEMBER')

        return User.objects.none()

    def perform_create(self, serializer):
        user_instance = serializer.save()

        ActivityLog.objects.create(
            user=self.request.user,
            action='CREATE',
            model_name='User',
            details=f"Created user {user_instance.email} ({user_instance.role})"
        )

        if user_instance.role == 'MEMBER':
            pass

    def perform_update(self, serializer):
        user_instance = serializer.save()

        ActivityLog.objects.create(
            user=self.request.user,
            action='UPDATE',
            model_name='User',
            details=f"Updated user {user_instance.email} ({user_instance.role})",
            object_id=user_instance.id
        )


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        # Log Login
        ActivityLog.objects.create(
            user=user,
            action='LOGIN',
            model_name='User',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': user.role,
            'gym_branch': user.gym_branch.id if user.gym_branch else None,
            'email': user.email
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveAPIView):
    """
    Get the current user's profile.
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.data.get('old_password')):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.data.get('new_password'))
        user.save()
        return Response({"status": "Password updated successfully"}, status=status.HTTP_200_OK)


class ActivityLogListView(generics.ListAPIView):
    """
    Optional: Admin only activity logs
    """
    from .models import ActivityLog
    queryset = ActivityLog.objects.all()

    # Simple serializer for logs
    class LogSerializer(serializers.ModelSerializer):
        class Meta:
            model = ActivityLog
            fields = '__all__'

    serializer_class = LogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return ActivityLog.objects.all()
        return ActivityLog.objects.filter(user=self.request.user)