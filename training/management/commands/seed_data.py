from django.core.management.base import BaseCommand

from training.models import Choice, Level, Question, Scenario, User, UserProgress


class Command(BaseCommand):
    help = "Seed the database with sample training levels, scenarios, and questions"

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "email": "admin@beacon.com",
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created admin user (admin / admin123)"))

        level1 = Level.objects.get_or_create(
            order=1,
            defaults={
                "name": "Safety Fundamentals",
                "description": "Core safety principles every team member must know.",
                "passing_score": 70,
            },
        )[0]

        level2 = Level.objects.get_or_create(
            order=2,
            defaults={
                "name": "Hazard Identification",
                "description": "Learn to identify and assess workplace hazards.",
                "passing_score": 75,
            },
        )[0]

        level3 = Level.objects.get_or_create(
            order=3,
            defaults={
                "name": "Emergency Response",
                "description": "Protocols for emergency situations and incident response.",
                "passing_score": 80,
            },
        )[0]

        s1 = Scenario.objects.get_or_create(
            title="PPE Requirements",
            defaults={
                "description": "A new worker arrives on site without proper Personal Protective Equipment. "
                "As the safety lead, you need to address this situation while maintaining a positive "
                "team environment. Review the scenario and answer the questions.",
                "level": level1,
                "difficulty": "easy",
                "created_by": admin,
            },
        )[0]

        q1 = Question.objects.get_or_create(
            scenario=s1,
            text="What is the FIRST action you should take when you notice a worker without PPE?",
            defaults={"question_type": "multiple_choice", "order": 1},
        )[0]
        Choice.objects.get_or_create(question=q1, text="Ignore it and continue working", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q1, text="Stop the worker from entering the work area and provide proper PPE", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q1, text="Report them to HR immediately", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q1, text="Let them work and deal with it later", defaults={"is_correct": False})

        q2 = Question.objects.get_or_create(
            scenario=s1,
            text="Hard hats are only required in areas with overhead hazards.",
            defaults={"question_type": "true_false", "order": 2},
        )[0]
        Choice.objects.get_or_create(question=q2, text="True", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q2, text="False", defaults={"is_correct": True})

        q3 = Question.objects.get_or_create(
            scenario=s1,
            text="Describe how you would explain the importance of PPE to a resistant team member.",
            defaults={"question_type": "open_ended", "order": 3},
        )[0]

        s2 = Scenario.objects.get_or_create(
            title="Slip and Fall Prevention",
            defaults={
                "description": "During a routine site inspection, you discover a wet floor in a high-traffic corridor "
                "with no warning signs posted. Multiple workers are approaching the area.",
                "level": level1,
                "difficulty": "medium",
                "created_by": admin,
            },
        )[0]

        q4 = Question.objects.get_or_create(
            scenario=s2,
            text="What is the immediate priority in this situation?",
            defaults={"question_type": "multiple_choice", "order": 1},
        )[0]
        Choice.objects.get_or_create(question=q4, text="Document the hazard for the weekly report", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q4, text="Warn approaching workers and place warning signs immediately", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q4, text="Find who is responsible for the spill", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q4, text="Clean the floor yourself", defaults={"is_correct": False})

        s3 = Scenario.objects.get_or_create(
            title="Chemical Spill Response",
            defaults={
                "description": "A container of cleaning chemicals has been knocked over in the storage room. "
                "You can smell fumes and see liquid spreading across the floor. Two workers are nearby.",
                "level": level2,
                "difficulty": "hard",
                "created_by": admin,
            },
        )[0]

        q5 = Question.objects.get_or_create(
            scenario=s3,
            text="What should be your first action upon discovering the spill?",
            defaults={"question_type": "multiple_choice", "order": 1},
        )[0]
        Choice.objects.get_or_create(question=q5, text="Start cleaning up the spill immediately", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q5, text="Evacuate the immediate area and alert nearby workers", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q5, text="Open windows for ventilation", defaults={"is_correct": False})
        Choice.objects.get_or_create(question=q5, text="Call 911", defaults={"is_correct": False})

        q6 = Question.objects.get_or_create(
            scenario=s3,
            text="Before attempting any cleanup of an unknown chemical, you should always consult the Safety Data Sheet (SDS).",
            defaults={"question_type": "true_false", "order": 2},
        )[0]
        Choice.objects.get_or_create(question=q6, text="True", defaults={"is_correct": True})
        Choice.objects.get_or_create(question=q6, text="False", defaults={"is_correct": False})

        UserProgress.objects.get_or_create(user=admin, defaults={"current_level": level1})

        self.stdout.write(self.style.SUCCESS("Seed data loaded: 3 levels, 3 scenarios, 6 questions"))
