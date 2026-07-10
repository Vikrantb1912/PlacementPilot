"""
PlacementPilot AI — Flask Application Entry Point
Powered by IBM watsonx.ai (IBM Granite models)
"""
import os
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any
from logging.handlers import RotatingFileHandler

from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, flash
)
from dotenv import load_dotenv

# ── Load environment variables ────────────────────────────────
load_dotenv()

# ── App factory ───────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "placementpilot-default-secret-change-me")
app.permanent_session_lifetime = timedelta(
    minutes=int(os.getenv("SESSION_LIFETIME_MINUTES", 120))
)

# ── Logging setup ─────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")

file_handler = RotatingFileHandler(
    os.getenv("LOG_FILE", "logs/placementpilot.log"),
    maxBytes=5_000_000, backupCount=3
)
file_handler.setFormatter(formatter)
file_handler.setLevel(log_level)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(log_level)

app.logger.addHandler(file_handler)
app.logger.addHandler(stream_handler)
app.logger.setLevel(log_level)

# ── Import AI service ─────────────────────────────────────────
from modules.ai_service import AIService
from modules.profile_manager import ProfileManager
from modules.dashboard import DashboardEngine
from agent_instructions import (
    COMPANY_GUIDANCE, DSA_ROADMAP, CERTIFICATIONS, DOMAIN_SPECIALIZATION
)

ai_service = AIService()
profile_manager = ProfileManager()
dashboard_engine = DashboardEngine()

# ─────────────────────────────────────────────────────────────
#  HELPER UTILITIES
# ─────────────────────────────────────────────────────────────

def get_current_profile():
    """Return the active student profile from session."""
    return session.get("student_profile", {})

def save_chat_message(role: str, content: str):
    """Append a message to the session chat history."""
    history = session.setdefault("chat_history", [])
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    max_history = int(os.getenv("MAX_CHAT_HISTORY", 50))
    if len(history) > max_history:
        session["chat_history"] = history[-max_history:]
    session.modified = True

# ─────────────────────────────────────────────────────────────
#  CORE ROUTES
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    profile = get_current_profile()
    return render_template("index.html", profile=profile)


@app.route("/setup", methods=["GET", "POST"])
def setup():
    """Student profile setup / onboarding."""
    if request.method == "POST":
        data: dict[str, Any] = request.form.to_dict()
        data["target_companies"] = request.form.getlist("target_companies")
        data["skills"] = request.form.getlist("skills")
        data["profile_id"] = data.get("profile_id") or str(uuid.uuid4())[:8]

        profile_manager.save_profile(data["profile_id"], data)
        session["student_profile"] = data
        session["chat_history"] = []
        session.permanent = True

        flash(f"Welcome aboard, {data.get('name', 'Student')}! 🚀", "success")
        return redirect(url_for("dashboard"))

    companies = list(COMPANY_GUIDANCE.keys())
    domains = list(DOMAIN_SPECIALIZATION.keys())
    existing_profiles = profile_manager.list_profiles()
    return render_template("setup.html", companies=companies,
                           domains=domains, existing_profiles=existing_profiles)


@app.route("/switch-profile/<profile_id>")
def switch_profile(profile_id):
    profile = profile_manager.load_profile(profile_id)
    if profile:
        session["student_profile"] = profile
        session["chat_history"] = []
        session.modified = True
        flash(f"Switched to profile: {profile.get('name', profile_id)}", "info")
    else:
        flash("Profile not found.", "danger")
    return redirect(url_for("dashboard"))


@app.route("/delete-profile/<profile_id>", methods=["POST"])
def delete_profile(profile_id):
    profile_manager.delete_profile(profile_id)
    current = get_current_profile()
    if current.get("profile_id") == profile_id:
        session.pop("student_profile", None)
        session.pop("chat_history", None)
    flash("Profile deleted.", "warning")
    return redirect(url_for("setup"))


@app.route("/dashboard")
def dashboard():
    profile = get_current_profile()
    if not profile:
        return redirect(url_for("setup"))
    stats = dashboard_engine.compute_stats(profile)
    return render_template("dashboard.html", profile=profile, stats=stats)

# ─────────────────────────────────────────────────────────────
#  CHAT / AI ENDPOINT
# ─────────────────────────────────────────────────────────────

@app.route("/chat")
def chat_page():
    profile = get_current_profile()
    if not profile:
        return redirect(url_for("setup"))
    history = session.get("chat_history", [])
    return render_template("chat.html", profile=profile, history=history)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    module_hint = data.get("module", "general")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    profile = get_current_profile()
    history = session.get("chat_history", [])

    save_chat_message("user", user_message)

    try:
        response = ai_service.chat(
            user_message=user_message,
            student_profile=profile,
            chat_history=history,
            module_hint=module_hint
        )
        save_chat_message("assistant", response)
        return jsonify({"response": response, "timestamp": datetime.now().strftime("%H:%M")})
    except Exception as exc:
        app.logger.error("Chat error: %s", exc, exc_info=True)
        return jsonify({"error": "AI service unavailable. Please try again."}), 503


@app.route("/api/clear-chat", methods=["POST"])
def clear_chat():
    session["chat_history"] = []
    session.modified = True
    return jsonify({"status": "cleared"})

# ─────────────────────────────────────────────────────────────
#  MODULE ROUTES
# ─────────────────────────────────────────────────────────────

