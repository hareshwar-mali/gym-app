from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, ManualSubscriptionPayment


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'duration_days', 'price', 'is_active']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan_name', 'start_date', 'end_date', 'status', 'created_at']


class ManualPaymentSerializer(serializers.ModelSerializer):
    gym_name = serializers.CharField(source='gym.gym_name', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = ManualSubscriptionPayment
        fields = [
            'id', 'gym_name', 'plan_name', 'amount', 'payment_mode',
            'transaction_id', 'payment_date', 'remarks',
            'verified_by', 'verified_at', 'status', 'created_at'
        ]


class ActivatePlanSerializer(serializers.Serializer):
    gym_id = serializers.IntegerField()
    plan_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = serializers.ChoiceField(choices=['upi', 'bank_transfer', 'cash', 'other'])
    transaction_id = serializers.CharField(required=False, allow_blank=True)
    payment_date = serializers.DateField()
    remarks = serializers.CharField(required=False, allow_blank=True)
