from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("team_lead", "Team Lead"),
        ("member", "Team Member"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    position = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "users"


class Level(models.Model):
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(unique=True)
    description = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Level {self.order}: {self.name}"


class Scenario(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="scenarios")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="medium")
    video_url = models.URLField(blank=True)
    audio_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_scenarios")

    class Meta:
        ordering = ["level__order", "difficulty", "title"]

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ("multiple_choice", "Multiple Choice"),
        ("true_false", "True/False"),
        ("open_ended", "Open Ended"),
    ]
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default="multiple_choice")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text[:80]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:60]


class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="responses")
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    open_ended_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-answered_at"]


class ScenarioAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attempts")
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="attempts")
    score = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username} - {self.scenario.title} ({self.score}%)"


class UserProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="progress")
    current_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    total_scenarios_completed = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "User progress"

    def __str__(self):
        return f"{self.user.username} - Level {self.current_level}"
