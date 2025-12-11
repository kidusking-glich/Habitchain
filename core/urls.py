from rest_framework.routers import DefaultRouter
from .views import HabitViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = router.urls
