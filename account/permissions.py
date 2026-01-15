from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to Super Admins.
    Renamed from IsSuperAdmin to IsAdmin to match your existing gyms app imports.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsManager(permissions.BasePermission):
    """Allows access to Gym Managers."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'MANAGER'


class CanManageUsers(permissions.BasePermission):
    """
    - Admin can manage all.
    - Managers can manage users in their own branch.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['ADMIN', 'MANAGER', 'TRAINER']

    def has_object_permission(self, request, view, obj):
        # Super Admin can access anyone
        if request.user.role == 'ADMIN':
            return True

        # Manager can only access users in their specific branch
        if request.user.role == 'MANAGER':
            # Check if the target user belongs to the manager's branch
            return obj.gym_branch == request.user.gym_branch

        # Trainer can only access members in their specific branch
        if request.user.role == 'TRAINER':
            # Check if the target user belongs to the trainer's branch and is a member
            return obj.gym_branch == request.user.gym_branch and obj.role == 'MEMBER'

        return False