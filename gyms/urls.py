from django.urls import path
from . import views

app_name = 'gyms'

urlpatterns = [
    path('branches/', views.GymBranchListView.as_view(), name='gym-branches-list'),
    path('branches/create/', views.GymBranchCreateView.as_view(), name='gym-branches-create'),
    path('branches/<int:id>/', views.GymBranchDetailView.as_view(), name='gym-branches-detail'),
    path('branches/<int:id>/update/', views.GymBranchUpdateView.as_view(), name='gym-branches-update'),
    path('branches/<int:id>/delete/', views.GymBranchDeleteView.as_view(), name='gym-branches-delete'),
]