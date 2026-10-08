from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from bson.objectid import ObjectId

from yoga_engine import generate_ai_yoga_plan


app = Flask(__name__)

# =========================
# SECRET KEY
# =========================

app.secret_key = "yogasutra_ai_secret_key_2026"


# =========================
# MONGODB CONNECTION
# =========================

MONGO_URI = "mongodb://localhost:27017/"

try:

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    client.admin.command("ping")

    print("MongoDB Connected Successfully!")

except Exception as e:

    print("MongoDB Connection Error:", e)


db = client["yogasutra_ai"]

users_collection = db["users"]

yoga_plans_collection = db["yoga_plans"]

sessions_collection = db["sessions"]


# =========================
# ADMIN COLLECTION
# =========================

admins_collection = db["admins"]

DEFAULT_ADMIN_EMAIL = "admin@yogasutra.ai"
DEFAULT_ADMIN_PASSWORD = "admin123"

existing_admin = admins_collection.find_one({
    "email": DEFAULT_ADMIN_EMAIL
})

if not existing_admin:

    admins_collection.insert_one({
        "name": "YogaSutra Admin",
        "email": DEFAULT_ADMIN_EMAIL,
        "password": generate_password_hash(
            DEFAULT_ADMIN_PASSWORD
        ),
        "role": "admin",
        "created_at": datetime.now()
    })


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    return render_template("index.html")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        age = request.form.get("age")
        experience = request.form.get("experience")

        existing_user = users_collection.find_one({
            "email": email
        })

        if existing_user:

            flash("Email already registered. Please login.")

            return redirect(
                url_for("login")
            )

        hashed_password = generate_password_hash(
            password
        )

        user = {

            "name": name,

            "email": email,

            "password": hashed_password,

            "age": age,

            "experience": experience,

            "created_at": datetime.now()
        }

        users_collection.insert_one(user)

        flash(
            "Registration successful! Please login."
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")

        password = request.form.get("password")

        user = users_collection.find_one({
            "email": email
        })

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = str(
                user["_id"]
            )

            session["user_name"] = user.get(
                "name",
                "User"
            )

            session["user_email"] = user.get(
                "email",
                ""
            )

            return redirect(
                url_for("dashboard")
            )

        else:

            flash(
                "Invalid email or password."
            )

    return render_template(
        "login.html"
    )


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]


    # =========================
    # LATEST PLAN
    # =========================

    latest_plan_data = yoga_plans_collection.find_one(
        {
            "user_id": user_id
        },
        sort=[
            ("_id", -1)
        ]
    )

    latest_plan = None

    current_goal = "Not Set"

    plan_duration = 0

    if latest_plan_data:

        latest_plan = latest_plan_data.get(
            "plan"
        )

        current_goal = latest_plan.get(
            "goal",
            "Not Set"
        )

        plan_duration = latest_plan.get(
            "duration",
            0
        )


    # =========================
    # TOTAL SESSIONS
    # =========================

    total_sessions = sessions_collection.count_documents({

        "user_id": user_id

    })


    # =========================
    # TOTAL PRACTICE TIME
    # =========================

    total_practice = 0

    user_sessions = sessions_collection.find({

        "user_id": user_id

    })

    for item in user_sessions:

        total_practice += item.get(
            "duration",
            0
        )


    # =========================
    # TODAY
    # =========================

    today = datetime.now().date()

    today_string = today.strftime(
        "%Y-%m-%d"
    )

    today_session = sessions_collection.find_one({

        "user_id": user_id,

        "completed_date": today_string

    })

    completed_today = (
        today_session is not None
    )


    # =========================
    # STREAK
    # =========================

    completed_dates = sessions_collection.find(

        {
            "user_id": user_id
        },

        {
            "completed_date": 1,
            "_id": 0
        }

    )

    date_set = set()

    for item in completed_dates:

        if item.get("completed_date"):

            date_set.add(
                datetime.strptime(
                    item["completed_date"],
                    "%Y-%m-%d"
                ).date()
            )

    current_streak = 0

    check_date = today

    while check_date in date_set:

        current_streak += 1

        check_date -= timedelta(
            days=1
        )


    # =========================
    # RECENT ACTIVITY
    # =========================

    recent_sessions = list(

        sessions_collection.find({

            "user_id": user_id

        })
        .sort(
            "completed_at",
            -1
        )
        .limit(5)

    )


    # =========================
    # RETURN DASHBOARD
    # =========================

    return render_template(

        "dashboard.html",

        name=session.get(
            "user_name",
            "User"
        ),

        latest_plan=latest_plan,

        current_goal=current_goal,

        plan_duration=plan_duration,

        total_sessions=total_sessions,

        total_practice=total_practice,

        current_streak=current_streak,

        completed_today=completed_today,

        recent_sessions=recent_sessions

    )


