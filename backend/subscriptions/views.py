from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date
from accounts.models import Gym
from .models import SubscriptionPlan, Subscription, ManualSubscriptionPayment
from .serializers import SubscriptionPlanSerializer, ActivatePlanSerializer, ManualPaymentSerializer


class IsSuperAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'super_admin'


class PlansListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        return Response(SubscriptionPlanSerializer(plans, many=True).data)


class ActivatePlanView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        serializer = ActivatePlanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            gym = Gym.objects.get(id=data['gym_id'])
            plan = SubscriptionPlan.objects.get(id=data['plan_id'])
        except (Gym.DoesNotExist, SubscriptionPlan.DoesNotExist):
            return Response({'error': 'Gym or Plan not found.'}, status=status.HTTP_404_NOT_FOUND)

        today = date.today()
        if gym.subscription_end_date and gym.subscription_end_date >= today:
            start_date = gym.subscription_end_date
        else:
            start_date = today

        from datetime import timedelta
        end_date = start_date + timedelta(days=plan.duration_days)

        Subscription.objects.create(
            gym=gym, plan=plan,
            start_date=start_date, end_date=end_date,
            status='active', activated_by=request.user.email
        )

        ManualSubscriptionPayment.objects.create(
            gym=gym, plan=plan,
            amount=data['amount'],
            payment_mode=data['payment_mode'],
            transaction_id=data.get('transaction_id', ''),
            payment_date=data['payment_date'],
            remarks=data.get('remarks', ''),
            verified_by=request.user.email,
            verified_at=timezone.now(),
            status='approved'
        )

        gym.subscription_end_date = end_date
        gym.status = 'active'
        gym.save(update_fields=['subscription_end_date', 'status'])

        return Response({
            'message': f'Plan activated. New expiry: {end_date}',
            'expiry_date': end_date
        })


class ExtendTrialView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, gym_id):
        days = request.data.get('days', 7)
        try:
            gym = Gym.objects.get(id=gym_id)
        except Gym.DoesNotExist:
            return Response({'error': 'Gym not found.'}, status=status.HTTP_404_NOT_FOUND)

        from datetime import timedelta
        gym.trial_end_date = gym.trial_end_date + timedelta(days=int(days))
        gym.status = 'trial_active'
        gym.save(update_fields=['trial_end_date', 'status'])
        return Response({'message': f'Trial extended by {days} days. New trial end: {gym.trial_end_date}'})


class GymPaymentHistoryView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, gym_id):
        payments = ManualSubscriptionPayment.objects.filter(gym_id=gym_id)
        return Response(ManualPaymentSerializer(payments, many=True).data)
