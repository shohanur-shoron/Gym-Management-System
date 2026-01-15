from rest_framework import serializers
from .models import GymBranch


class GymBranchSerializer(serializers.ModelSerializer):
    """Serializer for GymBranch model"""
    
    class Meta:
        model = GymBranch
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class GymBranchCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating GymBranch"""
    
    class Meta:
        model = GymBranch
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')