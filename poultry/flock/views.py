from datetime import datetime, time
from typing import Counter
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from rest_framework import viewsets, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from poultry.core.models import FinanceRecord, Flock, HealthCheck, FlockSummary
from poultry.flock.serializers import (
    AuthTokenSerializer,
    FinanceRecordSerializer,  # Ensure this is imported
    FinanceSummaryResponseSerializer,
    FlockSerializer,
    FlockDetailSerializer,
    FlockSummarySerializer,
    FlockSummaryResponseSerializer,
    HealthCheckSerializer,
    HealthCheckSummarySerializer,
    LogoutSerializer,
)
from statistics import mean
from django.utils import timezone
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)


class CustomObtainAuthToken(generics.GenericAPIView):
    serializer_class = AuthTokenSerializer

    @extend_schema(
        responses={"200": {"token": "string"}, "400": {"non_field_errors": ["string"]}}
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "").lower().strip()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"non_field_errors": ["Both email and password are required"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email__iexact=email)
            if user.check_password(password):
                if not user.is_active:
                    return Response(
                        {"non_field_errors": ["User account is disabled"]},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"non_field_errors": ["Invalid credentials"]},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except User.DoesNotExist:
            return Response(
                {"non_field_errors": ["No account found with this email"]},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"non_field_errors": [str(e)]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class FlockViewSet(viewsets.ModelViewSet):
    serializer_class = FlockDetailSerializer
    queryset = Flock.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user).order_by("-id")
        return Flock.objects.none()

    def get_serializer_class(self):
        if self.action == "list":
            return FlockSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(responses=LogoutSerializer)
    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"detail": "Successfully logged out."}, status=200)
        except Token.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class FlockSummaryViewSet(viewsets.ModelViewSet):
    serializer_class = FlockSummarySerializer
    queryset = FlockSummary.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(flock__user=self.request.user)
        return FlockSummary.objects.none()

    def perform_create(self, serializer):
        flock = serializer.validated_data["flock"]
        if flock.user != self.request.user:
            raise PermissionDenied("This flock does not belong to you.")
        serializer.save()


