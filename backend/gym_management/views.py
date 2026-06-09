from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import date
from .models import Member, Attendance, Payment, ClassSchedule
from .serializers import MemberSerializer, AttendanceSerializer, PaymentSerializer, ClassScheduleSerializer
from accounts.models import Gym


def get_gym(user):
    try:
        return user.gym
    except Exception:
        return None


def check_access(gym):
    if not gym:
        return False
    return gym.status in ['trial_active', 'active', 'expiring_soon']


# ── Members ──────────────────────────────────────────────────────────────────

class MemberListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gym = get_gym(request.user)
        if not gym:
            return Response({'error': 'Gym not found.'}, status=404)
        search = request.query_params.get('search', '')
        members = gym.members.all()
        if search:
            members = members.filter(name__icontains=search) | members.filter(mobile__icontains=search)
        return Response(MemberSerializer(members, many=True).data)

    def post(self, request):
        gym = get_gym(request.user)
        if not gym or not check_access(gym):
            return Response({'error': 'Subscription expired. Please renew to add members.'}, status=403)
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(gym=gym)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class MemberDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        gym = get_gym(request.user)
        try:
            return gym.members.get(pk=pk)
        except Member.DoesNotExist:
            return None

    def get(self, request, pk):
        member = self.get_object(request, pk)
        if not member:
            return Response({'error': 'Member not found.'}, status=404)
        return Response(MemberSerializer(member).data)

    def put(self, request, pk):
        gym = get_gym(request.user)
        if not check_access(gym):
            return Response({'error': 'Subscription expired.'}, status=403)
        member = self.get_object(request, pk)
        if not member:
            return Response({'error': 'Member not found.'}, status=404)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        gym = get_gym(request.user)
        if not check_access(gym):
            return Response({'error': 'Subscription expired.'}, status=403)
        member = self.get_object(request, pk)
        if not member:
            return Response({'error': 'Member not found.'}, status=404)
        member.delete()
        return Response(status=204)


# ── Attendance ────────────────────────────────────────────────────────────────

class AttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gym = get_gym(request.user)
        if not gym:
            return Response({'error': 'Gym not found.'}, status=404)
        att_date = request.query_params.get('date', str(date.today()))
        records = gym.attendance.filter(attendance_date=att_date)
        return Response(AttendanceSerializer(records, many=True).data)

    def post(self, request):
        gym = get_gym(request.user)
        if not check_access(gym):
            return Response({'error': 'Subscription expired.'}, status=403)
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.validated_data['member']
            att_date = serializer.validated_data['attendance_date']
            obj, created = Attendance.objects.get_or_create(
                gym=gym, member=member, attendance_date=att_date,
                defaults={
                    'status': serializer.validated_data.get('status', 'present'),
                    'check_in_time': serializer.validated_data.get('check_in_time'),
                    'remarks': serializer.validated_data.get('remarks', ''),
                }
            )
            if not created:
                obj.delete()
                return Response({'message': 'Marked absent.', 'action': 'removed'})
            return Response(AttendanceSerializer(obj).data, status=201)
        return Response(serializer.errors, status=400)


class BulkAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        gym = get_gym(request.user)
        if not check_access(gym):
            return Response({'error': 'Subscription expired.'}, status=403)
        att_date = request.data.get('date', str(date.today()))
        from datetime import datetime
        import time
        now_time = datetime.now().time()
        members = gym.members.filter(membership_status='active')
        created_count = 0
        for member in members:
            _, created = Attendance.objects.get_or_create(
                gym=gym, member=member, attendance_date=att_date,
                defaults={'status': 'present', 'check_in_time': now_time}
            )
            if created:
                created_count += 1
        return Response({'message': f'{created_count} members marked present.'})


# ── Payments ──────────────────────────────────────────────────────────────────

class PaymentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gym = get_gym(request.user)
        if not gym:
            return Response({'error': 'Gym not found.'}, status=404)
        pay_status = request.query_params.get('status', '')
        payments = gym.payments.all()
        if pay_status:
            payments = payments.filter(payment_status=pay_status)
        return Response(PaymentSerializer(payments, many=True).data)

    def post(self, request):
        gym = get_gym(request.user)
        if not check_access(gym):
            return Response({'error': 'Subscription expired.'}, status=403)
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(gym=gym)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        gym = get_gym(request.user)
        try:
            payment = gym.payments.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=404)
        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        gym = get_gym(request.user)
        try:
            payment = gym.payments.get(pk=pk)
            payment.delete()
            return Response(status=204)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=404)


# ── Classes ───────────────────────────────────────────────────────────────────

class ClassListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gym = get_gym(request.user)
        if not gym:
            return Response({'error': 'Gym not found.'}, status=404)
        classes = gym.classes.filter(is_active=True)
        return Response(ClassScheduleSerializer(classes, many=True).data)

    def post(self, request):
        gym = get_gym(request.user)
        if not check_access(gym):
            return Response({'error': 'Subscription expired.'}, status=403)
        serializer = ClassScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(gym=gym)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ClassDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        gym = get_gym(request.user)
        try:
            cls = gym.classes.get(pk=pk)
        except ClassSchedule.DoesNotExist:
            return Response({'error': 'Class not found.'}, status=404)
        serializer = ClassScheduleSerializer(cls, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        gym = get_gym(request.user)
        try:
            cls = gym.classes.get(pk=pk)
            cls.delete()
            return Response(status=204)
        except ClassSchedule.DoesNotExist:
            return Response({'error': 'Class not found.'}, status=404)


# ── Dashboard Stats ───────────────────────────────────────────────────────────

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gym = get_gym(request.user)
        if not gym:
            return Response({'error': 'Gym not found.'}, status=404)

        today = date.today()
        from datetime import timedelta
        week_later = today + timedelta(days=7)

        total_members = gym.members.count()
        active_members = gym.members.filter(membership_status='active').count()
        today_attendance = gym.attendance.filter(attendance_date=today).count()
        expiring_this_week = gym.members.filter(
            membership_end_date__gte=today,
            membership_end_date__lte=week_later,
            membership_status='active'
        ).count()

        this_month = today.strftime('%Y-%m')
        monthly_revenue = sum(
            p.paid_amount for p in gym.payments.filter(
                payment_date__startswith=this_month,
                payment_status='paid'
            )
        )
        pending_payments = gym.payments.filter(payment_status='pending').count()
        recent_members = gym.members.order_by('-created_at')[:5]

        return Response({
            'total_members': total_members,
            'active_members': active_members,
            'today_attendance': today_attendance,
            'expiring_this_week': expiring_this_week,
            'monthly_revenue': float(monthly_revenue),
            'pending_payments': pending_payments,
            'recent_members': MemberSerializer(recent_members, many=True).data,
            'gym_status': gym.status,
        })
