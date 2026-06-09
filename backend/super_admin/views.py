from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date, timedelta
from accounts.models import Gym
from accounts.serializers import GymDetailSerializer


class IsSuperAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'super_admin'


class GymListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        filter_type = request.query_params.get('filter', 'all')
        search = request.query_params.get('search', '')
        today = date.today()
        week_later = today + timedelta(days=7)
        month_later = today + timedelta(days=30)

        gyms = Gym.objects.all()

        if search:
            gyms = gyms.filter(
                mobile__icontains=search
            ) | Gym.objects.filter(
                gym_name__icontains=search
            ) | Gym.objects.filter(
                owner_name__icontains=search
            ) | Gym.objects.filter(
                email__icontains=search
            ) | Gym.objects.filter(
                city__icontains=search
            )
            gyms = gyms.distinct()

        if filter_type == 'trial_active':
            gyms = gyms.filter(status='trial_active')
        elif filter_type == 'trial_expired':
            gyms = gyms.filter(status='trial_expired')
        elif filter_type == 'active':
            gyms = gyms.filter(status__in=['active', 'expiring_soon'])
        elif filter_type == 'expiring_today':
            gyms = gyms.filter(subscription_end_date=today)
        elif filter_type == 'expiring_week':
            gyms = gyms.filter(subscription_end_date__gte=today, subscription_end_date__lte=week_later)
        elif filter_type == 'expiring_month':
            gyms = gyms.filter(subscription_end_date__gte=today, subscription_end_date__lte=month_later)
        elif filter_type == 'expired':
            gyms = gyms.filter(status='expired')
        elif filter_type == 'blocked':
            gyms = gyms.filter(is_blocked=True)

        return Response(GymDetailSerializer(gyms, many=True).data)


class GymDetailView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, gym_id):
        try:
            gym = Gym.objects.get(id=gym_id)
            return Response(GymDetailSerializer(gym).data)
        except Gym.DoesNotExist:
            return Response({'error': 'Gym not found.'}, status=404)


class BlockGymView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, gym_id):
        try:
            gym = Gym.objects.get(id=gym_id)
            gym.is_blocked = True
            gym.status = 'blocked'
            gym.save(update_fields=['is_blocked', 'status'])
            return Response({'message': f'{gym.gym_name} has been blocked.'})
        except Gym.DoesNotExist:
            return Response({'error': 'Gym not found.'}, status=404)


class UnblockGymView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, gym_id):
        try:
            gym = Gym.objects.get(id=gym_id)
            gym.is_blocked = False
            gym.status = 'trial_active'
            gym.save(update_fields=['is_blocked', 'status'])
            return Response({'message': f'{gym.gym_name} has been unblocked.'})
        except Gym.DoesNotExist:
            return Response({'error': 'Gym not found.'}, status=404)


class SuperAdminDashboardView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        today = date.today()
        week_later = today + timedelta(days=7)
        month_later = today + timedelta(days=30)

        all_gyms = Gym.objects.all()
        total = all_gyms.count()
        trial_active = all_gyms.filter(status='trial_active').count()
        trial_expired = all_gyms.filter(status='trial_expired').count()
        active = all_gyms.filter(status__in=['active', 'expiring_soon']).count()
        expired = all_gyms.filter(status='expired').count()
        blocked = all_gyms.filter(is_blocked=True).count()
        expiring_today = all_gyms.filter(subscription_end_date=today).count()
        expiring_week = all_gyms.filter(subscription_end_date__gte=today, subscription_end_date__lte=week_later).count()
        expiring_month = all_gyms.filter(subscription_end_date__gte=today, subscription_end_date__lte=month_later).count()

        from subscriptions.models import ManualSubscriptionPayment
        from django.db.models import Sum
        total_revenue = ManualSubscriptionPayment.objects.filter(status='approved').aggregate(
            total=Sum('amount')
        )['total'] or 0

        upcoming_expiry = all_gyms.filter(
            subscription_end_date__gte=today,
            subscription_end_date__lte=week_later
        ).order_by('subscription_end_date')

        return Response({
            'total_gyms': total,
            'trial_active': trial_active,
            'trial_expired': trial_expired,
            'active_paid': active,
            'expired': expired,
            'blocked': blocked,
            'expiring_today': expiring_today,
            'expiring_this_week': expiring_week,
            'expiring_this_month': expiring_month,
            'total_revenue': float(total_revenue),
            'upcoming_expiry': GymDetailSerializer(upcoming_expiry, many=True).data,
        })
