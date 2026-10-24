from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import RegistrationForm
from .models import (
    Choice,
    Level,
    Question,
    Response,
    Scenario,
    ScenarioAttempt,
    UserProgress,
)


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            first_level = Level.objects.first()
            UserProgress.objects.create(user=user, current_level=first_level)
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegistrationForm()
    return render(request, "training/register.html", {"form": form})


@login_required
def dashboard(request):
    progress, _ = UserProgress.objects.get_or_create(
        user=request.user,
        defaults={"current_level": Level.objects.first()},
    )
    recent_attempts = ScenarioAttempt.objects.filter(user=request.user)[:5]
    levels = Level.objects.all()

    level_data = []
    for level in levels:
        scenarios = level.scenarios.all()
        completed = ScenarioAttempt.objects.filter(
            user=request.user,
            scenario__level=level,
            passed=True,
        ).values("scenario").distinct().count()
        level_data.append({
            "level": level,
            "total": scenarios.count(),
            "completed": completed,
            "unlocked": progress.current_level and level.order <= progress.current_level.order,
        })

    context = {
        "progress": progress,
        "recent_attempts": recent_attempts,
        "level_data": level_data,
    }
    return render(request, "training/dashboard.html", context)


@login_required
def level_detail(request, level_id):
    level = get_object_or_404(Level, pk=level_id)
    progress = UserProgress.objects.filter(user=request.user).first()

    if progress and progress.current_level and level.order > progress.current_level.order:
        return render(request, "training/locked.html", {"level": level})

    scenarios = level.scenarios.all()
    scenario_data = []
    for scenario in scenarios:
        best = ScenarioAttempt.objects.filter(
            user=request.user,
            scenario=scenario,
            passed=True,
        ).order_by("-score").first()
        scenario_data.append({
            "scenario": scenario,
            "best_score": best.score if best else None,
            "passed": best is not None,
        })

    return render(request, "training/level_detail.html", {
        "level": level,
        "scenario_data": scenario_data,
    })


@login_required
def scenario_start(request, scenario_id):
    scenario = get_object_or_404(Scenario, pk=scenario_id)
    questions = scenario.questions.all()
    return render(request, "training/scenario.html", {
        "scenario": scenario,
        "questions": questions,
    })


@login_required
def scenario_submit(request, scenario_id):
    if request.method != "POST":
        return redirect("scenario_start", scenario_id=scenario_id)

    scenario = get_object_or_404(Scenario, pk=scenario_id)
    questions = scenario.questions.all()
    total = questions.count()
    correct = 0

    attempt = ScenarioAttempt.objects.create(user=request.user, scenario=scenario)

    for question in questions:
        if question.question_type == "open_ended":
            answer_text = request.POST.get(f"question_{question.id}", "")
            Response.objects.create(
                user=request.user,
                question=question,
                open_ended_answer=answer_text,
            )
        else:
            choice_id = request.POST.get(f"question_{question.id}")
            if choice_id:
                choice = Choice.objects.filter(pk=choice_id, question=question).first()
                if choice:
                    is_correct = choice.is_correct
                    if is_correct:
                        correct += 1
                    Response.objects.create(
                        user=request.user,
                        question=question,
                        selected_choice=choice,
                        is_correct=is_correct,
                    )

    scoreable = questions.exclude(question_type="open_ended").count()
    score = int((correct / scoreable * 100)) if scoreable > 0 else 100
    passed = score >= scenario.level.passing_score

    attempt.score = score
    attempt.passed = passed
    attempt.completed_at = timezone.now()
    attempt.save()

    if passed:
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            defaults={"current_level": scenario.level},
        )
        progress.total_scenarios_completed = models.F("total_scenarios_completed") + 1
        progress.total_score = score

        all_scenarios_in_level = scenario.level.scenarios.count()
        passed_in_level = ScenarioAttempt.objects.filter(
            user=request.user,
            scenario__level=scenario.level,
            passed=True,
        ).values("scenario").distinct().count()

        if passed_in_level >= all_scenarios_in_level:
            next_level = Level.objects.filter(order__gt=scenario.level.order).first()
            if next_level:
                progress.current_level = next_level

        progress.save()

    return render(request, "training/results.html", {
        "scenario": scenario,
        "score": score,
        "passed": passed,
        "correct": correct,
        "total": scoreable,
        "attempt": attempt,
    })


@login_required
def team_dashboard(request):
    if request.user.role not in ("admin", "team_lead"):
        return redirect("dashboard")

    members = UserProgress.objects.select_related("user", "current_level").all()
    return render(request, "training/team_dashboard.html", {"members": members})
