from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import Habit, HabitCompletion 
from .serializers import HabitCompletionSerializer, HabitSerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from rest_framework.decorators import action
from rest_framework.response import Response




# Create your views here.

@extend_schema_view(
    list=extend_schema(tags=["Habit Completions"]),
    create=extend_schema(tags=["Habit Completions"]),
)

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


@extend_schema_view(
    list=extend_schema(
        summary="List Habit Complitation",
        description= "Retrieve all habit completions for the authenticated user.",
        parameters=[
            OpenApiParameter(
                name='habit',
                description='Filter completion by habit ID',
                required=False,
                type=int
            ),
        ],
    ),
    create=extend_schema(
        summary="Complete a Habit",
        description="Mark a habit as completed for today. A habit can only be completed once per day.",

    ),
    retrieve=extend_schema(
        summary="Retrieve Completation",
        description="Get a specific habit completion by ID.",
    ),
    destroy=extend_schema(
        summary="Delete Completion",
        description="Delete a habit completion (undo completion).",

    ),
)

@extend_schema_view(
    list=extend_schema(summary="List Habit Completions"),
    create=extend_schema(summary="Complete a Habit"),
    retrieve=extend_schema(summary="Retrieve Completation"),
    destroy=extend_schema(summary="Undo Habit Completion"),
)

class HabitCompletationViewSet(viewsets.ModelViewSet):
    serializer_class = HabitCompletionSerializer
   #permission_classes = [IsAuthenticated]
    permission_classes = [permissions.IsAuthenticated]
  

    def get_queryset(self):
        queryset = HabitCompletion.object.filter(user=self.request.user)
        habit_id = self.request.query_params.get('habit')
        if habit_id:
            queryset = queryset.filter(habit_id=habit_id)
        return queryset
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(tags=["Habit Streaks"])


    @action(detail=True, methods=['get'])
    def streak(self, request, pk=None):
        return Response({"message": "streak logic not implemented yet"})

    @extend_schema(
            summary="Get Streak History",
            description=(
                "Returns all streak segments for this habit, including start and end dates of each streak.",
                "for each streak block."
            ),
            responses={
                200: OpenApiTypes.OBJECT,
            }
            
    )
    
    @action(detail=True, methods=['get'])
    def straek_history(self, request, pk=None):
        return Response({"message": "streak history logic not implemented yet"})