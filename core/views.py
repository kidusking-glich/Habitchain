from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import Habit 
from .serializers import HabitSerializer


# Create your views here.
class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.object.all()
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    search_fields = ['name', 'description']
    ordering_fields =['created_at', 'difficulty']
    ordering = ['-created_at']


    def get_queryset(self):
        # return habits owned by logged-in user only
        return Habit.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)