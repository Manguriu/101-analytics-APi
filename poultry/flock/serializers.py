# "serializer for flocks api"

# from rest_framework import serializers

# from poultry.core.models import FinanceRecord, Flock, HealthCheck
# from poultry.core.models import FlockSummary
# from django.contrib.auth import authenticate


# class AuthTokenSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(style={"input_type": "password"})

#     def validate(self, attrs):
#         email = attrs.get("email")
#         password = attrs.get("password")

#         if email and password:
#             user = authenticate(email=email, password=password)

#             if not user:
#                 raise serializers.ValidationError(
#                     "Unable to log in with provided credentials.", code="authorization"
#                 )

#             if not user.is_active:
#                 raise serializers.ValidationError(
#                     "User account is disabled.", code="authorization"
#                 )

#             attrs["user"] = user
#             return attrs

#         raise serializers.ValidationError(
#             "Must include 'email' and 'password'.", code="authorization"
#         )


# class FlockSerializer(serializers.ModelSerializer):
#     "serializer for flock"

#     class Meta:
#         model = Flock
#         fields = [
#             "id",
#             "batch_id",
#             "batch_name",
#             "date_acquired",
#             "initial_count",
#             "breed",
#         ]
#         read_only_fields = [
#             "id",
#             "batch_id",
#         ]


# class FlockDetailSerializer(FlockSerializer):
#     """Extension of the flock serializer with extra fields."""


# class Meta(FlockSerializer.Meta):
#     fields = FlockSerializer.Meta.fields + ["batch_name"]


# class LogoutSerializer(serializers.Serializer):
#     detail = serializers.CharField(read_only=True)


# class FlockSummarySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FlockSummary
#         fields = [
#             "id",
#             "flock",
#             "date",
#             "weight_1",
#             "weight_2",
#             "weight_3",
#             "weight_4",
#             "weight_5",
#             "total_feed",
#             "total_water",
#             "deaths",
#         ]
#         read_only_fields = ["id", "user"]

#     def validate_flock(self, value):
#         if value.user != self.context["request"].user:
#             raise serializers.ValidationError("Current user has no rights")
#         return value


# class HealthCheckSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HealthCheck
#         fields = [
#             "id",
#             "flock",
#             "date",
#             "symptoms",
#             "disease",
#             "treatment",
#             "health_status",
#             "deaths",
#             "notes",
#         ]

#         read_only_fields = ["id"]

#     def validate_flock(self, value):
#         if value.user != self.context["request"].user:
#             raise serializers.ValidationError("Current user has no rights")
#         return value


# class FinanceRecordSerializer(serializers.ModelSerializer):
#     profit_margin = serializers.SerializerMethodField()

#     def get_profit_margin(self, obj):
#         calc_expenses = (
#             obj.total_initial_cost
#             + obj.food_expense
#             + obj.water_expense
#             + obj.vaccination_expense
#             + obj.medicine_expense
#             + obj.lab_expense
#         )
#         calc_revenue = obj.remaining_birds * obj.selling_price_per_bird
#         return calc_revenue - calc_expenses

#     class Meta:
#         model = FinanceRecord
#         fields = [
#             "id",
#             "flock",
#             "batch_name",
#             "number_of_initial_birds",
#             "price_per_initial_bird",
#             "total_initial_cost",
#             "food_expense",
#             "water_expense",
#             "vaccination_expense",
#             "medicine_expense",
#             "lab_expense",
#             "remaining_birds",
#             "selling_price_per_bird",
#             "created_at",
#             "profit_margin",
#         ]


# class FinanceSummaryResponseSerializer(serializers.Serializer):
#     flock_id = serializers.IntegerField(allow_null=True)
#     batch_name = serializers.CharField()
#     total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
#     total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
#     profit_margin = serializers.DecimalField(max_digits=15, decimal_places=2)
#     created_at = serializers.DateTimeField()


from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field  # type: ignore
from poultry.core.models import FinanceRecord, Flock, HealthCheck, FlockSummary
from django.contrib.auth import authenticate
from django.utils import timezone


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials.", code="authorization"
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    "User account is disabled.", code="authorization"
                )

            attrs["user"] = user
            return attrs

        raise serializers.ValidationError(
            "Must include 'email' and 'password'.", code="authorization"
        )


class FlockSerializer(serializers.ModelSerializer):
    """Serializer for flock list view."""

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
        read_only_fields = ["id", "batch_id"]


class FlockDetailSerializer(FlockSerializer):
    """Serializer for flock detail view, extending FlockSerializer."""

    class Meta(FlockSerializer.Meta):
        fields = (
            FlockSerializer.Meta.fields
        )  # No need to add batch_name again, already included


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
        read_only_fields = ["id"]

    def validate_flock(self, value):
        if value.user != self.context["request"].user:
            raise serializers.ValidationError("Current user has no rights")
        return value


class FlockSummaryResponseSerializer(serializers.Serializer):
    """Serializer for FlockSummaryView response."""

    total_flocks = serializers.IntegerField()
    total_birds = serializers.IntegerField()
    total_deaths = serializers.IntegerField()
    estimated_total_weight = serializers.FloatField()
    total_feed_consumed = serializers.FloatField()
    total_water_consumed = serializers.FloatField()
    health_percentage = serializers.FloatField()


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


class HealthCheckSummarySerializer(serializers.Serializer):
    """Serializer for HealthCheckSummaryView response."""

    total_deaths = serializers.IntegerField()
    most_common_disease = serializers.CharField(allow_null=True)
    health_percentage = serializers.FloatField()


class FinanceRecordSerializer(serializers.ModelSerializer):
    profit_margin = serializers.SerializerMethodField()

    @extend_schema_field(float)  # Explicitly define return type for schema
    def get_profit_margin(self, obj) -> float:  # Add type hint
        calc_expenses = (
            float(obj.total_initial_cost)
            + float(obj.food_expense)
            + float(obj.water_expense)
            + float(obj.vaccination_expense)
            + float(obj.medicine_expense)
            + float(obj.lab_expense)
        )
        calc_revenue = float(obj.remaining_birds) * float(obj.selling_price_per_bird)
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
        read_only_fields = ["id", "profit_margin"]


class FinanceSummaryResponseSerializer(serializers.Serializer):
    """Serializer for FinanceSummaryView response."""

    flock_id = serializers.IntegerField(allow_null=True)
    batch_name = serializers.CharField()
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    profit_margin = serializers.DecimalField(max_digits=15, decimal_places=2)
    created_at = serializers.DateTimeField()


class LogoutSerializer(serializers.Serializer):
    """Serializer for LogoutView response."""

    detail = serializers.CharField(read_only=True)
