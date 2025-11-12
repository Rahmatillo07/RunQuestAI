from datetime import date

from rest_framework import serializers
from .models import User, Territory, Run, RunLocation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'height', 'weight']


class TerritorySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Territory
        fields = ['id', 'owner', 'center_lat', 'center_lon', 'radius', 'created_at']
        read_only_fields = ['owner', 'created_at']


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ['id', 'date', 'distance', 'duration', 'calories', 'territory', 'created_at']
        read_only_fields = ['distance', 'duration', 'calories', 'territory', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        today = date.today()

        run, created = Run.objects.get_or_create(
            user=user,
            date=today,
            defaults={'distance': 0, 'duration': 0}
        )
        return run


class RunLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunLocation
        fields = ['id', 'run', 'lat', 'lon', 'timestamp']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password','weight','height']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            weight = validated_data['weight'],
            height = validated_data['height'],
        )
        return user
