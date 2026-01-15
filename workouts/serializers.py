from rest_framework import serializers
from .models import WorkoutPlan, WorkoutTask
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkoutPlanSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    gym_branch_name = serializers.CharField(source='gym_branch.name', read_only=True)

    class Meta:
        model = WorkoutPlan
        fields = ['id', 'title', 'description', 'created_by', 'created_by_name', 'gym_branch', 'gym_branch_name',
                  'is_active', 'created_at']
        read_only_fields = ['created_by', 'gym_branch']


class WorkoutTaskSerializer(serializers.ModelSerializer):
    workout_plan_title = serializers.CharField(source='workout_plan.title', read_only=True)
    member_name = serializers.CharField(source='member.get_full_name', read_only=True)

    class Meta:
        model = WorkoutTask
        fields = ['id', 'workout_plan', 'workout_plan_title', 'member', 'member_name', 'status', 'due_date', 'notes',
                  'completed_at']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user

        # Validation for Create/Update by Trainer
        if user.role == 'TRAINER':
            plan = attrs.get('workout_plan') or self.instance.workout_plan
            member = attrs.get('member') or self.instance.member

            # Rule: Trainer cannot assign to member of another branch
            if member.gym_branch != user.gym_branch:
                raise serializers.ValidationError({"member": "You cannot assign tasks to members of another branch."})

            # Rule: Plan must belong to the trainer's branch
            if plan.gym_branch != user.gym_branch:
                raise serializers.ValidationError({"workout_plan": "You can only use workout plans from your branch."})

        return attrs


class MemberTaskUpdateSerializer(serializers.ModelSerializer):
    """
    Restricted serializer for Members.
    They can ONLY update the status, nothing else.
    """

    class Meta:
        model = WorkoutTask
        fields = ['status', 'notes']  # Optional: allow them to add notes

    def validate_status(self, value):
        # Prevent member from setting status back to Pending if wanted
        return value