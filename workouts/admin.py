from django.contrib import admin
from .models import WorkoutPlan, WorkoutTask

admin.site.register(WorkoutPlan)
admin.site.register(WorkoutTask)