class FlockSummaryView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FlockSummaryResponseSerializer

    @extend_schema(responses=FlockSummaryResponseSerializer)
    def get(self, request):
        flocks = Flock.objects.filter(user=request.user)
        total_flocks = flocks.count()
        total_birds = sum(f.initial_count for f in flocks)
        total_estimated_weight = 0
        total_feed = 0
        total_water = 0
        total_deaths = 0

        for flock in flocks:
            summaries = flock.summaries.all()
            total_feed += sum(s.total_feed for s in summaries)
            total_water += sum(s.total_water for s in summaries)
            total_deaths += sum(s.deaths for s in summaries)
            latest_summary = summaries.order_by("-date").first()
            if latest_summary:
                weights = [
                    latest_summary.weight_1,
                    latest_summary.weight_2,
                    latest_summary.weight_3,
                    latest_summary.weight_4,
                    latest_summary.weight_5,
                ]
                avg_weight = mean(weights)
                total_estimated_weight += avg_weight * flock.initial_count

        birds_alive = total_birds - total_deaths
        health_percentage = (birds_alive / total_birds * 100) if total_birds > 0 else 0

        return Response(
            {
                "total_flocks": total_flocks,
                "total_birds": total_birds,
                "total_deaths": total_deaths,
                "estimated_total_weight": round(total_estimated_weight, 2),
                "total_feed_consumed": round(total_feed, 2),
                "total_water_consumed": round(total_water, 2),
                "health_percentage": round(health_percentage, 2),
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class HealthCheckViewSet(viewsets.ModelViewSet):
    serializer_class = HealthCheckSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return HealthCheck.objects.filter(flock__user=self.request.user)
        return HealthCheck.objects.none()

    def perform_create(self, serializer):
        flock = serializer.validated_data["flock"]
        if flock.user != self.request.user:
            raise PermissionDenied("Current user has no rights to access this flock")
        serializer.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.flock.user != self.request.user:
            raise PermissionDenied("Current user has no rights to access this flock")
        serializer.save()

    @extend_schema(parameters=[{"name": "id", "type": "integer"}])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class HealthCheckSummaryView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = HealthCheckSummarySerializer

    @extend_schema(responses=HealthCheckSummarySerializer)
    def get(self, request):
        flocks = Flock.objects.filter(user=request.user)
        total_initial_birds = (
            flocks.aggregate(sum_initial=Sum("initial_count"))["sum_initial"] or 0
        )

        health_checks = HealthCheck.objects.filter(flock__user=request.user)
        total_deaths = (
            health_checks.aggregate(sum_deaths=Sum("deaths"))["sum_deaths"] or 0
        )

        diseases = [hc.disease for hc in health_checks if hc.disease]
        most_common_disease = (
            Counter(diseases).most_common(1)[0][0] if diseases else None
        )

        health_percentage = (
            ((total_initial_birds - total_deaths) / total_initial_birds * 100)
            if total_initial_birds > 0
            else 100
        )

        return Response(
            {
                "total_deaths": total_deaths,
                "most_common_disease": most_common_disease,
                "health_percentage": round(health_percentage, 2),
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class FinanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = FinanceRecordSerializer  # This should now resolve correctly
    queryset = FinanceRecord.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = FinanceRecord.objects.filter(flock__user=self.request.user)
            flock_id = self.request.query_params.get("flock")
            if flock_id:
                queryset = queryset.filter(flock_id=flock_id)
            start_date = self.request.query_params.get("start_date")
            end_date = self.request.query_params.get("end_date")
            if start_date and end_date:
                queryset = queryset.filter(created_at__range=[start_date, end_date])
            return queryset
        return FinanceRecord.objects.none()


class FinanceSummaryView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FinanceSummaryResponseSerializer

    @extend_schema(responses=FinanceSummaryResponseSerializer(many=True))
    def get(self, request):
        flock_id = request.query_params.get("flock_id")
        start_date = request.query_params.get("start")
        end_date = request.query_params.get("end")

        queryset = FinanceRecord.objects.filter(flock__user=request.user)

        if flock_id:
            queryset = queryset.filter(flock_id=flock_id)
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                start = timezone.make_aware(datetime.combine(start, time.min))
                end = timezone.make_aware(datetime.combine(end, time.max))
                queryset = queryset.filter(created_at__range=(start, end))
                logger.debug(f"Start: {start}, End: {end}")
                logger.debug(
                    f"Filtered records: {[(r.batch_name, r.created_at) for r in queryset]}"
                )
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."}, status=400
                )

        records = queryset.order_by("created_at")
        response_data = []

        for record in records:
            calc_expenses = (
                float(record.total_initial_cost)
                + float(record.food_expense)
                + float(record.water_expense)
                + float(record.vaccination_expense)
                + float(record.medicine_expense)
                + float(record.lab_expense)
            )
            calc_revenue = float(record.remaining_birds) * float(
                record.selling_price_per_bird
            )
            calc_profit = calc_revenue - calc_expenses

            response_data.append(
                {
                    "flock_id": record.flock.id,
                    "batch_name": record.batch_name,
                    "total_expenses": calc_expenses,
                    "total_revenue": calc_revenue,
                    "profit_margin": calc_profit,
                    "created_at": record.created_at.isoformat(),
                }
            )

        total_expenses_sum = sum(r["total_expenses"] for r in response_data)
        total_revenue_sum = sum(r["total_revenue"] for r in response_data)
        overall_profit = total_revenue_sum - total_expenses_sum

        response_data.append(
            {
                "flock_id": None,
                "batch_name": "Overall",
                "total_expenses": total_expenses_sum,
                "total_revenue": total_revenue_sum,
                "profit_margin": overall_profit,
                "created_at": timezone.now().isoformat(),
            }
        )

        return Response(response_data)
