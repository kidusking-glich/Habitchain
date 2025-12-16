from rest_framework.routers import DefaultRouter
from .views import HabitCompletationViewSet, HabitViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')
router.register(r'completions', HabitCompletationViewSet, basename='completion')


urlpatterns = router.urls
