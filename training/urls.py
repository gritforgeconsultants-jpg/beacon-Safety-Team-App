from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("level/<int:level_id>/", views.level_detail, name="level_detail"),
    path("scenario/<int:scenario_id>/", views.scenario_start, name="scenario_start"),
    path("scenario/<int:scenario_id>/submit/", views.scenario_submit, name="scenario_submit"),
    path("history/", views.history, name="history"),
    path("history/<int:attempt_id>/", views.attempt_detail, name="attempt_detail"),
    path("team/", views.team_dashboard, name="team_dashboard"),
]
