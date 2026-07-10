"""
PlacementPilot AI — Dashboard Stats Engine
Computes placement readiness scores and progress metrics.
"""
import logging

logger = logging.getLogger(__name__)


class DashboardEngine:
    """Compute dashboard statistics from a student profile."""

    SECTIONS = [
        "dsa", "development", "projects", "certifications",
        "resume", "mock_interviews", "aptitude", "hr_prep",
    ]

    SECTION_WEIGHTS = {
        "dsa":            25,
        "development":    20,
        "projects":       15,
        "certifications":  5,
        "resume":         10,
        "mock_interviews": 10,
        "aptitude":       10,
        "hr_prep":         5,
    }

    SECTION_LABELS = {
        "dsa":            "DSA & Algorithms",
        "development":    "Development Skills",
        "projects":       "Project Portfolio",
        "certifications": "Certifications",
        "resume":         "Resume Quality",
        "mock_interviews":"Mock Interviews",
        "aptitude":       "Aptitude Practice",
        "hr_prep":        "HR Preparation",
    }

    LEVEL_DEFAULTS = {
        "Beginner":     {"dsa": 10, "development": 15, "projects": 5,
                         "certifications": 0, "resume": 20, "mock_interviews": 0,
                         "aptitude": 10, "hr_prep": 5},
        "Intermediate": {"dsa": 35, "development": 40, "projects": 25,
                         "certifications": 10, "resume": 40, "mock_interviews": 15,
                         "aptitude": 30, "hr_prep": 20},
        "Advanced":     {"dsa": 65, "development": 70, "projects": 60,
                         "certifications": 30, "resume": 70, "mock_interviews": 40,
                         "aptitude": 60, "hr_prep": 40},
    }

    def compute_stats(self, profile: dict) -> dict:
        level = profile.get("skill_level", "Beginner")
        defaults = self.LEVEL_DEFAULTS.get(level, self.LEVEL_DEFAULTS["Beginner"])
        progress = profile.get("progress", {})

        section_progress = {}
        for sec in self.SECTIONS:
            raw = progress.get(sec, defaults.get(sec, 0))
            section_progress[sec] = max(0, min(100, int(raw)))

        # Weighted readiness score
        total_weight = sum(self.SECTION_WEIGHTS.values())
        readiness = sum(
            section_progress[s] * self.SECTION_WEIGHTS[s]
            for s in self.SECTIONS
        ) / total_weight

        # Identify strengths and weaknesses
        sorted_sections = sorted(
            self.SECTIONS,
            key=lambda s: section_progress[s],
            reverse=True
        )
        strengths = [
            self.SECTION_LABELS[s]
            for s in sorted_sections[:3]
            if section_progress[s] >= 50
        ]
        weaknesses = [
            self.SECTION_LABELS[s]
            for s in sorted_sections[-3:]
            if section_progress[s] < 50
        ]

        # Next steps
        next_steps = self._recommend_next_steps(section_progress, level)

        # Interview readiness (DSA + dev + mock interviews)
        interview_readiness = int(
            0.4 * section_progress["dsa"] +
            0.3 * section_progress["development"] +
            0.3 * section_progress["mock_interviews"]
        )

        return {
            "section_progress": section_progress,
            "section_labels": self.SECTION_LABELS,
            "readiness_score": round(readiness, 1),
            "interview_readiness": interview_readiness,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "next_steps": next_steps,
            "level": level,
        }

    def _recommend_next_steps(self, progress: dict, level: str) -> list:
        steps = []
        thresholds = {"Beginner": 30, "Intermediate": 50, "Advanced": 70}
        threshold = thresholds.get(level, 40)
        for sec in self.SECTIONS:
            if progress[sec] < threshold:
                label = self.SECTION_LABELS[sec]
                steps.append(f"Improve {label} (currently {progress[sec]}%)")
        return steps[:4] if steps else ["🎉 Great progress! Focus on mock interviews now."]
