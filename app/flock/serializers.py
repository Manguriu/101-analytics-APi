"serializer for flocks api"

from rest_framework import serializers

from core.models import Flock


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
