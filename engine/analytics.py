"""
Analytics & Pacing Engine for GATE Preparation Command Center
Computes 23-week baseline trajectories, error Pareto distributions, and study velocity.
"""
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from database.db import get_all_topics, get_all_checkins, get_setting, get_aptitude_sessions
from config import TOTAL_WEEKS, DAILY_STUDY_CAP_HOURS, ERROR_TAXONOMY


def calculate_dashboard_metrics() -> Dict[str, Any]:
    """Calculates all primary metrics for the dynamic dashboard."""
    topics = get_all_topics()
    checkins = get_all_checkins()
    aptitude_records = get_aptitude_sessions()

    total_topics = len(topics)
    completed_topics = [t for t in topics if t["is_completed"]]
    completed_count = len(completed_topics)
    overall_progress_pct = (completed_count / total_topics * 100) if total_topics > 0 else 0.0

    # Start date & current week calculation
    start_date_str = get_setting("start_date", date.today().strftime("%Y-%m-%d"))
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        start_date = date.today()

    today = date.today()
    days_elapsed = max(0, (today - start_date).days)
    current_week = min(TOTAL_WEEKS, max(1, (days_elapsed // 7) + 1))
    days_remaining = max(0, (TOTAL_WEEKS * 7) - days_elapsed)

    # 23-Week Expected Baseline Target
    # Baseline expects topics to be covered uniformly across 23 weeks (~4.7 topics/week)
    target_topics_for_current_week = int((current_week / TOTAL_WEEKS) * total_topics)
    pacing_delta = completed_count - target_topics_for_current_week

    if pacing_delta >= 2:
        pacing_status = f"🟢 Ahead by {pacing_delta} topics"
        pacing_color = "#10B981"
        pacing_index = (completed_count / max(1, target_topics_for_current_week)) * 100
    elif pacing_delta >= -2:
        pacing_status = "🟡 On Track with Baseline"
        pacing_color = "#F59E0B"
        pacing_index = 100.0
    else:
        pacing_status = f"🔴 Lagging by {abs(pacing_delta)} topics"
        pacing_color = "#EF4444"
        pacing_index = (completed_count / max(1, target_topics_for_current_week)) * 100

    # Total Hours Logged & Streak
    total_hours = sum(c["hours_logged"] for c in checkins)
    total_aptitude_hours = sum(a["hours_logged"] for a in aptitude_records)
    combined_study_hours = total_hours + total_aptitude_hours

    # Calculate Study Streak
    streak = 0
    if checkins:
        dates_logged = {c["date"] for c in checkins}
        check_day = today
        # Check if today or yesterday was logged
        if check_day.strftime("%Y-%m-%d") not in dates_logged:
            check_day = check_day - timedelta(days=1)
        
        while check_day.strftime("%Y-%m-%d") in dates_logged:
            streak += 1
            check_day -= timedelta(days=1)

    # Domain-wise Breakdown
    domain_stats = {}
    for t in topics:
        dom = t["domain"]
        if dom not in domain_stats:
            domain_stats[dom] = {"total": 0, "completed": 0}
        domain_stats[dom]["total"] += 1
        if t["is_completed"]:
            domain_stats[dom]["completed"] += 1

    for dom in domain_stats:
        tot = domain_stats[dom]["total"]
        comp = domain_stats[dom]["completed"]
        domain_stats[dom]["pct"] = round((comp / tot * 100), 1) if tot > 0 else 0.0

    return {
        "total_topics": total_topics,
        "completed_count": completed_count,
        "overall_progress_pct": round(overall_progress_pct, 1),
        "current_week": current_week,
        "total_weeks": TOTAL_WEEKS,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "target_topics": target_topics_for_current_week,
        "pacing_delta": pacing_delta,
        "pacing_status": pacing_status,
        "pacing_color": pacing_color,
        "pacing_index": round(pacing_index, 1),
        "total_hours": round(combined_study_hours, 1),
        "streak_days": streak,
        "domain_stats": domain_stats
    }


def get_error_distribution() -> Dict[str, Any]:
    """Computes Pareto distribution for the 6 error classifications."""
    checkins = get_all_checkins()
    error_counts = {code: 0 for code in ERROR_TAXONOMY}

    for c in checkins:
        for code in c.get("error_codes", []):
            if code in error_counts:
                error_counts[code] += 1

    total_errors = sum(error_counts.values())
    error_data = []
    for code, count in error_counts.items():
        pct = round((count / total_errors * 100), 1) if total_errors > 0 else 0.0
        error_data.append({
            "code": code,
            "name": ERROR_TAXONOMY[code]["name"],
            "count": count,
            "percentage": pct,
            "icon": ERROR_TAXONOMY[code]["icon"],
            "color": ERROR_TAXONOMY[code]["color"]
        })

    # Sort descending by count
    error_data.sort(key=lambda x: x["count"], reverse=True)
    return {
        "total_errors": total_errors,
        "breakdown": error_data
    }


def calculate_backlog_recovery() -> Dict[str, Any]:
    """Calculates adaptive recovery pace if the candidate is lagging."""
    metrics = calculate_dashboard_metrics()
    remaining_topics = metrics["total_topics"] - metrics["completed_count"]
    remaining_days = max(1, metrics["days_remaining"])
    remaining_weeks = max(1, remaining_days // 7)

    required_topics_per_week = round(remaining_topics / remaining_weeks, 1)
    recommended_daily_window = min(
        DAILY_STUDY_CAP_HOURS,
        max(1.0, round((required_topics_per_week * 1.5) / 6, 2))
    )

    return {
        "remaining_topics": remaining_topics,
        "remaining_weeks": remaining_weeks,
        "remaining_days": remaining_days,
        "required_topics_per_week": required_topics_per_week,
        "recommended_daily_window": recommended_daily_window,
        "is_lagging": metrics["pacing_delta"] < -2
    }
