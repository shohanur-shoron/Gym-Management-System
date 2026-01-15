from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings  # Best practice to refer to User model


class WorkoutPlan(models.Model):
    """Workout Plan created by trainers"""

    title = models.CharField(max_length=255)
    description = models.TextField()

    # Use settings.AUTH_USER_MODEL instead of importing User directly
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_workout_plans',
        limit_choices_to={'role': 'TRAINER'}
    )

    # Point to the gyms app
    gym_branch = models.ForeignKey(
        'gyms.GymBranch',
        on_delete=models.CASCADE,
        related_name='workout_plans'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workout_plans'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['gym_branch', 'is_active']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.title} - {self.gym_branch.name}"

    def clean(self):
        """Validate business rules"""
        super().clean()

        # Ensure creator is a trainer
        if self.created_by and self.created_by.role != 'TRAINER':
            raise ValidationError({
                'created_by': 'Workout plans can only be created by trainers'
            })

        # Ensure gym branch matches creator's branch
        if self.created_by and self.created_by.gym_branch != self.gym_branch:
            raise ValidationError({
                'gym_branch': 'Workout plan must belong to trainer\'s gym branch'
            })

    def save(self, *args, **kwargs):
        # Auto-set gym_branch from trainer if not provided
        if not self.gym_branch and self.created_by:
            self.gym_branch = self.created_by.gym_branch
        self.full_clean()
        super().save(*args, **kwargs)


class WorkoutTask(models.Model):
    """Workout tasks assigned to members"""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workout_tasks',
        limit_choices_to={'role': 'MEMBER'}
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    due_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workout_tasks'
        ordering = ['-created_at']
        unique_together = [['workout_plan', 'member', 'due_date']]
        indexes = [
            models.Index(fields=['member', 'status']),
            models.Index(fields=['workout_plan']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.workout_plan.title} - {self.member.email} ({self.status})"

    def clean(self):
        """Validate business rules"""
        super().clean()

        # Ensure member role is correct
        if self.member and self.member.role != 'MEMBER':
            raise ValidationError({
                'member': 'Tasks can only be assigned to members'
            })

        # Ensure member belongs to same branch as workout plan
        if self.member and self.workout_plan:
            if self.member.gym_branch != self.workout_plan.gym_branch:
                raise ValidationError({
                    'member': 'Cannot assign tasks to members from different gym branches'
                })

    def save(self, *args, **kwargs):
        self.full_clean()

        # Auto-set completed_at when status changes to COMPLETED
        if self.status == 'COMPLETED' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'COMPLETED' and self.completed_at:
            self.completed_at = None

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == 'COMPLETED':
            return False
        return self.due_date < timezone.now().date()

    @property
    def gym_branch(self):
        return self.workout_plan.gym_branch if self.workout_plan else None