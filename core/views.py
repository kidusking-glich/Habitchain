from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import date 
from .models import Habit, HabitCompletion, HabitDependency, Streak
from .serializers import HabitCompletionSerializer, HabitDependencySerializer, HabitSerializer, StreakSerializer
from .utils import evaluate_difficulty, update_streak
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView

from core import serializers

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




# Create your views here.

@extend_schema_view(
    list=extend_schema(tags=["Habit Completions"]),
    create=extend_schema(tags=["Habit Completions"]),
)

#login endpoint 
@extend_schema(
    tags=["Authentication"],
    summary="login using username and password",
    description="returns access and refresh JWT tokens."
)

class CustomTokenObtainPairView(TokenObtainPairView):
    pass


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
    permission_classes = [IsAuthenticated]



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

@extend_schema(
    description="Difficulty automatically adjusts based on recent completion performance."
)

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
    permission_classes = [IsAuthenticated]
  

    def get_queryset(self):
        queryset = HabitCompletion.objects.filter(user=self.request.user)
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



class HabitDependencyViewSet(viewsets.ModelViewSet):
    queryset = HabitDependency.objects.all()
    serializer_class = HabitDependencySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HabitDependency.objects.filter(habit__user=self.request.user)

    def perform_create(self, serializer):
        habit= serializer.validated_data['habit']
        depends_on = serializer.validated_data['depends_on']

        #prevent self.dependency
        if habit == depends_on:
            raise serializers.ValidationError("A habit cannot depend on itself.")
            
        #prevent circular dependencies
        if HabitDependency.objects.filter(habit=depends_on, depends_on=habit).exists():
            raise serializers.ValidationError("Circular dependency are not allowed.")

        #ownership check
        if habit.user != self.request.user or depends_on.user != self.request.user:
            raise serializers.ValidationError("Both habits must belong to you.")
        # if habit.user != self.request.user:
        #     raise serializers.ValidationError("You can only add dependencies for your own habits.")
        
        # if depends_on.user != self.request.user:
        #     raise serializers.ValidationError("Dependency habit must also belong to you.")
        
        serializer.save()


class StreakViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # GET /habits/{id}/streak/
    def retrieve(self, request, pk=None):
        habit = get_object_or_404(Habit, pk=pk, user=request.user)

        streak, _ = Streak.objects.get_or_create(
            user=request.user,
            habit=habit,
            defaults={
                "current_streak": 0,
                "longest_streak": 0
            }
        )

        serializer = StreakSerializer(streak)
        return Response(serializer.data)

    # GET /habits/{id}/streak_history/
    def list(self, request, pk=None):
        return Response({"message": "streak history logic not implemented yet"})

    # POST /habits/{id}/complete/
    def create(self, request, pk=None):
        habit = get_object_or_404(Habit, pk=pk, user=request.user)

        # Dependency enforcement
        dependencies = HabitDependency.objects.filter(habit=habit)
        for dep in dependencies:
            completed_today = HabitCompletion.objects.filter(
                habit=dep.depends_on,
                user=request.user,
                completed_at=date.today()
            ).exists()

            if not completed_today:
                return Response(
                    {"error": f"Complete '{dep.depends_on.title}' first."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create completion (idempotent)
        HabitCompletion.objects.get_or_create(
            habit=habit,
            user=request.user,
            completed_at=date.today()
        )

        streak, _ = Streak.objects.get_or_create(
            user=request.user,
            habit=habit,
            defaults={
                "current_streak": 0,
                "longest_streak": 0
            }
        )
        updated_streak = update_streak(streak)
        evaluate_difficulty(habit)

        serializer = StreakSerializer(updated_streak)
        return Response(serializer.data, status=status.HTTP_200_OK)
