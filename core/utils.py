from datetime import datetime, timedelta, date
from .models import Streak

def update_streak(streak: Streak):
    today = date.today()

    if streak.last_completed_date is None:
        streak.current_streak = 1
        streak.longest_streak = 1
        streak.last_completed_date = today
        streak.save()
        return streak
    
    last = streak.last_completed_date

    #alerady completed today
    if last == today:
        return streak
    #continue streak
    if last == today - timedelta(days=1):
        streak.current_streak += 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        
        streak.last_completed_date = today
        streak.save()
        return streak
    #missed a day, reset streak
    streak.current_streak = 1
    streak.longest_streak = max(streak.longest_streak, 1)
    streak.last_completed_date = today
    streak.save()
    return streak