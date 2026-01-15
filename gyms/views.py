from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import GymBranch
from .serializers import GymBranchSerializer, GymBranchCreateUpdateSerializer
from account.permissions import IsAdmin


class GymBranchListView(generics.ListAPIView):
    """List all gym branches with pagination - Admin only"""
    queryset = GymBranch.objects.all()
    serializer_class = GymBranchSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        """Optionally filter by active status"""
        queryset = GymBranch.objects.all()

        # Filter by active status if provided
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset


class GymBranchCreateView(generics.CreateAPIView):
    """Create a new gym branch - Admin only"""
    queryset = GymBranch.objects.all()
    serializer_class = GymBranchCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class GymBranchDetailView(generics.RetrieveAPIView):
    """Retrieve a specific gym branch - Admin only"""
    queryset = GymBranch.objects.all()
    serializer_class = GymBranchSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'


class GymBranchUpdateView(generics.UpdateAPIView):
    """Update a specific gym branch - Admin only"""
    queryset = GymBranch.objects.all()
    serializer_class = GymBranchCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'


class GymBranchDeleteView(generics.DestroyAPIView):
    """Delete a specific gym branch - Admin only"""
    queryset = GymBranch.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "Gym branch deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )