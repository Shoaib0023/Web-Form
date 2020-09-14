from rest_framework import serializers
from .models import Signal, Attachment


class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = (
            'id',
            'signal_id',
            'text',
            'address',
            'coordinates',
            'state',
            'category_level_name1',
            'category_level_name2',
            'category_level_name3',
            'category_level_name4',
            'email',
            'phone',
            'priority',
            'name',
            'code',
            'created_at',
            'updated_at',
        )

        read_only = (
            'category_level_name1',
            'category_level_name2',
            'category_level_name3',
            'category_level_name4',
            'created_at',
            'updated_at',
        )


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = (
            '_signal',
            'file',
            'seda_signal_id',
            'created_at',
       )
