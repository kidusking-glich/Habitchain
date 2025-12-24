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
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default="easy"
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
        return f"{self.user.username} completed on {self.habit.title}"
    

class Streak(models.Model):
    habit = models.OneToOneField(Habit, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)  
    longest_streak = models.IntegerField(default=0)
    
    last_completed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.habit.title} -{self.current_streak} day streak"
    
class DifficultyAdjustmentLog(models.Model):
    Habit =models.ForeignKey(Habit, on_delete=models.CASCADE)
    old_difficulty = models.CharField(max_length=10)
    new_difficulty = models.CharField(max_length=10)
    reason =models.TextField()
    timestamp =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.habit.title} adjusted {self.old_difficulty} → {self.new_difficulty}"



    
