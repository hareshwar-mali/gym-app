from django.urls import path
from .views import PlansListView, ActivatePlanView, ExtendTrialView, GymPaymentHistoryView

urlpatterns = [
    path('plans/', PlansListView.as_view(), name='plans-list'),
    path('activate/', ActivatePlanView.as_view(), name='activate-plan'),
    path('extend-trial/<int:gym_id>/', ExtendTrialView.as_view(), name='extend-trial'),
    path('payments/<int:gym_id>/', GymPaymentHistoryView.as_view(), name='gym-payment-history'),
]