@app.route("/roadmap")
def roadmap():
    profile = get_current_profile()
    if not profile:
        return redirect(url_for("setup"))
    return render_template("roadmap.html", profile=profile,
                           dsa_roadmap=DSA_ROADMAP,
                           certifications=CERTIFICATIONS)


@app.route("/resume")
def resume():
    profile = get_current_profile()
    if not profile:
        return redirect(url_for("setup"))
    return render_template("resume.html", profile=profile)


@app.route("/interview")
def interview():
    profile = get_current_profile()
    if not profile:
        return redirect(url_for("setup"))
    companies = list(COMPANY_GUIDANCE.keys())
    return render_template("interview.html", profile=profile, companies=companies)


@app.route("/aptitude")
def aptitude():
    profile = get_current_profile()
    if not profile:
        return redirect(url_for("setup"))
    return render_template("aptitude.html", profile=profile)


@app.route("/company-guide")
def company_guide():
    profile = get_current_profile()
    if not profile:
        return redirect(url_for("setup"))
    return render_template("company_guide.html",
                           profile=profile,
                           companies=COMPANY_GUIDANCE)


@app.route("/projects")
def projects():
    profile = get_current_profile()
    if not profile:
        return redirect(url_for("setup"))
    return render_template("projects.html", profile=profile)

# ─────────────────────────────────────────────────────────────
#  MODULE-SPECIFIC AI API ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.route("/api/generate-roadmap", methods=["POST"])
def api_generate_roadmap():
    profile = get_current_profile()
    data = request.get_json(silent=True) or {}
    try:
        result = ai_service.generate_placement_roadmap(profile, data)
        return jsonify({"result": result})
    except Exception as exc:
        app.logger.error("Roadmap error: %s", exc)
        return jsonify({"error": str(exc)}), 503


@app.route("/api/analyze-resume", methods=["POST"])
def api_analyze_resume():
    profile = get_current_profile()
    data = request.get_json(silent=True) or {}
    resume_text = data.get("resume_text", "")
    if not resume_text:
        return jsonify({"error": "Resume text is required"}), 400
    try:
        result = ai_service.analyze_resume(profile, resume_text)
        return jsonify({"result": result})
    except Exception as exc:
        app.logger.error("Resume error: %s", exc)
        return jsonify({"error": str(exc)}), 503


@app.route("/api/mock-interview", methods=["POST"])
def api_mock_interview():
    profile = get_current_profile()
    data = request.get_json(silent=True) or {}
    try:
        result = ai_service.generate_mock_interview(
            profile,
            interview_type=data.get("type", "technical"),
            company=data.get("company", ""),
            topic=data.get("topic", "")
        )
        return jsonify({"result": result})
    except Exception as exc:
        app.logger.error("Interview error: %s", exc)
        return jsonify({"error": str(exc)}), 503


@app.route("/api/aptitude-quiz", methods=["POST"])
def api_aptitude_quiz():
    profile = get_current_profile()
    data = request.get_json(silent=True) or {}
    try:
        result = ai_service.generate_aptitude_questions(
            profile,
            category=data.get("category", "quantitative"),
            difficulty=data.get("difficulty", "medium"),
            count=int(data.get("count", 5))
        )
        return jsonify({"result": result})
    except Exception as exc:
        app.logger.error("Aptitude error: %s", exc)
        return jsonify({"error": str(exc)}), 503


@app.route("/api/project-recommendations", methods=["POST"])
def api_project_recommendations():
    profile = get_current_profile()
    data = request.get_json(silent=True) or {}
    try:
        result = ai_service.recommend_projects(profile, data.get("focus_area", ""))
        return jsonify({"result": result})
    except Exception as exc:
        app.logger.error("Projects error: %s", exc)
        return jsonify({"error": str(exc)}), 503


@app.route("/api/dsa-plan", methods=["POST"])
def api_dsa_plan():
    profile = get_current_profile()
    data = request.get_json(silent=True) or {}
    try:
        result = ai_service.generate_dsa_plan(
            profile,
            weeks=int(data.get("weeks", 8)),
            target_level=data.get("target_level", "Intermediate")
        )
        return jsonify({"result": result})
    except Exception as exc:
        app.logger.error("DSA plan error: %s", exc)
        return jsonify({"error": str(exc)}), 503


@app.route("/api/update-progress", methods=["POST"])
def api_update_progress():
    profile = get_current_profile()
    data = request.get_json(silent=True) or {}
    if not profile:
        return jsonify({"error": "No active profile"}), 400

    profile_id = profile.get("profile_id")
    section = data.get("section")
    value = data.get("value")

    if profile_id and section:
        profile.setdefault("progress", {})[section] = value
        session["student_profile"] = profile
        session.modified = True
        profile_manager.save_profile(profile_id, profile)

    stats = dashboard_engine.compute_stats(profile)
    return jsonify({"stats": stats})

# ─────────────────────────────────────────────────────────────
#  ERROR HANDLERS
# ─────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404,
                           message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500,
                           message="Internal server error"), 500


# ─────────────────────────────────────────────────────────────
#  CONTEXT PROCESSORS
# ─────────────────────────────────────────────────────────────

@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "profile": get_current_profile(),
        "all_profiles": profile_manager.list_profiles(),
    }

# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "True").lower() == "true"
    )
