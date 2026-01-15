from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutPlanViewSet, WorkoutTaskViewSet

app_name = 'workouts'

router = DefaultRouter()
router.register(r'plans', WorkoutPlanViewSet, basename='workout-plans')
router.register(r'tasks', WorkoutTaskViewSet, basename='workout-tasks')

urlpatterns = [
    path('', include(router.urls)),
]