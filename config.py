"""
Configuration and Metadata for GATE IN & RA Preparation Master Command Center
Strictly tailored for Instrumentation Engineering (IN) and Robotics & Automation (RA).
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "gate_prep.db"

# 23-Week Cycle Duration
TOTAL_WEEKS = 23
DAILY_STUDY_CAP_HOURS = 2.0
WEEKEND_APTITUDE_HOURS = 2.0

# Supported GATE Papers (Strictly IN & RA)
PAPERS = {
    "IN": "Instrumentation Engineering (IN)",
    "RA": "Robotics & Automation (RA)",
    "DUAL": "Dual Aspirant (IN + RA Combined)"
}

# Domains strictly for GATE IN & RA
DOMAINS = [
    "Engineering Mathematics",
    "IN - Sensors & Industrial Transducers",
    "IN - Circuits & Analog/Digital Electronics",
    "IN - Signals & Control Systems",
    "RA - Robot Kinematics & Jacobians",
    "RA - Dynamics, Actuators & Robot Vision",
    "RA - Industrial Automation & PLCs",
    "General Aptitude (Weekend)",
    "Comprehensive Revision & Mock Sprints"
]

# Standardized 6-Error Diagnostic Taxonomy
ERROR_TAXONOMY = {
    "C": {
        "name": "Conceptual Gap",
        "description": "Misunderstood fundamental physical/mathematical principle or theory.",
        "icon": "🧠",
        "color": "#EF4444"
    },
    "F": {
        "name": "Formula / Recall Failure",
        "description": "Forgot or misremembered a standard formula, value, or definition.",
        "icon": "📝",
        "color": "#F59E0B"
    },
    "A": {
        "name": "Application / Strategy Deficit",
        "description": "Chose an inappropriate approach or sub-optimal solving method.",
        "icon": "🧭",
        "color": "#3B82F6"
    },
    "I": {
        "name": "Interpretation / Reading Slip",
        "description": "Misread problem constraints, boundary conditions, units, or question wording.",
        "icon": "🔍",
        "color": "#8B5CF6"
    },
    "T": {
        "name": "Time Pressure Mismanagement",
        "description": "Spent excessive time (>4 min) or rushed under clock pressure.",
        "icon": "⏱️",
        "color": "#EC4899"
    },
    "S": {
        "name": "Silly / Calculation Slip",
        "description": "Virtual calculator typo, arithmetic error, or sign inversion on a solved problem.",
        "icon": "⚠️",
        "color": "#10B981"
    }
}
