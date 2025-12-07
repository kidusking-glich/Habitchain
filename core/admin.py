from django.contrib import admin
from .models import Habit, HabitDependency, Streak, DifficultyAdjustmentLog

# Register your models here.
admin.site.register(Habit)
admin.site.register(HabitDependency)
admin.site.register(Streak)
admin.site.register(DifficultyAdjustmentLog)

