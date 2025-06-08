"Views for the flock APIs"

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from core.models import Flock
from flock import serializers


class FlockViewSet(viewsets.ModelViewSet):
    """View for manage flock APIs."""

    serializer_class = serializers.FlockDetailSerializer
    queryset = Flock.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve flocks for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        "return serializer class for request"
        if self.action == "list":
            return serializers.FlockSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new FLOCK."""
        serializer.save(user=self.request.user)
