import sys
import io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Test imports
import config
from database.db import (
    init_db, get_all_topics, update_topic_completion, log_daily_checkin,
    get_checkin_by_date, get_all_checkins, log_aptitude_session,
    get_aptitude_sessions, add_error_quarantine, get_quarantined_errors,
    update_error_mastery, get_formula_vault, update_formula_review,
    get_setting, set_setting
)
from engine.ai_planner import generate_next_day_action_plan, generate_heuristic_action_plan
from engine.analytics import calculate_dashboard_metrics, get_error_distribution, calculate_backlog_recovery
from engine.spaced_repetition import get_due_formula_cards, process_formula_feedback, get_formula_deck_statistics

# Test components modules
from components.attendance_form import render_attendance_form
from components.dashboard_view import render_dashboard_view
from components.resource_hub import render_resource_hub
from components.formula_vault import render_formula_vault
from components.virtual_calc import render_virtual_calc, eval_safe
from components.pomodoro_timer import render_pomodoro_timer
from components.error_quarantine import render_error_quarantine
from components.aptitude_tracker import render_aptitude_tracker

def smoke_test_all():
    print("Executing full smoke test on engine and database...")
    init_db()
    
    # Check topics
    topics = get_all_topics()
    assert len(topics) >= 50
    print(f"  -> All {len(topics)} IN & RA topics loaded successfully")
    
    # Test setting
    set_setting("target_paper", "RA")
    assert get_setting("target_paper") == "RA"
    set_setting("target_paper", "IN")
    print("  -> User settings CRUD working")
    
    # Test analytics
    m = calculate_dashboard_metrics()
    assert m["total_topics"] >= 50
    assert "domain_stats" in m
    print("  -> Dashboard metrics computed successfully")
    
    # Test error Pareto
    e = get_error_distribution()
    assert len(e["breakdown"]) == 6
    print("  -> Error distribution computed successfully")
    
    # Test backlog recovery
    r = calculate_backlog_recovery()
    assert "required_topics_per_week" in r
    print("  -> Backlog recovery engine functional")
    
    # Test spaced repetition
    f_stats = get_formula_deck_statistics()
    assert f_stats["total_cards"] >= 50
    print("  -> Spaced repetition statistics working")
    
    # Test AI Action Plan heuristic generation
    plan = generate_heuristic_action_plan(
        primary_topic=topics[0],
        study_window_hours=2.0,
        recall_mins=20,
        theory_mins=50,
        pyq_mins=50,
        recent_errors=["C", "S"],
        roadblocks="Confusion with matrix rank edge cases"
    )
    assert "Part 1: Recall Session" in plan
    assert "Part 2: Theory Deep Dive" in plan
    assert "Part 3: Targeted PYQ Problem Set" in plan
    assert "Confusion with matrix rank edge cases" in plan
    print("  -> AI Action Plan generator functional with state injection")
    
    print("\nALL SMOKE TESTS PASSED CLEANLY WITH 100% SUCCESS!")

if __name__ == "__main__":
    smoke_test_all()
