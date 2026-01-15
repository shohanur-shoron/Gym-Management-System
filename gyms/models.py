from django.db import models
from django.core.exceptions import ValidationError


class GymBranch(models.Model):
    """Gym Branch model"""

    name = models.CharField(max_length=200)
    location = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gym_branches'
        verbose_name_plural = 'Gym Branches'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.location}"

    def clean(self):
        """Validate trainer limit"""
        super().clean()

        # Check trainer limit only when updating
        if self.pk:
            trainer_count = self.users.filter(role='TRAINER', is_active=True).count()
            if trainer_count > 3:
                raise ValidationError({
                    'trainers': 'A gym branch can have a maximum of 3 trainers'
                })

    @property
    def trainer_count(self):
        return self.users.filter(role='TRAINER', is_active=True).count()

    @property
    def member_count(self):
        return self.users.filter(role='MEMBER', is_active=True).count()

    @property
    def can_add_trainer(self):
        return self.trainer_count < 3