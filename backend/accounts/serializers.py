from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Gym, GymProfile
from datetime import date, timedelta

User = get_user_model()


class GymRegisterSerializer(serializers.Serializer):
    gym_name = serializers.CharField(max_length=200)
    owner_name = serializers.CharField(max_length=200)
    mobile = serializers.CharField(max_length=15)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    opening_time = serializers.TimeField(required=False, allow_null=True)
    closing_time = serializers.TimeField(required=False, allow_null=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def validate_mobile(self, value):
        if Gym.objects.filter(mobile=value).exists():
            raise serializers.ValidationError('Mobile number already registered.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data['email']

        user = User.objects.create_user(email=email, password=password, role='gym_owner')

        today = date.today()
        gym = Gym.objects.create(
            user=user,
            gym_name=validated_data['gym_name'],
            owner_name=validated_data['owner_name'],
            mobile=validated_data['mobile'],
            email=email,
            address=validated_data.get('address', ''),
            city=validated_data.get('city', ''),
            state=validated_data.get('state', ''),
            opening_time=validated_data.get('opening_time'),
            closing_time=validated_data.get('closing_time'),
            status='trial_active',
            trial_start_date=today,
            trial_end_date=today + timedelta(days=7),
        )

        GymProfile.objects.create(gym=gym)
        return gym


class GymSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gym
        fields = [
            'id', 'gym_name', 'owner_name', 'mobile', 'email',
            'address', 'city', 'state', 'opening_time', 'closing_time',
            'status', 'trial_start_date', 'trial_end_date',
            'subscription_end_date', 'created_at'
        ]


class GymDetailSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()
    effective_expiry = serializers.SerializerMethodField()

    class Meta:
        model = Gym
        fields = [
            'id', 'gym_name', 'owner_name', 'mobile', 'email',
            'address', 'city', 'state', 'opening_time', 'closing_time',
            'status', 'trial_start_date', 'trial_end_date',
            'subscription_end_date', 'is_blocked',
            'days_remaining', 'effective_expiry', 'created_at'
        ]

    def get_effective_expiry(self, obj):
        if obj.subscription_end_date:
            return obj.subscription_end_date
        return obj.trial_end_date

    def get_days_remaining(self, obj):
        expiry = obj.subscription_end_date or obj.trial_end_date
        if not expiry:
            return 0
        return (expiry - date.today()).days
