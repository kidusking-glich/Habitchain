from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Habit(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, "Medium"),
        (3, "Hard"),
        (4, "Very Hard"),
        (5, "Extreme"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    title = models.CharField(max_length=255)
    description =models.TextField(blank=True)
    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        default=1
    )
    category = models.CharField(max_length=100, blank=True)
    base_score = models.IntegerField(default=10)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.title
    
class HabitDependency(models.Model):
    habit = models.ForeignKey(Habit, related_name= "dependencies", on_delete=models.CASCADE)
    depends_on = models.ForeignKey(Habit, related_name="required_for", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('habit', 'depends_on')
        verbose_name = "Habit Dependency"
        verbose_name_plural = "Habit Dependencies"

    def __str__(self):
        return f"{self.habit.title} depends on {self.depends_on.title}"
    
class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="completions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('habit', 'completed_at')
    def __str__(self):
        return f"{self.user.username} completed  {self.habit.title} on {self.completed_at}"
    

class Streak(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="streaks")
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="streaks")
    #habit = models.OneToOneField(Habit, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)  
    longest_streak = models.IntegerField(default=0)
    
    last_completed_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'habit')

    def __str__(self):
        return f"{self.user.username} - {self.habit.title} ({self.current_streak} days)"
    
class DifficultyAdjustmentLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="difficulty_logs")
    old_difficulty = models.IntegerField()
    new_difficulty = models.IntegerField()
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.habit.title}: {self.old_difficulty} → {self.new_difficulty}"



    
