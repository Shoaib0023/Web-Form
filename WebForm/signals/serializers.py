from rest_framework import serializers
from .models import Signal


class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = (
            'id',
            'text',
            'address',
            'coordinates',
            'state',
            'email',
            'phone',
            'priority',
            'file',
            'name',
            'code',
            'kenmark',
            'created_at',
            'updated_at',
        )

        read_only = (
            'kenmark',
            'created_at',
            'updated_at',
        )
