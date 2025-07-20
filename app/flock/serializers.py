"serializer for flocks api"

from rest_framework import serializers  # type: ignore

from core.models import Flock
from core.models import FlockSummary


class FlockSerializer(serializers.ModelSerializer):
    "serializer for flock"

    class Meta:
        model = Flock
        fields = [
            "id",
            "batch_id",
            "batch_name",
            "date_acquired",
            "initial_count",
            "breed",
        ]
        read_only_fields = [
            "id",
            "batch_id",
        ]


class FlockDetailSerializer(FlockSerializer):
    """Extension of the flock serializer with extra fields."""

    class Meta(FlockSerializer.Meta):
        fields = FlockSerializer.Meta.fields + ["batch_name"]


class LogoutSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)


class FlockSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = FlockSummary
        fields = [
            "id",
            "flock",
            "day",
            "date",
            "weight_1",
            "weight_2",
            "weight_3",
            "weight_4",
            "weight_5",
            "total_feed",
            "total_water",
            "deaths",
        ]
