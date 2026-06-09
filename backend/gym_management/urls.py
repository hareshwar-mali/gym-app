from django.urls import path
from .views import (
    MemberListCreateView, MemberDetailView,
    AttendanceView, BulkAttendanceView,
    PaymentListCreateView, PaymentDetailView,
    ClassListCreateView, ClassDetailView,
    DashboardView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('members/', MemberListCreateView.as_view(), name='member-list'),
    path('members/<int:pk>/', MemberDetailView.as_view(), name='member-detail'),
    path('attendance/', AttendanceView.as_view(), name='attendance'),
    path('attendance/bulk/', BulkAttendanceView.as_view(), name='bulk-attendance'),
    path('payments/', PaymentListCreateView.as_view(), name='payment-list'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('classes/', ClassListCreateView.as_view(), name='class-list'),
    path('classes/<int:pk>/', ClassDetailView.as_view(), name='class-detail'),
]
