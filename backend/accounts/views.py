from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .models import Gym
from .serializers import GymRegisterSerializer, GymDetailSerializer
from datetime import date

User = get_user_model()


def get_gym_status(gym):
    today = date.today()
    if gym.is_blocked:
        return 'blocked'
    if gym.subscription_end_date and gym.subscription_end_date >= today:
        days_left = (gym.subscription_end_date - today).days
        if days_left <= 7:
            return 'expiring_soon'
        return 'active'
    if gym.trial_end_date and gym.trial_end_date >= today:
        return 'trial_active'
    if gym.subscription_end_date and gym.subscription_end_date < today:
        return 'expired'
    return 'trial_expired'


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GymRegisterSerializer(data=request.data)
        if serializer.is_valid():
            gym = serializer.save()
            refresh = RefreshToken.for_user(gym.user)
            return Response({
                'message': 'Registration successful. Your 7-day free trial has started.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'role': 'gym_owner',
                'gym': GymDetailSerializer(gym).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        role = request.data.get('role', 'gym_owner')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.role == 'super_admin':
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'role': 'super_admin',
                'email': user.email,
            })

        try:
            gym = user.gym
        except Gym.DoesNotExist:
            return Response({'error': 'No gym found for this account.'}, status=status.HTTP_404_NOT_FOUND)

        current_status = get_gym_status(gym)
        gym.status = current_status
        gym.save(update_fields=['status'])

        if current_status == 'blocked':
            return Response({'error': 'Your account has been blocked. Please contact support.'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'role': 'gym_owner',
            'gym': GymDetailSerializer(gym).data
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'super_admin':
            return Response({'role': 'super_admin', 'email': user.email})
        try:
            gym = user.gym
            current_status = get_gym_status(gym)
            gym.status = current_status
            gym.save(update_fields=['status'])
            return Response({
                'role': 'gym_owner',
                'gym': GymDetailSerializer(gym).data
            })
        except Gym.DoesNotExist:
            return Response({'error': 'Gym not found.'}, status=status.HTTP_404_NOT_FOUND)