# =========================
# VIEW SAVED YOGA PLAN
# =========================

@app.route("/my-yoga-plan")
def my_yoga_plan():

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]


    # Get latest saved plan

    latest_plan_data = yoga_plans_collection.find_one(

        {
            "user_id": user_id
        },

        sort=[
            ("_id", -1)
        ]

    )


    if not latest_plan_data:

        flash(
            "No yoga plan found. Please generate a plan first."
        )

        return redirect(
            url_for("recommendation")
        )


    yoga_plan = latest_plan_data.get(
        "plan"
    )


    return render_template(

        "yoga_plan.html",

        plan=yoga_plan

    )


# =========================
# COMPLETE SESSION
# =========================

@app.route(
    "/complete-session",
    methods=["POST"]
)
def complete_session():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    today = datetime.now().date()

    today_string = today.strftime(
        "%Y-%m-%d"
    )


    # Check duplicate

    already_completed = sessions_collection.find_one({

        "user_id": user_id,

        "completed_date": today_string

    })


    if already_completed:

        flash(
            "You have already completed today's session! 🎉"
        )

        return redirect(
            url_for("dashboard")
        )


    # Get latest plan

    latest_plan_data = yoga_plans_collection.find_one(

        {
            "user_id": user_id
        },

        sort=[
            ("_id", -1)
        ]

    )


    if not latest_plan_data:

        flash(
            "Please generate a yoga plan first."
        )

        return redirect(
            url_for("recommendation")
        )


    latest_plan = latest_plan_data["plan"]

    duration = latest_plan.get(
        "duration",
        0
    )


    # Save session

    sessions_collection.insert_one({

        "user_id": user_id,

        "duration": duration,

        "goal": latest_plan.get(
            "goal",
            "Yoga"
        ),

        "completed_date": today_string,

        "completed_at": datetime.now()

    })


    flash(
        "Excellent! Today's yoga session is complete! 🔥🎉"
    )

    return redirect(
        url_for("dashboard")
    )


# =========================
# PROFILE
# =========================

@app.route("/profile")
def profile():

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    try:

        user = users_collection.find_one({

            "_id": ObjectId(
                session["user_id"]
            )

        })

    except Exception:

        user = None


    if not user:

        session.clear()

        flash(
            "User account not found."
        )

        return redirect(
            url_for("login")
        )


    return render_template(

        "profile.html",

        user=user

    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully."
    )

    return redirect(
        url_for("home")
    )


