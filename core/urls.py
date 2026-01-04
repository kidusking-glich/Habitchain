from rest_framework.routers import DefaultRouter
from .views import HabitCompletationViewSet, HabitDependencyViewSet, HabitViewSet, StreakViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')
router.register(r'completions', HabitCompletationViewSet, basename='completion')
router.register(r'dependencies', HabitDependencyViewSet, basename='dependencies')


streak_view = StreakViewSet.as_view({
    "get": "retrieve",
    "post": "create",
})

streak_history_view = StreakViewSet.as_view({
    "get": "list",
})

urlpatterns = router.urls + [
    path("habits/<int:pk>/streak/", streak_view, name="habit-streak"),
    path("habits/<int:pk>/complete/", streak_view, name="habit-complete"),
    path("habits/<int:pk>/streak_history/", streak_history_view, name="habitcompletion-straek-history"),
]


