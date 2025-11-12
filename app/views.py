from django.utils import timezone
import math

from rest_framework import viewsets, status, generics, permissions
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response

from app.models import calc_calories, RunLocation, Run, Territory, User
from app.serializers import RunSerializer, RunLocationSerializer, TerritorySerializer, UserSerializer, \
    RegisterSerializer


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Run.objects.filter(user=self.request.user).order_by('-date')

    def create(self, request, *args, **kwargs):
        user = request.user
        today = timezone.localdate()

        run, created = Run.objects.get_or_create(user=user, date=today)

        serializer = self.get_serializer(run)
        return Response(serializer.data, status=200 if not created else 201)

    @action(detail=True, methods=['post'])
    def add_location(self, request, pk=None):
        run = self.get_object()
        lat = request.data.get("lat")
        lon = request.data.get("lon")

        if lat is None or lon is None:
            return Response({"error": "lat and lon required"}, status=400)

        RunLocation.objects.create(run=run, lat=lat, lon=lon)

        return Response({"message": "location added"}, status=200)

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        run = self.get_object()

        locations = run.locations.order_by("timestamp")
        if len(locations) < 2:
            return Response({"error": "Not enough points to calculate distance"}, status=400)

        # Haversine distance
        def dist(lat1, lon1, lat2, lon2):
            R = 6371000
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
            return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

        total_dist = 0
        for i in range(len(locations) - 1):
            p1 = locations[i]
            p2 = locations[i + 1]
            total_dist += dist(p1.lat, p1.lon, p2.lat, p2.lon)

        run.distance = round(total_dist, 2)

        duration_seconds = (locations.last().timestamp - locations.first().timestamp).total_seconds()
        run.duration = int(duration_seconds)

        run.calories = calc_calories(run.distance, run.duration, run.user.weight)
        run.save()

        return Response(RunSerializer(run).data, status=200)

    def update(self, *args, **kwargs):
        return Response({'detail': 'Editing run data is not allowed.'}, status=405)

    def destroy(self, *args, **kwargs):
        return Response({'detail': 'Deleting run data is not allowed.'}, status=405)


class RunLocationViewSet(viewsets.ModelViewSet):
    queryset = RunLocation.objects.all()
    serializer_class = RunLocationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        run_id = request.data.get('run')
        lat = request.data.get('lat')
        lon = request.data.get('lon')

        if not Run.objects.filter(id=run_id, user=request.user).exists():
            return Response({"detail": "You can't attach location to another user's run."},
                            status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)

    def update(self, *args, **kwargs):
        return Response({'detail': 'Editing locations is not allowed.'}, status=405)

    def destroy(self, *args, **kwargs):
        return Response({'detail': 'Deleting locations is not allowed.'}, status=405)


class TerritoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Territory.objects.all()
    serializer_class = TerritorySerializer
    permission_classes = [IsAuthenticated]


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

