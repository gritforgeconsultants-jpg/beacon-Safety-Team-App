from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    Choice,
    Level,
    Question,
    Response,
    Scenario,
    ScenarioAttempt,
    User,
    UserProgress,
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "position", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Safety Team", {"fields": ("role", "position")}),
    )


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "passing_score")
    ordering = ("order",)


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "difficulty", "created_at")
    list_filter = ("level", "difficulty")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "scenario", "question_type", "order")
    list_filter = ("question_type",)
    inlines = [ChoiceInline]


@admin.register(ScenarioAttempt)
class ScenarioAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "scenario", "score", "passed", "started_at")
    list_filter = ("passed",)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "current_level", "total_scenarios_completed")
