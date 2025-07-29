"serializer for flocks api"

from rest_framework import serializers

from core.models import FinanceRecord, Flock, HealthCheck
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
            "disease",
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


class FinanceRecordSerializer(serializers.ModelSerializer):
    profit_margin = serializers.SerializerMethodField()

    def get_profit_margin(self, obj):
        calc_expenses = (
            obj.total_initial_cost
            + obj.food_expense
            + obj.water_expense
            + obj.vaccination_expense
            + obj.medicine_expense
            + obj.lab_expense
        )
        calc_revenue = obj.remaining_birds * obj.selling_price_per_bird
        return calc_revenue - calc_expenses

    class Meta:
        model = FinanceRecord
        fields = [
            "id",
            "flock",
            "batch_name",
            "number_of_initial_birds",
            "price_per_initial_bird",
            "total_initial_cost",
            "food_expense",
            "water_expense",
            "vaccination_expense",
            "medicine_expense",
            "lab_expense",
            "remaining_birds",
            "selling_price_per_bird",
            "created_at",
            "profit_margin",
        ]


class FinanceSummaryResponseSerializer(serializers.Serializer):
    flock_id = serializers.IntegerField(allow_null=True)
    batch_name = serializers.CharField()
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    profit_margin = serializers.DecimalField(max_digits=15, decimal_places=2)
    created_at = serializers.DateTimeField()
