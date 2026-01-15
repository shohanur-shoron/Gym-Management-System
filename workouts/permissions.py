from rest_framework import permissions


class IsTrainer(permissions.BasePermission):
    """Allows access only to Trainers."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'TRAINER'


class IsBranchManager(permissions.BasePermission):
    """Allows access only to Managers."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'MANAGER'


class IsMember(permissions.BasePermission):
    """Allows access only to Members."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'MEMBER'


class PlanAccessPermission(permissions.BasePermission):
    """
    - Trainers: Create, Read, Update (Own Branch)
    - Managers: Read Only (Own Branch)
    - Members: No Access (Cannot view plans directly)
    - Admin: Full Access
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'MEMBER':
            return False  # Members cannot view plans directly
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'ADMIN':
            return True
        # Trainers/Managers can only view plans in their branch
        return obj.gym_branch == user.gym_branch


class TaskAccessPermission(permissions.BasePermission):
    """
    - Trainers: Create, Read, Update (Own Branch)
    - Managers: Read Only (Own Branch)
    - Members: Read, Update Status Only (Own Tasks)
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'ADMIN':
            return True

        # Member can only access their own task
        if user.role == 'MEMBER':
            return obj.member == user

        # Staff can access tasks in their branch
        return obj.workout_plan.gym_branch == user.gym_branch