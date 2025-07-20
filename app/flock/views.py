from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets  # type: ignore
from rest_framework.authentication import TokenAuthentication  # type: ignore
from rest_framework.permissions import IsAuthenticated  # type: ignore
from rest_framework.authtoken.models import Token  # type: ignore
from rest_framework.views import APIView  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.exceptions import PermissionDenied  # type: ignore
from core.models import Flock
from flock import serializers
from core.models import FlockSummary
from flock.serializers import FlockSummarySerializer
from statistics import mean


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
                "estimated_total_weight": round(total_estimated_weight, 2),
                "total_feed_consumed": round(total_feed, 2),
                "total_water_consumed": round(total_water, 2),
                "health_percentage": round(health_percentage, 2),
            }
        )
