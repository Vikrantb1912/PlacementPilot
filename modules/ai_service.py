"""
PlacementPilot AI — IBM watsonx.ai Service Layer
Handles all IBM Llama / Granite model interactions via the Chat API (v1.5+).
"""
import os
import logging
from typing import Optional

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference  # type: ignore[import-untyped]
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters  # type: ignore[import-untyped]

from agent_instructions import (
    build_system_prompt,
    COMPANY_GUIDANCE,
    DSA_ROADMAP,
    CERTIFICATIONS,
)

logger = logging.getLogger(__name__)


class AIService:
    """Wraps IBM watsonx.ai Chat API for PlacementPilot features."""

    # ── Chat parameter profiles (TextChatParameters-compatible dicts) ──────
    PARAMS_CHAT = TextChatParameters(
        max_tokens=1024,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.1,
    )

    PARAMS_STRUCTURED = TextChatParameters(
        max_tokens=2048,
        temperature=0.4,
        top_p=0.85,
        repetition_penalty=1.15,
    )

    def __init__(self):
        api_key    = os.getenv("IBM_API_KEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        url        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

        # Primary chat model — must support the Chat API
        self.model_id = os.getenv("GRANITE_MODEL_ID", "meta-llama/llama-3-3-70b-instruct")
        # Structured / long-output model
        self.structured_model_id = os.getenv(
            "GRANITE_CODE_MODEL_ID", "meta-llama/llama-3-3-70b-instruct"
        )

        if not api_key or not project_id:
            logger.warning(
                "IBM_API_KEY or WATSONX_PROJECT_ID not set — AI features will return mock responses."
            )
            self._mock_mode = True
            return

        self._mock_mode = False
        credentials = Credentials(api_key=api_key, url=url)

        # Separate ModelInference instances for chat vs. structured tasks
        self._chat_model = ModelInference(
            model_id=self.model_id,
            credentials=credentials,
            project_id=project_id,
        )
        self._structured_model = ModelInference(
            model_id=self.structured_model_id,
            credentials=credentials,
            project_id=project_id,
        )
        logger.info(
            "AIService initialized — chat: %s | structured: %s",
            self.model_id,
            self.structured_model_id,
        )

    # ── Internal helpers ─────────────────────────────────────────────────

    def _call(self, messages: list[dict], structured: bool = False) -> str:
        """Send a chat messages list to IBM watsonx.ai Chat API."""

        if self._mock_mode:
            return self._mock_response()

        model = self._structured_model if structured else self._chat_model
        params = self.PARAMS_STRUCTURED if structured else self.PARAMS_CHAT

        try:
            response = model.chat(
                messages=messages,
                params=params,
            )
            # Extract the assistant reply from the standard Chat API response shape:
            # {"choices": [{"message": {"content": "..."}}]}
            content = (
                response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            return content.strip() if content else "No response generated."

        except Exception as exc:
            logger.error("watsonx Chat API error: %s", exc, exc_info=True)
            raise RuntimeError(
                f"IBM watsonx Chat API error: {exc}"
            ) from exc
        
    @staticmethod
    def _mock_response() -> str:
        """Return a placeholder when credentials are not configured."""
        return (
            "⚠️ **Demo Mode** — IBM watsonx.ai credentials are not configured.\n\n"
            "Please add your `IBM_API_KEY` and `WATSONX_PROJECT_ID` to the `.env` file "
            "to enable full AI-powered responses.\n\n"
            "**What to do:**\n"
            "1. Copy `.env.example` → `.env`\n"
            "2. Fill in your IBM Cloud API Key and watsonx.ai Project ID\n"
            "3. Restart the application\n\n"
            "_Your question was recorded and will be answered once credentials are set._"
        )

    @staticmethod
    def _build_messages(system: str, history: list, user_msg: str) -> list[dict]:
        """Build an OpenAI-style messages list from system prompt, history, and user input."""
        messages: list[dict] = [{"role": "system", "content": system}]
        for msg in history[-10:]:  # last 10 turns for context
            role    = msg.get("role", "user")
            content = msg.get("content", "")
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_msg})
        return messages

    # ── Public API ───────────────────────────────────────────────────────

    def chat(self, user_message: str, student_profile: dict,
             chat_history: list, module_hint: str = "general") -> str:
        """General chat endpoint — routes message to appropriate context."""
        system = build_system_prompt(student_profile)

        module_contexts = {
            "dsa":       "Focus on DSA topics, algorithms, and coding practice.",
            "resume":    "Focus on resume review, ATS optimization, and improvements.",
            "interview": "Focus on mock interview questions and ideal answers.",
            "aptitude":  "Focus on aptitude, reasoning, and verbal practice.",
            "roadmap":   "Focus on personalized placement preparation roadmap.",
            "company":   "Focus on company-specific interview strategies and culture.",
            "projects":  "Focus on project recommendations and portfolio building.",
            "hr":        "Focus on HR, behavioral interview, and STAR stories.",
        }
        if module_hint in module_contexts:
            system += f"\n\nCURRENT MODULE CONTEXT: {module_contexts[module_hint]}"

        messages = self._build_messages(system, chat_history, user_message)
        return self._call(messages)

    def generate_placement_roadmap(self, profile: dict, options: dict) -> str:
        """Generate a personalized placement preparation roadmap."""
        weeks   = options.get("weeks", 12)
        system  = build_system_prompt(profile)
        name    = profile.get("name", "the student")
        branch  = profile.get("branch", "CSE")
        level   = profile.get("skill_level", "Intermediate")
        targets = ", ".join(profile.get("target_companies", ["TCS", "Infosys"]))

        user_msg = f"""Generate a detailed {weeks}-week placement preparation roadmap for {name}.
- Branch: {branch}
- Current Skill Level: {level}
- Target Companies: {targets}
- Career Goal: {profile.get('career_goal', 'Software Development')}

Structure the roadmap as:
1. Phase breakdown (weeks)
2. Weekly DSA topics and goals
3. Development skills to build
4. Projects to build during the roadmap
5. Mock interview milestones
6. Certifications to pursue
7. Company-specific preparation timeline
8. Weekly time commitment (hours/day)

Be specific, actionable, and motivating."""

        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_msg},
        ]
        return self._call(messages, structured=True)

    def analyze_resume(self, profile: dict, resume_text: str) -> str:
        """Analyze resume and provide improvement suggestions."""
        system  = build_system_prompt(profile)
        targets = ", ".join(profile.get("target_companies", ["TCS"]))

        user_msg = f"""Analyze the following resume for a student targeting: {targets}

RESUME:
{resume_text[:3000]}

Provide a comprehensive analysis covering:
1. **ATS Score Estimate** (out of 100) and reasons
2. **Strengths** — what's good about this resume
3. **Weaknesses** — critical gaps and issues
4. **Missing Sections** — what should be added
5. **Action Verb Improvements** — weak phrases → strong alternatives
6. **Quantification Opportunities** — where to add numbers/metrics
7. **Skills Section** — missing technical skills relevant to target companies
8. **Project Section** — how to make projects stand out
9. **Summary/Objective** — rewrite suggestion
10. **Top 5 Priority Fixes** — ranked by impact

Format clearly with headings and bullet points."""

        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_msg},
        ]
        return self._call(messages, structured=True)

    def generate_mock_interview(self, profile: dict, interview_type: str,
                                company: str, topic: str) -> str:
        """Generate mock interview questions with ideal answers."""
        system      = build_system_prompt(profile)
        level       = profile.get("skill_level", "Intermediate")
        company_ctx = ""
        if company and company in COMPANY_GUIDANCE:
            cg          = COMPANY_GUIDANCE[company]
            company_ctx = f"\nCompany Focus: {cg['focus']}\nInterview Process: {cg['rounds']}"

        type_instructions = {
            "technical":     f"Generate 5 technical coding/DSA questions on topic: {topic or 'Arrays & Strings'}. For each: question → hints → optimal solution with complexity.",
            "system_design": f"Generate 2 system design questions appropriate for {level} level. Walk through requirements → design → trade-offs.",
            "hr":             "Generate 8 HR/behavioral questions using STAR framework. Include ideal answer structures and sample answers.",
            "aptitude":      f"Generate 10 aptitude questions (mix of quantitative, logical, verbal) at {level} level with solutions.",
        }
        instruction = type_instructions.get(interview_type, type_instructions["technical"])

        user_msg = f"""Mock Interview Session — Type: {interview_type.upper()}
{company_ctx}

{instruction}

For each question, provide:
- **Question**: Clear problem statement
- **Expected Answer**: What the interviewer looks for
- **Ideal Response**: Complete well-structured answer
- **Common Mistakes**: What candidates get wrong
- **Follow-up**: Likely follow-up question

Make it feel like a real interview. Be challenging but fair for {level} level."""

        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_msg},
        ]
        return self._call(messages, structured=True)

    def generate_aptitude_questions(self, profile: dict, category: str,
                                    difficulty: str, count: int) -> str:
        """Generate aptitude practice questions."""
        system  = build_system_prompt(profile)
        targets = ", ".join(profile.get("target_companies", ["TCS"]))

        user_msg = f"""Generate {count} {difficulty}-difficulty {category} aptitude questions.
These are for a student targeting: {targets}

For each question provide:
1. **Question** (with options A, B, C, D for MCQs)
2. **Answer**: Correct option
3. **Solution**: Step-by-step explanation
4. **Shortcut**: Faster method if applicable
5. **Similar Pattern**: Type of question to practice more

Categories covered: {category}
Difficulty: {difficulty}"""

        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_msg},
        ]
        return self._call(messages, structured=True)

    def recommend_projects(self, profile: dict, focus_area: str) -> str:
        """Recommend projects based on student profile."""
        system  = build_system_prompt(profile)
        branch  = profile.get("branch", "CSE")
        level   = profile.get("skill_level", "Intermediate")
        goal    = profile.get("career_goal", "Software Development")
        targets = ", ".join(profile.get("target_companies", ["TCS"]))

        user_msg = f"""Recommend 6 impactful projects for a {branch} student targeting {targets}.
Skill Level: {level} | Career Goal: {goal}
{f"Focus Area: {focus_area}" if focus_area else ""}

For each project provide:
1. **Project Name & One-line Description**
2. **Tech Stack** (specific technologies)
3. **Key Features** to implement (3-5 bullet points)
4. **Complexity Level** and estimated time
5. **Resume Impact** — how to describe it impressively
6. **Interview Talking Points** — what to highlight
7. **GitHub / Deployment** — where to host
8. **Unique Twist** — what makes it stand out from generic projects

Include a mix of: beginner-friendly, medium complexity, and advanced showcase projects."""

        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_msg},
        ]
        return self._call(messages, structured=True)

    def generate_dsa_plan(self, profile: dict, weeks: int, target_level: str) -> str:
        """Generate a week-by-week DSA study plan."""
        system        = build_system_prompt(profile)
        current_level = profile.get("skill_level", "Beginner")
        topics        = DSA_ROADMAP.get(target_level, DSA_ROADMAP["Intermediate"])

        user_msg = f"""Create a {weeks}-week DSA study plan to take a student from {current_level} to {target_level} level.

Topics to cover: {', '.join(topics)}

For each week provide:
1. **Week X: [Topic Name]**
2. **Daily Schedule** (what to study each day, 2-3 hours/day)
3. **LeetCode Problems** (5-10 specific problems with difficulty)
4. **Key Concepts** to master
5. **Resources** (specific YouTube channels, articles, books)
6. **Weekly Goal** — measurable milestone
7. **Practice Platform** suggestions

Also include:
- Revision strategy
- Mock test schedule (1 test every 2 weeks)
- Tracking system recommendation"""

        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_msg},
        ]
        return self._call(messages, structured=True)
