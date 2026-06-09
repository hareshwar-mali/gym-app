from django.urls import path
from .views import (
    GymListView, GymDetailView,
    BlockGymView, UnblockGymView,
    SuperAdminDashboardView,
)

urlpatterns = [
    path('dashboard/', SuperAdminDashboardView.as_view(), name='super-dashboard'),
    path('gyms/', GymListView.as_view(), name='gym-list'),
    path('gyms/<int:gym_id>/', GymDetailView.as_view(), name='gym-detail'),
    path('gyms/<int:gym_id>/block/', BlockGymView.as_view(), name='block-gym'),
    path('gyms/<int:gym_id>/unblock/', UnblockGymView.as_view(), name='unblock-gym'),
]
