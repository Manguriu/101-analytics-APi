"serializer for flocks api"

from rest_framework import serializers  # type: ignore

from core.models import Flock, HealthCheck
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
        read_only_fields = ["id", "user"]

    def validate_flock(self, value):
        if value.user != self.context["request"].user:
            raise serializers.ValidationError("Current user has no rights")
        return value


class HealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCheck
        fields = [
            "id",
            "flock",
            "date",
            "symptoms",
            "treatment",
            "health_status",
            "deaths",
            "notes",
        ]

        read_only_fields = ["id"]

    def validate_flock(self, value):
        if value.user != self.context["request"].user:
            raise serializers.ValidationError("Current user has no rights")
        return value
