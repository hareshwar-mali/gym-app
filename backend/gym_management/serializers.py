from rest_framework import serializers
from .models import Member, Attendance, Payment, ClassSchedule


class MemberSerializer(serializers.ModelSerializer):
    days_left = serializers.SerializerMethodField()

    class Meta:
        model = Member
        exclude = ['gym']

    def get_days_left(self, obj):
        from datetime import date
        return (obj.membership_end_date - date.today()).days


class AttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)

    class Meta:
        model = Attendance
        exclude = ['gym']


class PaymentSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)

    class Meta:
        model = Payment
        exclude = ['gym']


class ClassScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSchedule
        exclude = ['gym']
