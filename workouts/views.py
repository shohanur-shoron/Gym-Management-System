from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import WorkoutPlan, WorkoutTask
from .serializers import (
    WorkoutPlanSerializer,
    WorkoutTaskSerializer,
    MemberTaskUpdateSerializer
)
from .permissions import PlanAccessPermission, TaskAccessPermission


class WorkoutPlanViewSet(viewsets.ModelViewSet):
    """
    Manage Workout Plans.
    - Create: Trainers only.
    - View: Trainers & Managers (Own Branch), Admin (All).
    - Members cannot view this endpoint.
    """
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsAuthenticated, PlanAccessPermission]

    def get_queryset(self):
        user = self.request.user

        # Admin sees all
        if user.role == 'ADMIN':
            return WorkoutPlan.objects.all()

        # Trainers/Managers see branch plans
        if user.role in ['TRAINER', 'MANAGER']:
            return WorkoutPlan.objects.filter(gym_branch=user.gym_branch)

        # Members see nothing (Strict Rule)
        return WorkoutPlan.objects.none()

    def perform_create(self, serializer):
        # Auto-assign creator and branch
        if self.request.user.role != 'TRAINER':
            # This check is technically handled by permissions, but as a safeguard:
            raise PermissionError("Only trainers can create workout plans.")

        serializer.save(
            created_by=self.request.user,
            gym_branch=self.request.user.gym_branch
        )


class WorkoutTaskViewSet(viewsets.ModelViewSet):
    """
    Manage Workout Tasks.
    - Trainers: Create & Assign tasks.
    - Members: View & Update status of OWN tasks.
    - Managers: View branch tasks.
    """
    permission_classes = [IsAuthenticated, TaskAccessPermission]

    def get_serializer_class(self):
        # If a member is updating, use restricted serializer
        if self.action in ['update', 'partial_update'] and self.request.user.role == 'MEMBER':
            return MemberTaskUpdateSerializer
        return WorkoutTaskSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == 'ADMIN':
            return WorkoutTask.objects.all()

        # Trainers/Managers see all tasks in their branch
        if user.role in ['TRAINER', 'MANAGER']:
            return WorkoutTask.objects.filter(workout_plan__gym_branch=user.gym_branch)

        # Members ONLY see their own tasks
        if user.role == 'MEMBER':
            return WorkoutTask.objects.filter(member=user)

        return WorkoutTask.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'TRAINER':
            raise PermissionError("Only trainers can assign tasks.")
        serializer.save()

    def perform_update(self, serializer):
        # Business Logic: Auto-timestamp completion
        instance = serializer.save()
        if instance.status == 'COMPLETED' and not instance.completed_at:
            instance.completed_at = timezone.now()
            instance.save()