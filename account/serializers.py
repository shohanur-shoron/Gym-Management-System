from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for viewing users (safely without password)"""
    gym_branch_name = serializers.CharField(source='gym_branch.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'gym_branch', 'gym_branch_name', 'phone_number', 'is_active',
                  'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating users.
    Handles strict validation for Branch limits and Hierarchy.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'password', 'role', 'first_name', 'last_name', 'gym_branch', 'phone_number', 'gender']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        new_role = attrs.get('role')
        target_branch = attrs.get('gym_branch')

        # --- Hierarchy Logic ---

        # 1. Super Admin Restrictions
        if user.role == 'ADMIN':
            if new_role == 'MANAGER' and not target_branch:
                raise serializers.ValidationError({"gym_branch": "Managers must be assigned to a branch."})
            if new_role == 'ADMIN':
                # Optional: Decide if Admins can create other Admins. Usually yes.
                pass

        # 2. Manager Restrictions
        elif user.role == 'MANAGER':
            # Manager can only create Trainers or Members
            if new_role not in ['TRAINER', 'MEMBER']:
                raise serializers.ValidationError("Managers can only create Trainers or Members.")

            # Manager cannot assign users to other branches
            if target_branch and target_branch != user.gym_branch:
                raise serializers.ValidationError({"gym_branch": "You cannot create users for another branch."})

            # Force the branch to be the Manager's branch
            attrs['gym_branch'] = user.gym_branch
            target_branch = user.gym_branch

        # 3. Trainer Restrictions
        elif user.role == 'TRAINER':
            # Trainers can only create members
            if new_role != 'MEMBER':
                raise serializers.ValidationError("Trainers can only create members.")

            # Trainer cannot assign users to other branches
            if target_branch and target_branch != user.gym_branch:
                raise serializers.ValidationError({"gym_branch": "You cannot create users for another branch."})

            # Force the branch to be the Trainer's branch
            attrs['gym_branch'] = user.gym_branch
            target_branch = user.gym_branch

        else:
            raise serializers.ValidationError("You do not have permission to create users.")

        # --- Business Rule: Max 3 Trainers per Branch ---
        if new_role == 'TRAINER' and target_branch:
            trainer_count = User.objects.filter(gym_branch=target_branch, role='TRAINER').count()
            if trainer_count >= 3:
                raise serializers.ValidationError("This branch already has the maximum of 3 trainers.")

        return attrs

    def create(self, validated_data):
        # Since Admin/Manager creates this, we auto-verify the account
        validated_data['is_verified'] = True
        return User.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        from django.contrib.auth import authenticate
        user = authenticate(email=attrs['email'], password=attrs['password'])

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        return {'user': user}


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating users.
    Allows updating of user details including phone number.
    """
    class Meta:
        model = User
        fields = ['email', 'role', 'first_name', 'last_name', 'gym_branch', 'phone_number', 'gender', 'is_active']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        new_role = attrs.get('role')
        target_branch = attrs.get('gym_branch')

        # Apply similar business rules as creation
        if user.role == 'ADMIN':
            # Admin can update anything
            pass
        elif user.role == 'MANAGER':
            # Manager can only update users in their own branch
            target_obj = self.instance  # The user being updated
            if target_obj and target_obj.gym_branch != user.gym_branch:
                raise serializers.ValidationError("You can only update users in your own branch.")

            # Manager cannot change role to ADMIN or MANAGER
            if new_role in ['ADMIN', 'MANAGER']:
                raise serializers.ValidationError("Managers cannot change user roles to Admin or Manager.")

        elif user.role == 'TRAINER':
            # Trainer can only update members in their own branch
            target_obj = self.instance  # The user being updated
            if target_obj:
                if target_obj.gym_branch != user.gym_branch:
                    raise serializers.ValidationError("You can only update users in your own branch.")

                if target_obj.role != 'MEMBER':
                    raise serializers.ValidationError("Trainers can only update members.")

            # Trainers cannot change roles
            if new_role:
                raise serializers.ValidationError("Trainers cannot change user roles.")

        else:
            raise serializers.ValidationError("You do not have permission to update users.")

        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])