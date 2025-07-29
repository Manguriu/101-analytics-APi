from datetime import datetime, time
from typing import Counter
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets  # type: ignore
from rest_framework.authentication import TokenAuthentication  # type: ignore
from rest_framework.permissions import IsAuthenticated  # type: ignore
from rest_framework.authtoken.models import Token  # type: ignore
from rest_framework.views import APIView  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.exceptions import PermissionDenied  # type: ignore
from rest_framework.decorators import action  # type: ignore
from core.models import FinanceRecord, Flock, HealthCheck
from flock import serializers
from core.models import FlockSummary
from flock.serializers import (
    FinanceRecordSerializer,
    FinanceSummaryResponseSerializer,
    FlockSummarySerializer,
    HealthCheckSerializer,
)
from statistics import mean
from django.utils import timezone
from django.db.models import Sum


@method_decorator(csrf_exempt, name="dispatch")
class FlockViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FlockDetailSerializer
    queryset = Flock.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.FlockSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"detail": "Successfully logged out."}, status=200)
        except Token.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=400)


class FlockSummaryViewSet(viewsets.ModelViewSet):
    serializer_class = FlockSummarySerializer
    queryset = FlockSummary.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(flock__user=self.request.user)

    def perform_create(self, serializer):
        # Optionally, validate that the flock belongs to the user
        flock = serializer.validated_data["flock"]
        if flock.user != self.request.user:
            raise PermissionDenied("This flock does not belong to you.")
        serializer.save()

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        flocks = Flock.objects.filter(user=request.user)
        total_flocks = flocks.count()
        total_birds = sum(f.initial_count for f in flocks)

        total_estimated_weight = 0
        for flock in flocks:
            latest_summary = flock.summaries.order_by("-date").first()
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
        return Response(
            {
                "total_flocks": total_flocks,
                "total_birds": total_birds,
                "estimated_total_weight": round(total_estimated_weight, 2),
            }
        )


class FlockSummaryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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

            # Sum feed, water, deaths for this flock
            total_feed += sum(s.total_feed for s in summaries)
            total_water += sum(s.total_water for s in summaries)
            total_deaths += sum(s.deaths for s in summaries)

            # Calculate estimated weight from latest summary
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


class HealthCheckViewSet(viewsets.ModelViewSet):
    serializer_class = HealthCheckSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HealthCheck.objects.filter(flock__user=self.request.user)

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


class HealthCheckSummaryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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

        summary_data = {
            "total_deaths": total_deaths,
            "most_common_disease": most_common_disease,
            "health_percentage": round(health_percentage, 2),
        }

        return Response(summary_data)


class FinanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = FinanceRecordSerializer
    queryset = FinanceRecord.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FinanceRecord.objects.filter(flock__user=self.request.user)

        # Filtering by flock ID
        flock_id = self.request.query_params.get("flock")
        if flock_id:
            queryset = queryset.filter(flock_id=flock_id)

        # date filtering
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        return queryset


class FinanceSummaryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
                print(f"Start: {start}, End: {end}")
                print(
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
