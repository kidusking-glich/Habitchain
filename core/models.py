from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Habit(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", 'Easy'),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description =models.TextField(blank=True)
    difficulty = models.IntegerField(default=1)
    category = models.CharField(max_length=100, blank=True)
    base_score = models.IntegerField(default=10)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.title
    
class HabitDependency(models.Model):
    habit = models.ForeignKey(Habit, related_name= "main_habit", on_delete=models.CASCADE)
    depends_on = models.ForeignKey(Habit, related_name="dependency", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.habit.title} depends on {self.depends_on.title}"
    
class Streak(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    date_completed = models.DateField()
    current_streak = models.IntegerField(default=0)
    streak_broken = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.habit.title} - {self.current_streak} days"
    
class DifficultyAdjustmentLog(models.Model):
    Habit =models.ForeignKey(Habit, on_delete=models.CASCADE)
    old_difficulty = models.CharField(max_length=10)
    new_difficulty = models.CharField(max_length=10)
    reason =models.TextField()
    timestamp =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.habit.name} adjusted {self.old_difficulty} → {self.new_difficulty}"

class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="completions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('habit', 'completed_at')
    