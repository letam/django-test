from rest_framework import serializers

from .models import Happiness


class HappinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Happiness
        fields = ['date', 'level']

    def validate_level(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                'Happiness level must be between 1 and 5'
            )
        return value