# =========================
# ADMIN LOGIN
# =========================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        email = request.form.get("email")

        password = request.form.get("password")

        admin = admins_collection.find_one({

            "email": email

        })


        if admin and check_password_hash(

            admin["password"],

            password

        ):

            session.clear()

            session["admin_id"] = str(
                admin["_id"]
            )

            session["admin_name"] = admin["name"]

            session["is_admin"] = True

            return redirect(
                url_for("admin_dashboard")
            )

        else:

            flash(
                "Invalid admin email or password."
            )


    return render_template(
        "admin_login.html"
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("is_admin"):

        return redirect(
            url_for("admin_login")
        )


    total_users = users_collection.count_documents({})

    total_plans = yoga_plans_collection.count_documents({})

    total_sessions = sessions_collection.count_documents({})


    recent_sessions = list(

        sessions_collection.find()

        .sort(
            "completed_at",
            -1
        )

        .limit(10)

    )


    for activity in recent_sessions:

        try:

            user = users_collection.find_one({

                "_id": ObjectId(
                    activity["user_id"]
                )

            })

        except Exception:

            user = None


        if user:

            activity["user_name"] = user.get(
                "name",
                "Unknown User"
            )

        else:

            activity["user_name"] = "Unknown User"


    return render_template(

        "admin_dashboard.html",

        total_users=total_users,

        total_plans=total_plans,

        total_sessions=total_sessions,

        recent_sessions=recent_sessions

    )


# =========================
# ADMIN - MANAGE USERS
# =========================

@app.route("/admin/users")
def admin_users():

    if not session.get("is_admin"):

        return redirect(
            url_for("admin_login")
        )


    users = list(

        users_collection.find()

        .sort(
            "created_at",
            -1
        )

    )


    return render_template(

        "admin_users.html",

        users=users

    )


# =========================
# ADMIN - DELETE USER
# =========================

@app.route(
    "/admin/users/delete/<user_id>",
    methods=["POST"]
)
def admin_delete_user(user_id):

    if not session.get("is_admin"):

        return redirect(
            url_for("admin_login")
        )


    try:

        user_object_id = ObjectId(
            user_id
        )


        users_collection.delete_one({

            "_id": user_object_id

        })


        yoga_plans_collection.delete_many({

            "user_id": user_id

        })


        sessions_collection.delete_many({

            "user_id": user_id

        })


        flash(
            "User deleted successfully."
        )


    except Exception:

        flash(
            "Unable to delete user."
        )


    return redirect(
        url_for("admin_users")
    )


# =========================
# ADMIN - VIEW YOGA PLANS
# =========================

@app.route("/admin/plans")
def admin_plans():

    if not session.get("is_admin"):

        return redirect(
            url_for("admin_login")
        )


    plans = list(

        yoga_plans_collection.find()

        .sort(
            "created_at",
            -1
        )

    )


    for plan in plans:

        user_id = plan.get(
            "user_id"
        )


        try:

            user = users_collection.find_one({

                "_id": ObjectId(
                    user_id
                )

            })

        except Exception:

            user = None


        if user:

            plan["user_name"] = user.get(
                "name",
                "Unknown User"
            )

            plan["user_email"] = user.get(
                "email",
                "Unknown Email"
            )

        else:

            plan["user_name"] = "Unknown User"

            plan["user_email"] = "Unknown Email"


    return render_template(

        "admin_plans.html",

        plans=plans

    )


# =========================
# ADMIN YOGA KNOWLEDGE
# =========================

@app.route("/admin/yoga")
def admin_yoga():

    if not session.get("is_admin"):

        return redirect(
            url_for("admin_login")
        )


    from yoga_engine import (

        YOGA_KNOWLEDGE_BASE,

        PRANAYAMA_KNOWLEDGE_BASE,

        MEDITATION_KNOWLEDGE_BASE

    )


    return render_template(

        "admin_yoga.html",

        yogasanas=YOGA_KNOWLEDGE_BASE,

        pranayama=PRANAYAMA_KNOWLEDGE_BASE,

        meditation=MEDITATION_KNOWLEDGE_BASE

    )


# ==========================================
# ADD YOGASANA
# ==========================================

@app.route(
    "/admin/yoga/add",
    methods=["GET", "POST"]
)
def admin_add_yoga():

    if not session.get("is_admin"):

        return redirect(
            url_for("admin_login")
        )


    from yoga_engine import YOGA_KNOWLEDGE_BASE


    if request.method == "POST":

        name = request.form.get("name")

        goal = request.form.get("goal")

        levels = request.form.getlist("levels")

        age_limit = int(
            request.form.get("age_limit")
        )

        duration = int(
            request.form.get("duration")
        )

        category = request.form.get("category")

        contraindications = request.form.getlist(
            "contraindications"
        )


        # Check duplicate

        if any(

            yoga["name"].lower() == name.lower()

            for yoga in YOGA_KNOWLEDGE_BASE

        ):

            flash(
                "Yogasana already exists."
            )

            return redirect(
                url_for("admin_add_yoga")
            )


        YOGA_KNOWLEDGE_BASE.append({

            "name": name,

            "goals": [goal],

            "levels": levels,

            "age_limit": age_limit,

            "duration": duration,

            "category": category,

            "contraindications": contraindications

        })


        flash(
            "Yogasana added successfully."
        )

        return redirect(
            url_for("admin_yoga")
        )


    return render_template(

        "admin_yoga_form.html",

        yoga=None

    )


# ==========================================
# EDIT YOGASANA
# ==========================================

@app.route(
    "/admin/yoga/edit/<yoga_name>",
    methods=["GET", "POST"]
)
def admin_edit_yoga(yoga_name):

    if not session.get("is_admin"):

        return redirect(
            url_for("admin_login")
        )


    from yoga_engine import YOGA_KNOWLEDGE_BASE


    yoga = next(

        (

            item

            for item in YOGA_KNOWLEDGE_BASE

            if item["name"] == yoga_name

        ),

        None

    )


    if not yoga:

        flash(
            "Yogasana not found."
        )

        return redirect(
            url_for("admin_yoga")
        )


    if request.method == "POST":

        yoga["name"] = request.form.get(
            "name"
        )

        yoga["goals"] = [
            request.form.get("goal")
        ]

        yoga["levels"] = request.form.getlist(
            "levels"
        )

        yoga["age_limit"] = int(
            request.form.get("age_limit")
        )

        yoga["duration"] = int(
            request.form.get("duration")
        )

        yoga["category"] = request.form.get(
            "category"
        )

        yoga["contraindications"] = request.form.getlist(
            "contraindications"
        )


        flash(
            "Yogasana updated successfully."
        )

        return redirect(
            url_for("admin_yoga")
        )


    return render_template(

        "admin_yoga_form.html",

        yoga=yoga

    )


# ==========================================
# DELETE YOGASANA
# ==========================================

@app.route(
    "/admin/yoga/delete/<yoga_name>",
    methods=["POST"]
)
def admin_delete_yoga(yoga_name):

    if not session.get("is_admin"):

        return redirect(
            url_for("admin_login")
        )


    from yoga_engine import YOGA_KNOWLEDGE_BASE


    for yoga in YOGA_KNOWLEDGE_BASE:

        if yoga["name"] == yoga_name:

            YOGA_KNOWLEDGE_BASE.remove(
                yoga
            )

            flash(
                "Yogasana deleted successfully."
            )

            break


    return redirect(
        url_for("admin_yoga")
    )


# =========================
# ADMIN LOGOUT
# =========================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    flash(
        "Admin logged out successfully."
    )

    return redirect(
        url_for("admin_login")
    )


# =========================
# AI YOGA RECOMMENDATION
# =========================

@app.route(
    "/recommendation",
    methods=["GET", "POST"]
)
def recommendation():

    if "user_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )


    if request.method == "POST":

        # Get form data

        try:

            age = int(
                request.form["age"]
            )

            duration = int(
                request.form["duration"]
            )

        except ValueError:

            flash(
                "Please enter valid age and duration."
            )

            return redirect(
                url_for("recommendation")
            )


        fitness_level = request.form[
            "fitness_level"
        ]

        goal = request.form[
            "goal"
        ]

        practice_time = request.form[
            "practice_time"
        ]

        health_conditions = request.form.getlist(
            "health_conditions"
        )


        # Generate AI plan

        yoga_plan = generate_ai_yoga_plan(

            age,

            fitness_level,

            goal,

            duration,

            practice_time,

            health_conditions

        )


        # Save plan

        yoga_plans_collection.insert_one({

            "user_id": session["user_id"],

            "plan": yoga_plan,

            "created_at": datetime.now()

        })


        return render_template(

            "yoga_plan.html",

            plan=yoga_plan

        )


    return render_template(
        "recommendation.html"
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )