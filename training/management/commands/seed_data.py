from django.core.management.base import BaseCommand

from training.models import Choice, Level, Question, Scenario, User, UserProgress


def _mc(scenario, text, order, choices):
    q = Question.objects.get_or_create(
        scenario=scenario, text=text,
        defaults={"question_type": "multiple_choice", "order": order},
    )[0]
    for label, correct in choices:
        Choice.objects.get_or_create(question=q, text=label, defaults={"is_correct": correct})
    return q


def _tf(scenario, text, order, answer_is_true):
    q = Question.objects.get_or_create(
        scenario=scenario, text=text,
        defaults={"question_type": "true_false", "order": order},
    )[0]
    Choice.objects.get_or_create(question=q, text="True", defaults={"is_correct": answer_is_true})
    Choice.objects.get_or_create(question=q, text="False", defaults={"is_correct": not answer_is_true})
    return q


def _oe(scenario, text, order):
    return Question.objects.get_or_create(
        scenario=scenario, text=text,
        defaults={"question_type": "open_ended", "order": order},
    )[0]


class Command(BaseCommand):
    help = "Seed the database with training levels, scenarios, and questions"

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

        # --- LEVELS ---
        level1 = Level.objects.get_or_create(order=1, defaults={
            "name": "Safety Fundamentals",
            "description": "Core safety principles every team member must know.",
            "passing_score": 70,
        })[0]

        level2 = Level.objects.get_or_create(order=2, defaults={
            "name": "Hazard Identification",
            "description": "Learn to identify and assess workplace hazards before they cause harm.",
            "passing_score": 75,
        })[0]

        level3 = Level.objects.get_or_create(order=3, defaults={
            "name": "Emergency Response",
            "description": "Protocols for emergency situations and incident response.",
            "passing_score": 80,
        })[0]

        level4 = Level.objects.get_or_create(order=4, defaults={
            "name": "Leadership & Communication",
            "description": "Lead safety culture, communicate risks, and manage incident reporting.",
            "passing_score": 80,
        })[0]

        # ============================
        # LEVEL 1: Safety Fundamentals
        # ============================

        s1 = Scenario.objects.get_or_create(title="PPE Requirements", defaults={
            "description": (
                "A new worker arrives on site without proper Personal Protective Equipment. "
                "As the safety lead, you need to address this situation while maintaining a positive "
                "team environment. Review the scenario and answer the questions."
            ),
            "level": level1, "difficulty": "easy", "created_by": admin,
        })[0]

        _mc(s1, "What is the FIRST action you should take when you notice a worker without PPE?", 1, [
            ("Ignore it and continue working", False),
            ("Stop the worker from entering the work area and provide proper PPE", True),
            ("Report them to HR immediately", False),
            ("Let them work and deal with it later", False),
        ])
        _tf(s1, "Hard hats are only required in areas with overhead hazards.", 2, False)
        _oe(s1, "Describe how you would explain the importance of PPE to a resistant team member.", 3)

        s2 = Scenario.objects.get_or_create(title="Slip and Fall Prevention", defaults={
            "description": (
                "During a routine site inspection, you discover a wet floor in a high-traffic corridor "
                "with no warning signs posted. Multiple workers are approaching the area."
            ),
            "level": level1, "difficulty": "medium", "created_by": admin,
        })[0]

        _mc(s2, "What is the immediate priority in this situation?", 1, [
            ("Document the hazard for the weekly report", False),
            ("Warn approaching workers and place warning signs immediately", True),
            ("Find who is responsible for the spill", False),
            ("Clean the floor yourself", False),
        ])
        _tf(s2, "Warning signs should only be placed after a supervisor approves.", 2, False)
        _mc(s2, "Which of the following is NOT a common cause of slips and falls?", 3, [
            ("Wet or oily surfaces", False),
            ("Loose rugs or mats", False),
            ("Proper lighting", True),
            ("Cluttered walkways", False),
        ])

        s_fire = Scenario.objects.get_or_create(title="Fire Extinguisher Basics", defaults={
            "description": (
                "You smell smoke coming from the break room. Upon investigation, you find a small grease fire "
                "on the stovetop. A fire extinguisher is mounted on the wall nearby. Several coworkers are "
                "watching, unsure what to do."
            ),
            "level": level1, "difficulty": "medium", "created_by": admin,
        })[0]

        _mc(s_fire, "What does the acronym PASS stand for when using a fire extinguisher?", 1, [
            ("Push, Aim, Spray, Sweep", False),
            ("Pull, Aim, Squeeze, Sweep", True),
            ("Point, Activate, Spray, Stop", False),
            ("Pull, Activate, Squeeze, Stop", False),
        ])
        _mc(s_fire, "Which type of fire extinguisher should NEVER be used on a grease fire?", 2, [
            ("Class B (flammable liquids)", False),
            ("Class K (kitchen fires)", False),
            ("Class A (water-based)", True),
            ("Class ABC (multi-purpose)", False),
        ])
        _tf(s_fire, "You should always attempt to fight a fire regardless of its size.", 3, False)
        _oe(s_fire, "Describe the evacuation steps you would communicate to your coworkers if the fire was too large to extinguish.", 4)

        s_ladder = Scenario.objects.get_or_create(title="Ladder Safety", defaults={
            "description": (
                "A team member needs to access equipment stored on a high shelf in the warehouse. "
                "They grab the nearest ladder and start climbing without inspection or setup."
            ),
            "level": level1, "difficulty": "easy", "created_by": admin,
        })[0]

        _mc(s_ladder, "What should be done BEFORE using any ladder?", 1, [
            ("Inspect it for damage and ensure it's rated for the load", True),
            ("Just start climbing if it looks fine", False),
            ("Ask someone to hold the bottom", False),
            ("Use it only if a supervisor is present", False),
        ])
        _tf(s_ladder, "The 4-to-1 rule means for every 4 feet of ladder height, the base should be 1 foot from the wall.", 2, True)
        _mc(s_ladder, "What is the maximum recommended reach from a ladder?", 3, [
            ("As far as you can stretch", False),
            ("Arm's length while keeping your belt buckle between the side rails", True),
            ("Two feet past the side rail", False),
            ("Whatever feels comfortable", False),
        ])

        # =============================
        # LEVEL 2: Hazard Identification
        # =============================

        s3 = Scenario.objects.get_or_create(title="Chemical Spill Response", defaults={
            "description": (
                "A container of cleaning chemicals has been knocked over in the storage room. "
                "You can smell fumes and see liquid spreading across the floor. Two workers are nearby."
            ),
            "level": level2, "difficulty": "hard", "created_by": admin,
        })[0]

        _mc(s3, "What should be your first action upon discovering the spill?", 1, [
            ("Start cleaning up the spill immediately", False),
            ("Evacuate the immediate area and alert nearby workers", True),
            ("Open windows for ventilation", False),
            ("Call 911", False),
        ])
        _tf(s3, "Before attempting any cleanup of an unknown chemical, you should always consult the Safety Data Sheet (SDS).", 2, True)
        _oe(s3, "Explain the steps you would take to contain a minor chemical spill after consulting the SDS.", 3)

        s_confined = Scenario.objects.get_or_create(title="Confined Space Entry", defaults={
            "description": (
                "Your team needs to perform maintenance inside a large storage tank that has been emptied. "
                "The tank has one entry point and limited ventilation. A team member suggests they can just "
                "climb in and get the work done quickly."
            ),
            "level": level2, "difficulty": "hard", "created_by": admin,
        })[0]

        _mc(s_confined, "What must be completed before anyone enters a confined space?", 1, [
            ("A verbal agreement from the supervisor", False),
            ("A confined space entry permit and atmospheric testing", True),
            ("A quick visual inspection of the space", False),
            ("Notifying the front desk", False),
        ])
        _mc(s_confined, "What is the minimum number of people required for a confined space entry?", 2, [
            ("One — the person entering", False),
            ("Two — one entrant and one attendant outside", True),
            ("Three — entrant, attendant, and supervisor", False),
            ("It depends on the company policy", False),
        ])
        _tf(s_confined, "If the atmosphere tests normal at the entry, it's safe to assume the entire space has breathable air.", 3, False)
        _oe(s_confined, "What rescue plan would you have in place before authorizing a confined space entry?", 4)

        s_electrical = Scenario.objects.get_or_create(title="Electrical Hazard Assessment", defaults={
            "description": (
                "During a walkthrough of the production floor, you notice a power cord running across a "
                "walkway with visible damage to the insulation. The cord is connected to a running machine. "
                "A small puddle of water is nearby from a recent cleaning."
            ),
            "level": level2, "difficulty": "medium", "created_by": admin,
        })[0]

        _mc(s_electrical, "What is the FIRST thing you should do?", 1, [
            ("Unplug the cord immediately", False),
            ("Secure the area and prevent anyone from approaching the hazard", True),
            ("Put tape over the damaged insulation", False),
            ("Mop up the water", False),
        ])
        _mc(s_electrical, "Why is the puddle of water especially dangerous in this scenario?", 2, [
            ("It could cause someone to slip", False),
            ("Water conducts electricity, increasing the risk of electrocution", True),
            ("It could damage the machine", False),
            ("It will rust the floor", False),
        ])
        _tf(s_electrical, "Electrical tape is an acceptable permanent repair for damaged power cord insulation.", 3, False)

        s_ergo = Scenario.objects.get_or_create(title="Ergonomic Risk Factors", defaults={
            "description": (
                "A warehouse worker has been manually lifting boxes weighing 40-50 lbs from floor level "
                "to a shelf at shoulder height, repeating the motion 60+ times per shift. They've started "
                "complaining about lower back pain."
            ),
            "level": level2, "difficulty": "medium", "created_by": admin,
        })[0]

        _mc(s_ergo, "Which ergonomic risk factor is MOST present in this scenario?", 1, [
            ("Vibration", False),
            ("Repetitive motion with heavy loads at awkward angles", True),
            ("Prolonged sitting", False),
            ("Cold temperature exposure", False),
        ])
        _mc(s_ergo, "What is the best corrective action?", 2, [
            ("Tell the worker to lift with their legs", False),
            ("Provide mechanical lift assists and redesign the workstation height", True),
            ("Give the worker pain medication", False),
            ("Reduce their pay so they work less", False),
        ])
        _tf(s_ergo, "Proper lifting technique alone is sufficient to prevent injuries from repetitive heavy lifting.", 3, False)

        # ============================
        # LEVEL 3: Emergency Response
        # ============================

        s_evac = Scenario.objects.get_or_create(title="Building Evacuation", defaults={
            "description": (
                "The fire alarm has activated during a busy work shift. You are the designated floor warden. "
                "Some workers are heading for the exits, but others are still at their desks finishing tasks. "
                "One worker is mobility-impaired and uses a wheelchair."
            ),
            "level": level3, "difficulty": "hard", "created_by": admin,
        })[0]

        _mc(s_evac, "As floor warden, what is your first responsibility when the alarm sounds?", 1, [
            ("Investigate the cause of the alarm", False),
            ("Begin systematic sweep of your floor and direct everyone to exits", True),
            ("Call the fire department", False),
            ("Wait for instructions from management", False),
        ])
        _mc(s_evac, "How should the mobility-impaired worker be assisted during evacuation?", 2, [
            ("Leave them and send help later", False),
            ("Carry them down the stairs", False),
            ("Move them to the designated area of refuge and notify emergency responders of their location", True),
            ("Tell them to use the elevator", False),
        ])
        _tf(s_evac, "During a fire alarm, it is acceptable to use elevators if the fire is on a different floor.", 3, False)
        _mc(s_evac, "What should you do after all personnel have evacuated your floor?", 4, [
            ("Go back inside to save equipment", False),
            ("Report to the assembly point and confirm a headcount with the incident commander", True),
            ("Drive home", False),
            ("Call your family", False),
        ])

        s_medical = Scenario.objects.get_or_create(title="Medical Emergency Response", defaults={
            "description": (
                "A coworker collapses on the production floor. They are unresponsive and do not appear to "
                "be breathing. An AED is mounted on the wall 50 feet away. Several workers are nearby."
            ),
            "level": level3, "difficulty": "hard", "created_by": admin,
        })[0]

        _mc(s_medical, "What is the correct sequence of actions?", 1, [
            ("Move the person to a comfortable area, then call 911", False),
            ("Call 911, begin CPR, send someone for the AED", True),
            ("Wait for a trained first responder to arrive", False),
            ("Give the person water and wait", False),
        ])
        _tf(s_medical, "You should only perform CPR if you are officially certified.", 2, False)
        _mc(s_medical, "When using an AED, what must you do before delivering a shock?", 3, [
            ("Check for a pulse one more time", False),
            ("Ensure no one is touching the person and say 'Clear!'", True),
            ("Remove all clothing from the person", False),
            ("Turn off nearby machinery", False),
        ])
        _oe(s_medical, "Describe how you would manage the scene to protect the victim's privacy and dignity while waiting for EMS.", 4)

        s_active = Scenario.objects.get_or_create(title="Active Threat Response", defaults={
            "description": (
                "You receive a notification that an active threat situation has been reported in an adjacent "
                "building on your campus. Your building has not been directly affected yet. Workers are "
                "starting to panic."
            ),
            "level": level3, "difficulty": "hard", "created_by": admin,
        })[0]

        _mc(s_active, "What does the 'Run, Hide, Fight' protocol prioritize?", 1, [
            ("Fighting the threat first", False),
            ("Hiding immediately no matter what", False),
            ("Evacuating if a safe path exists, hiding if not, fighting only as a last resort", True),
            ("Running in any direction", False),
        ])
        _mc(s_active, "If you decide to shelter in place, which action is MOST important?", 2, [
            ("Continue working normally", False),
            ("Lock and barricade the door, silence phones, stay low and out of sight", True),
            ("Look out the window to see what's happening", False),
            ("Call all your coworkers to warn them", False),
        ])
        _tf(s_active, "You should prop doors open during a lockdown to help others evacuate.", 3, False)
        _oe(s_active, "How would you help calm panicking coworkers while following the active threat protocol?", 4)

        s_weather = Scenario.objects.get_or_create(title="Severe Weather Protocol", defaults={
            "description": (
                "A tornado warning has been issued for your area. You are working in a single-story warehouse "
                "with large bay doors. The warning says the tornado could arrive within 15 minutes."
            ),
            "level": level3, "difficulty": "medium", "created_by": admin,
        })[0]

        _mc(s_weather, "Where is the safest location in a single-story warehouse during a tornado?", 1, [
            ("Near the bay doors for quick exit", False),
            ("In an interior room or hallway away from windows and exterior walls", True),
            ("Under the largest piece of equipment", False),
            ("In the parking lot in your car", False),
        ])
        _tf(s_weather, "Opening windows during a tornado helps equalize pressure and prevent damage.", 2, False)
        _mc(s_weather, "What should workers do to protect themselves if no shelter room is available?", 3, [
            ("Stand against the exterior wall", False),
            ("Get under a sturdy workbench, cover head and neck, stay away from heavy equipment that could topple", True),
            ("Go to the roof for a better view", False),
            ("Run to the parking lot", False),
        ])

        # ====================================
        # LEVEL 4: Leadership & Communication
        # ====================================

        s_report = Scenario.objects.get_or_create(title="Incident Reporting", defaults={
            "description": (
                "A near-miss incident occurred yesterday — a heavy tool fell from scaffolding and landed "
                "inches from a worker below. No one was hurt. The crew lead says it's not worth reporting "
                "since no one was injured. You disagree."
            ),
            "level": level4, "difficulty": "medium", "created_by": admin,
        })[0]

        _mc(s_report, "Why is it critical to report near-miss incidents?", 1, [
            ("It's only important if someone was hurt", False),
            ("Near-misses reveal hazards that could cause future injuries or fatalities", True),
            ("It makes the paperwork look complete", False),
            ("To get the crew lead in trouble", False),
        ])
        _tf(s_report, "OSHA does not require reporting of near-miss incidents.", 2, True)
        _mc(s_report, "What information should a near-miss report include?", 3, [
            ("Only the date and time", False),
            ("Date, time, location, description, contributing factors, witnesses, and corrective actions", True),
            ("Just a verbal mention at the next meeting", False),
            ("A photo only", False),
        ])
        _oe(s_report, "How would you persuade a reluctant crew lead that near-miss reporting benefits the entire team?", 4)

        s_toolbox = Scenario.objects.get_or_create(title="Leading a Safety Toolbox Talk", defaults={
            "description": (
                "You've been asked to lead a 10-minute safety toolbox talk before the morning shift. "
                "The topic is heat stress prevention. Your audience is 15 field workers, some of whom "
                "tend to tune out safety meetings."
            ),
            "level": level4, "difficulty": "medium", "created_by": admin,
        })[0]

        _mc(s_toolbox, "What is the most effective way to open a toolbox talk?", 1, [
            ("Read directly from the safety manual", False),
            ("Start with a real incident or relatable scenario to capture attention", True),
            ("Threaten disciplinary action for non-compliance", False),
            ("Skip the intro and go straight to the rules", False),
        ])
        _mc(s_toolbox, "Which sign of heat exhaustion requires immediate action?", 2, [
            ("Slight thirst", False),
            ("Confusion, slurred speech, or loss of consciousness", True),
            ("Mild sweating", False),
            ("Feeling warm", False),
        ])
        _tf(s_toolbox, "Toolbox talks are most effective when workers participate and ask questions rather than just listen.", 3, True)
        _oe(s_toolbox, "Write a brief opening (2-3 sentences) for a toolbox talk on heat stress that would grab your crew's attention.", 4)

        s_culture = Scenario.objects.get_or_create(title="Building a Safety Culture", defaults={
            "description": (
                "You've noticed that workers on your team have started cutting corners — skipping pre-task "
                "safety checks, not wearing eye protection in designated areas, and rushing through "
                "procedures. No incidents have happened yet, but the trend is concerning."
            ),
            "level": level4, "difficulty": "hard", "created_by": admin,
        })[0]

        _mc(s_culture, "What is the root cause of workers cutting safety corners?", 1, [
            ("Workers are lazy", False),
            ("A combination of production pressure, complacency, and weak accountability culture", True),
            ("The rules are too strict", False),
            ("It's just bad luck", False),
        ])
        _mc(s_culture, "Which approach is most effective for changing unsafe behaviors long-term?", 2, [
            ("Punish every violation immediately", False),
            ("Combine positive reinforcement for safe behavior with consistent, fair accountability", True),
            ("Post more warning signs", False),
            ("Ignore it until an accident happens", False),
        ])
        _tf(s_culture, "A strong safety culture means zero accidents will ever occur.", 3, False)
        _oe(s_culture, "Describe three specific actions you would take this week to start rebuilding safety discipline on your team.", 4)

        UserProgress.objects.get_or_create(user=admin, defaults={"current_level": level1})

        counts = {
            "levels": Level.objects.count(),
            "scenarios": Scenario.objects.count(),
            "questions": Question.objects.count(),
        }
        self.stdout.write(self.style.SUCCESS(
            f"Seed data loaded: {counts['levels']} levels, {counts['scenarios']} scenarios, {counts['questions']} questions"
        ))
