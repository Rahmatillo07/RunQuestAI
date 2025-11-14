from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver


class User(AbstractUser):
    height = models.PositiveIntegerField(null=True, blank=True)
    weight = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.username


class Territory(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    center_lat = models.FloatField()
    center_lon = models.FloatField()
    radius = models.FloatField(default=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.owner.username


class Run(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='runs')
    date = models.DateField()
    distance = models.FloatField(default=0)
    duration = models.PositiveIntegerField(default=0)
    calories = models.FloatField(null=True, blank=True)
    territory = models.ForeignKey(Territory, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['territory', 'date']),
        ]
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_user_date_run')
        ]

    def __str__(self):
        return f"{self.user} | {self.date} | {self.distance}m"


def calc_calories(distance, duration, weight):
    if not weight:
        weight = 70
    if duration == 0:
        return 0

    kmh = (distance / 1000) / (duration / 3600)
    if kmh < 7:
        met = 6
    elif kmh < 9:
        met = 8.3
    elif kmh < 11:
        met = 10
    else:
        met = 12.5

    hours = duration / 3600
    return met * weight * hours


@receiver(pre_save, sender=Run)
def set_calories(sender, instance, **kwargs):
    if instance.calories in (None, 0):
        weight = instance.user.weight
        instance.calories = round(calc_calories(instance.distance, instance.duration, weight), 1)


class RunLocation(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='locations')
    lat = models.FloatField()
    lon = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.run.user} | {self.lat}, {self.lon}"
