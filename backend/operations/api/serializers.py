
from rest_framework import serializers

from .. import models


class PromotionCodeSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = models.PromotionCode
        fields = (
            'value', 'extra', 'is_active', 'expired_at',
            'is_available',
        )
        extra_kwargs = {
            'value': {'read_only': True, },
            'extra': {'read_only': True, },
            'is_active': {'read_only': True, },
            'expired_at': {'read_only': True, },
        }

    def get_is_available(self, obj):
        return obj.is_available
