# from datetime import timedelta
# from django.contrib.auth import get_user_model
# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.urls import reverse
# from ..models import Habit

# User = get_user_model()


# class HabitTests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(
#             username="test",
#             password="pass1234"
#         )
#         self.client.login(username="test", password="pass1234")

#     def test_list_habits(self):
#         url = reverse('habit-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_create_habit(self):
#         url = reverse('habit-list')
#         data = {
#             "title": "Drink Water",
#             "description": "Drink 8 glasses daily"
#         }
#         response = self.client.post(url, data)
#         #print(response.data)

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         #print(response.data)

#     def test_update_habit(self):
#         habit = Habit.objects.create(
#             title="Old Title",
#             description="Old description",
#             user=self.user
#         )

#         url = reverse('habit-detail', args=[habit.id])
#         data = {"title": "Updated Title"}

#         response = self.client.patch(url, data)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["title"], "Updated Title")


#     def test_user_cannot_delete_other_users_habit(self):
#         other_user = User.objects.create_user(
#             username="other",
#             password="pass1234"
#         )

#         habit = Habit.objects.create(
#             title="Private Habit",
#             description="Not yours",
#             user=other_user
#         )

#         url = reverse('habit-detail', args=[habit.id])
#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_filter_habits_by_difficulty(self):
#         # Clear any existing habits first
#         Habit.objects.all().delete()
        
#         Habit.objects.create(
#             title = "Easy_Habit",
#             difficulty = 1,
#             user = self.user
#         )
#         Habit.objects.create(
#             title = "Hard_Habit",
#             difficulty = 3,
#             user = self.user
#         )
        
#         url = reverse('habit-list') + '?difficulty=1'
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 1)

#     def test_search_habits(self):
#         # Clear any existing habits first
#         Habit.objects.all().delete()
        
#         Habit.objects.create(
#             title = "Drink Water",
#             description ="Hydration",
#             user = self.user 
#         )
#         Habit.objects.create(
#             title = "Read Book",
#             description = "focus",
#             user = self.user
#         )

#         url = reverse('habit-list') + '?search=Water'
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 1)
#         self.assertIn("Drink Water", response.data['results'][0]["title"])
    
#     def test_complete_habit_creates_streak(self):
#         habit = Habit.objects.create(title="Test Habit", user=self.user)
#         url = reverse('habitcompletion-list')
#         data = {"habit": habit.id}
        
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
#         # Verify streak created
#         from ..models import Streak
#         streak = Streak.objects.get(habit=habit)
#         self.assertEqual(streak.current_streak, 1)

#     def test_habit_dependency_blocks_completion(self):
#         habit1 = Habit.objects.create(title="Habit1", user=self.user)
#         habit2 = Habit.objects.create(title="Habit2", user=self.user)
        
#         from ..models import HabitDependency
#         HabitDependency.objects.create(habit=habit2, depends_on=habit1)
        
#         url = reverse('habitcompletion-list')
#         data = {"habit": habit2.id}
        
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 400)
#         self.assertIn("Complete 'Habit1' first", response.data["error"])

#     def test_streak_increments_on_consecutive_days(self):
#         habit = Habit.objects.create(title="Habit Streak", user=self.user)
#         url = reverse('habitcompletion-list')
        
#         # Complete today
#         self.client.post(url, {"habit": habit.id})
        
#         # Simulate streak continuation
#         from ..models import Streak
#         streak = Streak.objects.get(habit=habit)
#         streak.last_completed_date -= timedelta(days=1)
#         streak.save()
        
#         self.client.post(url, {"habit": habit.id})
#         streak.refresh_from_db()
#         self.assertEqual(streak.current_streak, 2)

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from django.utils import timezone

from ..models import Habit, HabitCompletion, HabitDependency, Streak

User = get_user_model()

class HabitTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="test", password="pass1234")
        self.other_user = User.objects.create_user(username="other", password="pass1234")

        # Login user via API to get JWT token
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {"username": "test", "password": "pass1234"})
        self.token = response.data['access']
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    # ----------------- Habit CRUD -----------------
    def test_list_habits(self):
        url = reverse('habit-list')
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_habit(self):
        url = reverse('habit-list')
        data = {"title": "Drink Water", "description": "Drink 8 glasses daily"}
        response = self.client.post(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Drink Water")

    def test_update_habit(self):
        habit = Habit.objects.create(title="Old Title", user=self.user)
        url = reverse('habit-detail', args=[habit.id])
        response = self.client.patch(url, {"title": "Updated Title"}, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Updated Title")

    def test_user_cannot_delete_other_users_habit(self):
        habit = Habit.objects.create(title="Private Habit", user=self.other_user)
        url = reverse('habit-detail', args=[habit.id])
        response = self.client.delete(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------- Filtering / Search -----------------
    def test_filter_habits_by_difficulty(self):
        Habit.objects.all().delete()
        Habit.objects.create(title="Easy_Habit", difficulty=1, user=self.user)
        Habit.objects.create(title="Hard_Habit", difficulty=3, user=self.user)

        url = reverse('habit-list') + '?difficulty=1'
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Easy_Habit")

    def test_search_habits(self):
        Habit.objects.all().delete()
        Habit.objects.create(title="Drink Water", description="Hydration", user=self.user)
        Habit.objects.create(title="Read Book", description="Focus", user=self.user)

        url = reverse('habit-list') + '?search=Water'
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn("Drink Water", response.data['results'][0]["title"])

    # ----------------- HabitCompletion & Streak -----------------
    def test_complete_habit_creates_streak(self):
        habit = Habit.objects.create(title="Test Habit", user=self.user)
        url = reverse('habit-complete', args=[habit.id])

        response = self.client.post(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that streak was created with user parameter
        streak = Streak.objects.get(user=self.user, habit=habit)
        self.assertEqual(streak.current_streak, 1)
        self.assertEqual(streak.longest_streak, 1)

    def test_streak_increments_on_consecutive_days(self):
        habit = Habit.objects.create(title="Habit Streak", user=self.user)
        url = reverse('habit-complete', args=[habit.id])
        self.client.post(url, **self.auth_headers)

        streak = Streak.objects.get(user=self.user, habit=habit)
        streak.last_completed_date -= timedelta(days=1)
        streak.save()

        self.client.post(url, **self.auth_headers)
        streak.refresh_from_db()
        self.assertEqual(streak.current_streak, 2)
        self.assertEqual(streak.longest_streak, 2)

    def test_streak_resets_after_missed_day(self):
        habit = Habit.objects.create(title="Reset Habit", user=self.user)
        url = reverse('habit-complete', args=[habit.id])
        
        print(f"DEBUG TEST: Initial completion")
        self.client.post(url, **self.auth_headers)

        streak = Streak.objects.get(user=self.user, habit=habit)
        print(f"DEBUG TEST: After initial completion - current={streak.current_streak}, longest={streak.longest_streak}")
        
        print(f"DEBUG TEST: Setting longest_streak to 5...")
        streak.last_completed_date -= timedelta(days=3)
        streak.current_streak = 5
        print(f"DEBUG TEST: Before save - current={streak.current_streak}, longest={streak.longest_streak}")
        print(f"DEBUG TEST: Before save - longest_streak value: {streak.longest_streak}, type: {type(streak.longest_streak)}")
        
        streak.longest_streak = 5
        print(f"DEBUG TEST: After setting longest_streak=5 - current={streak.current_streak}, longest={streak.longest_streak}")
        print(f"DEBUG TEST: longest_streak value: {streak.longest_streak}, type: {type(streak.longest_streak)}")
        
        streak.save()
        print(f"DEBUG TEST: After save - current={streak.current_streak}, longest={streak.longest_streak}")
        
        # Force reload from database to see what was actually saved
        streak_from_db = Streak.objects.get(user=self.user, habit=habit)
        print(f"DEBUG TEST: After database reload - current={streak_from_db.current_streak}, longest={streak_from_db.longest_streak}")

        print(f"DEBUG TEST: Second completion")
        self.client.post(url, **self.auth_headers)
        
        streak.refresh_from_db()
        print(f"DEBUG TEST: After refresh_from_db - current={streak.current_streak}, longest={streak.longest_streak}")
        
        self.assertEqual(streak.current_streak, 1)
        self.assertEqual(streak.longest_streak, 5)

    # ----------------- Habit Dependency -----------------
    def test_habit_dependency_blocks_completion(self):
        habit1 = Habit.objects.create(title="Habit1", user=self.user)
        habit2 = Habit.objects.create(title="Habit2", user=self.user)
        HabitDependency.objects.create(habit=habit2, depends_on=habit1)

        url = reverse('habit-complete', args=[habit2.id])
        response = self.client.post(url, **self.auth_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Complete 'Habit1' first", response.data["error"])

        # ----------------- StreakViewSet / Swagger Endpoints -----------------
    def test_get_streak_info(self):
        # Create habit and streak
        habit = Habit.objects.create(title="Habit Streak Info", user=self.user)
        url = reverse('habit-streak', args=[habit.id])  # GET /habits/{id}/streak/

        # Initially, streak should be created with 0
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('current_streak', response.data)
        self.assertIn('longest_streak', response.data)
        self.assertEqual(response.data['current_streak'], 0)
        self.assertEqual(response.data['longest_streak'], 0)

    def test_post_complete_habit_updates_streak(self):
        habit = Habit.objects.create(title="Complete Habit", user=self.user)
        url = reverse('habit-complete', args=[habit.id])  # POST /habits/{id}/complete/

        response = self.client.post(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Streak should now be 1
        streak = Streak.objects.get(habit=habit)
        self.assertEqual(streak.current_streak, 1)
        self.assertEqual(streak.longest_streak, 1)

        # Posting again the same day is idempotent
        response = self.client.post(url, **self.auth_headers)
        streak.refresh_from_db()
        self.assertEqual(streak.current_streak, 1)
        self.assertEqual(streak.longest_streak, 1)

    def test_post_complete_with_dependency(self):
        habit1 = Habit.objects.create(title="Required Habit", user=self.user)
        habit2 = Habit.objects.create(title="Dependent Habit", user=self.user)
        HabitDependency.objects.create(habit=habit2, depends_on=habit1)

        url = reverse('habit-complete', args=[habit2.id])
        response = self.client.post(url, **self.auth_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Complete 'Required Habit' first", response.data['error'])

        # Complete the required habit first
        complete_url = reverse('habit-complete', args=[habit1.id])
        self.client.post(complete_url, **self.auth_headers)

        # Now dependent habit can be completed
        response = self.client.post(url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        streak2 = Streak.objects.get(habit=habit2)
        self.assertEqual(streak2.current_streak, 1)

    def test_streak_history_endpoint_placeholder(self):
        habit = Habit.objects.create(title="History Habit", user=self.user)
        url = reverse('habitcompletion-straek-history', args=[habit.id])  # GET /habits/{id}/straek_history/
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "streak history logic not implemented yet")

