from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Habit, HabitCompletion, HabitDependency, Streak, DifficultyAdjustmentLog

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ['id', 'user', 'created_at', 'difficulty']

# class HabitDependencySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HabitDependency
#         fields = "__all__"

class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = [
            "id",
            "habit",
            "current_streak",
            "longest_streak",
            "last_completed_date",
        ]#"__all__"

class DifficultyAdjustmentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifficultyAdjustmentLog
        fields = "__all__"


class HabitCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitCompletion
        fields = ['id', 'habit', 'completed_at']
        read_only_fields = ['completed_at']

class HabitDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitDependency
        fields = ['id', 'habit', 'depends_on']

    def validate(self, attrs):
        habit = attrs.get('habit')
        depends_on = attrs.get('depends_on')

        # 1️ Prevent habit depending on itself

        if habit == depends_on:
            raise serializers.ValidationError("A habit cannot depend on itself.")
        
        # 2️ Prevent duplicate dependencies
        if HabitDependency.objects.filter(habit=habit, depends_on=depends_on).exists():
            raise serializers.ValidationError("This dependency already exists.")
        # 3️ Prevent reverse dependency (A → B while B → A)

        if HabitDependency.objects.filter(habit=depends_on, depends_on=habit).exists():
            raise serializers.ValidationError("Circular dependency detected.")
        
         # 4️ Prevent long circular chains (A → B → C → A)
        if self._creates_circular_dependency(habit, depends_on):
            raise serializers.ValidationError("This dependency would create a circular dependency chain.")
        return attrs
    
    # def creates_cycle(self, habit, depends_on):
    #     """
    #     Detect cycles by walking up the dependency chain.
    #     Example of cycle:
    #     A → B → C → A
    #     """
    #     current = depends_on

    #     while True:
    #         parent = HabitDependency.objects.filter(habit=current).first()
    #         if not parent:
    #             return False
    #         if parent.depends_on == habit: #cycle detected
    #             return True
    #         current = parent.depends_on

    def _creates_circular_dependency(self, habit, depends_on):

        visited = set()

        def dfs(current):
            if current == habit:
                return True
            if current in visited:
                return False
            visited.add(current)

            parents = HabitDependency.objects.filter(
                habit=current
            ).values_list('depends_on', flat=True)

            for parent_id in parents:
                parent_habit = Habit.objects.get(id=parent_id)
                if dfs(parent_habit):
                    return True
            return False    
        return dfs(depends_on)

class SteakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = {
            'id',
            'habit',
            'current_streak',
            'longest_streak',
            'last_completed_date',
            
            
        }

class StreakSegmentSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    length = serializers.IntegerField()

class StreakHistorySerializer(serializers.Serializer):
    habit_id = serializers.IntegerField()
    habit_title = serializers.CharField()
    streak_segments = StreakSegmentSerializer(many=True)
    total_completions = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
