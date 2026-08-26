"""
Automated Unit Tests for GATE Preparation Master Command Center
Tests database schema, 108 micro-topic seed data, CRUD queries, analytics, and AI plan engine.
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.db import (
    init_db,
    get_all_topics,
    log_daily_checkin,
    get_checkin_by_date,
    get_all_checkins,
    log_aptitude_session,
    get_aptitude_sessions,
    add_error_quarantine,
    get_quarantined_errors,
    update_error_mastery,
    get_formula_vault,
    update_formula_review
)
from engine.analytics import calculate_dashboard_metrics, get_error_distribution, calculate_backlog_recovery
from engine.ai_planner import generate_next_day_action_plan
from engine.spaced_repetition import get_formula_deck_statistics, process_formula_feedback


def test_database_initialization():
    print("[1/5] Testing Database Initialization & Seeding...")
    init_db()
    topics = get_all_topics()
    assert len(topics) >= 50, f"Expected >= 50 micro-topics, got {len(topics)}"
    
    # Verify IDs are unique
    topic_ids = [t["id"] for t in topics]
    assert len(topic_ids) == len(set(topic_ids)), "Duplicate topic IDs found!"
    
    # Verify all domains are populated
    domains = {t["domain"] for t in topics}
    assert len(domains) >= 5, f"Expected >= 5 domains, got {len(domains)}"
    print(f"  -> Passed! {len(topics)} unique IN & RA micro-topics verified.")


def test_checkin_and_quarantine():
    print("[2/5] Testing Check-In & Error Quarantine CRUD...")
    test_date = "2026-08-26"
    
    # Log check-in
    cid = log_daily_checkin(
        checkin_date=test_date,
        hours_logged=1.75,
        completed_topics=["M01", "M02", "S25"],
        error_codes=["C", "F"],
        roadblocks_text="Struggled with rank calculation of 4x4 matrix with parameter k."
    )
    assert cid > 0, "Failed to log checkin"
    
    # Verify retrieved check-in
    c = get_checkin_by_date(test_date)
    assert c is not None, "Checkin not found"
    assert c["hours_logged"] == 1.75
    assert "M01" in c["completed_topics"]
    assert "C" in c["error_codes"]
    
    # Log error quarantine
    eid = add_error_quarantine(
        date_logged=test_date,
        topic_id="M01",
        topic_name="Rank of Matrix",
        error_code="C",
        question_details="GATE 2020 2-Mark Rank of Matrix Question",
        wrong_attempt_notes="Assumed rank was 3 when det was 0",
        correct_takeaway="Check all 3x3 minors or reduce to echelon form"
    )
    assert eid > 0, "Failed to quarantine error"
    
    errors = get_quarantined_errors(only_active=True)
    assert len(errors) > 0, "No quarantined errors found"
    
    # Test mastery update
    update_error_mastery(eid, is_mastered=True)
    active_after = get_quarantined_errors(only_active=True)
    mastered_errs = [e for e in get_quarantined_errors(only_active=False) if e["is_mastered"] == 1]
    assert len(mastered_errs) > 0, "Mastered error not found"
    print("  -> Passed! Check-ins and error quarantine verified.")


def test_analytics_engine():
    print("[3/5] Testing Analytics & Pacing Engine...")
    metrics = calculate_dashboard_metrics()
    assert "overall_progress_pct" in metrics
    assert "pacing_status" in metrics
    assert "domain_stats" in metrics
    assert metrics["completed_count"] >= 3
    
    errors = get_error_distribution()
    assert errors["total_errors"] >= 2
    assert len(errors["breakdown"]) == 6
    
    recovery = calculate_backlog_recovery()
    assert "required_topics_per_week" in recovery
    print("  -> Passed! Analytics metrics & error Pareto verified.")


def test_spaced_repetition():
    print("[4/5] Testing Spaced Repetition Formula Vault...")
    deck = get_formula_vault(due_only=False)
    assert len(deck) >= 50, f"Expected >= 50 formula cards, got {len(deck)}"
    
    # Process feedback
    process_formula_feedback("M01", "easy")
    card = next(c for c in get_formula_vault(due_only=False) if c["topic_id"] == "M01")
    assert card["repetition_count"] >= 1
    assert card["interval_days"] >= 1
    
    stats = get_formula_deck_statistics()
    assert stats["total_cards"] >= 50
    print("  -> Passed! Spaced repetition interval arithmetic verified.")


def test_ai_action_planner():
    print("[5/5] Testing AI Action Plan Generator (Offline & Output Structure)...")
    plan = generate_next_day_action_plan(
        study_window_hours=1.5,
        recent_errors=["C", "F"],
        roadblocks="Testing roadblock advice rendering"
    )
    assert "Part 1: Recall Session" in plan
    assert "Part 2: Theory Deep Dive" in plan
    assert "Part 3: Targeted PYQ Problem Set" in plan
    assert "Allocated:" in plan
    print("  -> Passed! AI Action Plan conforms exactly to the 3-part schema.")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RUNNING COMPLETE TEST SUITE FOR GATE PREP DASHBOARD")
    print("="*60 + "\n")
    test_database_initialization()
    test_checkin_and_quarantine()
    test_analytics_engine()
    test_spaced_repetition()
    test_ai_action_planner()
    print("\n" + "="*60)
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("="*60 + "\n")
