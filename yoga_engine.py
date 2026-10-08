# ==========================================
# YOGASUTRA AI - YOGA KNOWLEDGE BASE
# ==========================================

YOGA_KNOWLEDGE_BASE = [

    # --------------------------------------
    # WEIGHT LOSS
    # --------------------------------------

    {
        "name": "Trikonasana",
        "goals": ["Weight Loss"],
        "levels": ["Beginner", "Intermediate", "Advanced"],
        "age_limit": 70,
        "duration": 4,
        "category": "Standing",
        "contraindications": []
    },

    {
        "name": "Utkatasana",
        "goals": ["Weight Loss"],
        "levels": ["Beginner", "Intermediate"],
        "age_limit": 60,
        "duration": 3,
        "category": "Strength",
        "contraindications": ["knee_pain"]
    },

    {
        "name": "Virabhadrasana I",
        "goals": ["Weight Loss"],
        "levels": ["Beginner", "Intermediate"],
        "age_limit": 65,
        "duration": 4,
        "category": "Standing",
        "contraindications": []
    },

    {
        "name": "Virabhadrasana II",
        "goals": ["Weight Loss"],
        "levels": ["Intermediate", "Advanced"],
        "age_limit": 60,
        "duration": 4,
        "category": "Standing",
        "contraindications": []
    },

    {
        "name": "Navasana",
        "goals": ["Weight Loss"],
        "levels": ["Intermediate", "Advanced"],
        "age_limit": 60,
        "duration": 4,
        "category": "Core",
        "contraindications": ["back_pain", "pregnancy"]
    },

    {
        "name": "Dhanurasana",
        "goals": ["Weight Loss"],
        "levels": ["Intermediate", "Advanced"],
        "age_limit": 60,
        "duration": 5,
        "category": "Backbend",
        "contraindications": ["back_pain", "pregnancy"]
    },


    # --------------------------------------
    # WEIGHT GAIN
    # --------------------------------------

    {
        "name": "Tadasana",
        "goals": ["Weight Gain"],
        "levels": ["Beginner", "Intermediate", "Advanced"],
        "age_limit": 100,
        "duration": 3,
        "category": "Standing",
        "contraindications": []
    },

    {
        "name": "Bhujangasana",
        "goals": ["Weight Gain"],
        "levels": ["Beginner", "Intermediate"],
        "age_limit": 70,
        "duration": 4,
        "category": "Backbend",
        "contraindications": ["back_pain", "pregnancy"]
    },

    {
        "name": "Setu Bandhasana",
        "goals": ["Weight Gain"],
        "levels": ["Beginner", "Intermediate"],
        "age_limit": 70,
        "duration": 4,
        "category": "Backbend",
        "contraindications": []
    },

    {
        "name": "Vrikshasana",
        "goals": ["Weight Gain"],
        "levels": ["Beginner", "Intermediate"],
        "age_limit": 70,
        "duration": 3,
        "category": "Balance",
        "contraindications": ["knee_pain"]
    },

    {
        "name": "Paschimottanasana",
        "goals": ["Weight Gain"],
        "levels": ["Beginner", "Intermediate", "Advanced"],
        "age_limit": 70,
        "duration": 5,
        "category": "Forward Bend",
        "contraindications": []
    }
]


# ==========================================
# SAFETY CHECK
# ==========================================

def is_safe_for_user(yoga, health_conditions):

    for condition in health_conditions:

        if condition in yoga.get("contraindications", []):
            return False

    return True


# ==========================================
# PRANAYAMA KNOWLEDGE
# ==========================================

PRANAYAMA_KNOWLEDGE_BASE = [

    {
        "name": "Anulom Vilom",
        "goals": [
            "Weight Gain",
            "Weight Loss"
        ]
    },

    {
        "name": "Kapalabhati",
        "goals": [
            "Weight Loss"
        ]
    }
]


# ==========================================
# MEDITATION KNOWLEDGE
# ==========================================

