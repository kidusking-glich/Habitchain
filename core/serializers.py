from rest_framework import serializers
from .models import Habit, HabitCompletion, HabitDependency, Streak, DifficultyAdjustmentLog


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

        # 1️⃣ Prevent habit depending on itself

        if habit == depends_on:
            raise serializers.ValidationError("A habit cannot depend on itself.")
        
        # 2️⃣ Prevent duplicate dependencies
        if HabitDependency.objects.filter(habit=habit, depends_on=depends_on).exists():
            raise serializers.ValidationError("This dependency already exists.")
        # 3️⃣ Prevent reverse dependency (A → B while B → A)

        if HabitDependency.objects.filter(habit=depends_on, depends_on=habit).exists():
            raise serializers.ValidationError("Circular dependency detected.")
        
         # 4️⃣ Prevent long circular chains (A → B → C → A)
        if self._creates_circular_dependency(habit, depends_on):
            raise serializers.ValidationError("This dependency would create a circular dependency chain.")
        return attrs
    
    def creates_cycle(self, habit, depends_on):
        """
        Detect cycles by walking up the dependency chain.
        Example of cycle:
        A → B → C → A
        """
        current = depends_on

        while True:
            parent = HabitDependency.objects.filter(habit=current).first()
            if not parent:
                return False
            if parent.depends_on == habit: #cycle detected
                return True
            current = parent.depends_on