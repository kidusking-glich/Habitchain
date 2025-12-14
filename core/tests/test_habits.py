from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from ..models import Habit

User = get_user_model()


class HabitTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            password="pass1234"
        )
        self.client.login(username="test", password="pass1234")

    def test_list_habits(self):
        url = reverse('habit-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_habit(self):
        url = reverse('habit-list')
        data = {
            "title": "Drink Water",
            "description": "Drink 8 glasses daily"
        }
        response = self.client.post(url, data)
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(response.data)

def test_update_habit(self):
    habit = Habit.objects.create(
        title="Old Title",
        description="Old description",
        user=self.user
    )

    url = reverse('habit-detail', args=[habit.id])
    data = {"title": "Updated Title"}

    response = self.client.patch(url, data)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["title"], "Updated Title")


def test_user_cannot_delete_other_users_habit(self):
    other_user = User.objects.create_user(
        username="other",
        password="pass1234"
    )

    habit = Habit.objects.create(
        title="Private Habit",
        description="Not yours",
        user=other_user
    )

    url = reverse('habit-detail', args=[habit.id])
    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