MEDITATION_KNOWLEDGE_BASE = [

    {
        "name": "Breathing Meditation",
        "goals": [
            "Weight Gain",
            "Weight Loss"
        ]
    },

    {
        "name": "Shavasana Relaxation",
        "goals": [
            "Weight Gain",
            "Weight Loss"
        ]
    }
]


# ==========================================
# YOGA RECOMMENDATION ENGINE
# ==========================================

def recommend_yogasanas(
    age,
    fitness_level,
    goal,
    available_duration,
    health_conditions
):

    candidates = []

    for yoga in YOGA_KNOWLEDGE_BASE:

        # Age filter
        if age > yoga["age_limit"]:
            continue

        # Fitness level filter
        if fitness_level not in yoga["levels"]:
            continue

        # Health safety filter
        if not is_safe_for_user(yoga, health_conditions):
            continue

        # Goal filter
        if goal not in yoga["goals"]:
            continue

        candidates.append(yoga)


    # --------------------------------------
    # Score suitable yogasanas
    # --------------------------------------

    scored_yogas = []

    for yoga in candidates:

        score = 0

        # Main goal match
        if goal in yoga["goals"]:
            score += 10

        # Fitness level match
        if fitness_level in yoga["levels"]:
            score += 5

        # Age suitability
        if age <= yoga["age_limit"]:
            score += 2

        scored_yogas.append(
            (score, yoga)
        )


    # Highest score first
    scored_yogas.sort(
        key=lambda item: item[0],
        reverse=True
    )


    # --------------------------------------
    # Select maximum 5 yogasanas
    # --------------------------------------

    selected = []

    total_time = 0

    for score, yoga in scored_yogas:

        if total_time + yoga["duration"] <= available_duration:

            selected.append(yoga)

            total_time += yoga["duration"]

        if len(selected) >= 5:
            break


    return selected


# ==========================================
# PRANAYAMA RECOMMENDATION
# ==========================================

def recommend_pranayama(goal):

    recommended = []

    for item in PRANAYAMA_KNOWLEDGE_BASE:

        if goal in item["goals"]:

            recommended.append(
                item["name"]
            )

    return recommended[:2]


# ==========================================
# MEDITATION RECOMMENDATION
# ==========================================

def recommend_meditation(goal):

    recommended = []

    for item in MEDITATION_KNOWLEDGE_BASE:

        if goal in item["goals"]:

            recommended.append(
                item["name"]
            )

    return recommended[:2]


# ==========================================
# GENERATE COMPLETE AI YOGA PLAN
# ==========================================

def generate_ai_yoga_plan(
    age,
    fitness_level,
    goal,
    duration,
    practice_time,
    health_conditions
):

    # --------------------------------------
    # Convert duration to integer
    # --------------------------------------

    duration = int(duration)


    # --------------------------------------
    # Allow 10 minutes for pranayama
    # and meditation
    # --------------------------------------

    yoga_duration = max(
        duration - 10,
        5
    )


    # --------------------------------------
    # Recommend Yogasanas
    # --------------------------------------

    recommended_yogasanas = recommend_yogasanas(
        age,
        fitness_level,
        goal,
        yoga_duration,
        health_conditions
    )


    # --------------------------------------
    # Recommend Pranayama
    # --------------------------------------

    pranayama = recommend_pranayama(
        goal
    )


    # --------------------------------------
    # Recommend Meditation
    # --------------------------------------

    meditation = recommend_meditation(
        goal
    )


    # --------------------------------------
    # Return Final AI Plan
    # --------------------------------------

    return {

        "age": age,

        "fitness_level": fitness_level,

        "goal": goal,

        "duration": duration,

        "practice_time": practice_time,

        "health_conditions": health_conditions,

        "yogasanas": [
            yoga["name"]
            for yoga in recommended_yogasanas
        ],

        "pranayama": pranayama,

        "meditation": meditation
    }