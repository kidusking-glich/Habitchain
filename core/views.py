from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import Habit 
from .serializers import HabitSerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view



# Create your views here.

@extend_schema_view(
    list=extend_schema(
        summary="List_Habit",
        description="Retrive all habits for the authentication user."
    ),
    create=extend_schema(
        summary="Create Habit",
        description="Create a new habit."
    ),
    retrieve=extend_schema(
        summary="Retrieve Habit",
        description="Get a single habit by ID."
    ),
    update=extend_schema(
        summary="Update Habit",
        description="Update a habit."
    ),
    destroy=extend_schema(
        summary="Delete Habit",
        description="Delete a habit"
    )
    
)

class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]



    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [ 'title','description']
    filterset_fields = ['difficulty', 'category']
    ordering_fields =['created_at', 'difficulty']
    ordering = ['-created_at']


    def get_queryset(self):
        # return habits owned by logged-in user only
        return Habit.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


