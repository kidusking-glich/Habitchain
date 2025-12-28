from datetime import datetime, timedelta, date
from django.utils import timezone
from .models import Streak
from .models import HabitCompletion, DifficultyAdjustmentLog

def update_streak(streak: Streak):
    #today = date.today()
    today = timezone.localdate()
    
    # Debug: print the streak values before processing
    print(f"DEBUG: update_streak called with streak id={streak.id}")
    print(f"DEBUG: current_streak={streak.current_streak}, longest_streak={streak.longest_streak}")
    print(f"DEBUG: last_completed_date={streak.last_completed_date}, today={today}")

    if streak.last_completed_date is None:
        # First time completing - set current to 1, and set longest to 1 if it's still 0 (default)
        print(f"DEBUG: First time completing, setting current_streak=1")
        streak.current_streak = 1
        # Only set longest_streak if it's still the default value of 0
        if streak.longest_streak == 0:  # Only set if it's still the default value
            print(f"DEBUG: Setting longest_streak=1 (was 0)")
            streak.longest_streak = 1
        else:
            print(f"DEBUG: Not changing longest_streak, keeping {streak.longest_streak}")
        # Don't change longest_streak if it already has a higher value
        streak.last_completed_date = today
        streak.save()
        return streak
    
    # last = streak.last_completed_date
    # yesterday = today - timedelta(days=1)
    #already updated today
    if streak.last_completed_date == today:
        print(f"DEBUG: Already completed today, returning early")
        return streak

    #CONSEQUATIVE DAYS LOGIC
    if streak.last_completed_date == today - timedelta(days=1):
        print(f"DEBUG: Consecutive day, incrementing current_streak")
        streak.current_streak += 1
    else:
        #missed a day or more
        print(f"DEBUG: Missed days, resetting current_streak to 1")
        streak.current_streak = 1
        # Don't change longest_streak when resetting current_streak

    #update longest streak
    if streak.current_streak > streak.longest_streak:
        print(f"DEBUG: New longest streak! Setting longest_streak={streak.current_streak}")
        streak.longest_streak = streak.current_streak
    else:
        print(f"DEBUG: current_streak ({streak.current_streak}) <= longest_streak ({streak.longest_streak}), keeping longest_streak as is")
    # If current_streak <= longest_streak, keep longest_streak as is
    

    
    #streak.current_streak = 1
    streak.last_completed_date = today
    streak.save()
    print(f"DEBUG: Final values: current_streak={streak.current_streak}, longest_streak={streak.longest_streak}")
    return streak


def evaluate_difficulty(habit):
    today = timezone.localdate()
    week_ago = today - timedelta(days=6)

    completions = HabitCompletion.objects.filter(
        habit=habit,
        completed_at__range=[week_ago, today]
    ).count()

    # Handle both old string and new integer difficulty values
    old = habit.difficulty
    if isinstance(old, str):
        # Convert old string values to integers for backward compatibility
        difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
        old = difficulty_map.get(old, 1)
    
    new = old

    if completions >= 6:
        new = min(old + 1, 5)
    elif completions <= 2:
        new = max(old - 1, 1)

    if new != old:
        habit.difficulty = new
        habit.save()

        DifficultyAdjustmentLog.objects.create(
            habit=habit,
            old_difficulty=old,
            new_difficulty=new,
            reason=f"{completions}/7 completions in last week"
        )

    return habit
