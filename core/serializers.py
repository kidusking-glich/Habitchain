from rest_framework import serializers
from .models import Habit, HabitDependency, Streak, DifficultyAdjustmentLog


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ['id', 'user', 'created_at', 'difficulty']

class HabitDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitDependency
        fields = "__all__"

class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = "__all__"

class DifficultyAdjustmentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifficultyAdjustmentLog
        fields = "__all__"