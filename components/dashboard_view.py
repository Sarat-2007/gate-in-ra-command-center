"""
Dashboard View Component with Interactive Plotly Visualizations
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from engine.analytics import calculate_dashboard_metrics, get_error_distribution, calculate_backlog_recovery


def render_dashboard_view() -> None:
    st.subheader("📊 Dynamic Analytics & 23-Week Pacing Dashboard")
    st.caption("Track syllabus clearance velocity against the 23-week baseline, inspect error Pareto distributions, and maintain study streaks.")

    metrics = calculate_dashboard_metrics()
    errors = get_error_distribution()
    recovery = calculate_backlog_recovery()

    # Top KPI Metrics Bar
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.metric(
            label="Syllabus Cleared",
            value=f"{metrics['overall_progress_pct']}%",
            delta=f"{metrics['completed_count']} / {metrics['total_topics']} Topics"
        )
    with kpi_col2:
        st.metric(
            label="23-Week Pacing Index",
            value=f"{metrics['pacing_index']}%",
            delta=metrics['pacing_status'],
            delta_color="normal"
        )
    with kpi_col3:
        st.metric(
            label="Timeline Status",
            value=f"Week {metrics['current_week']} / {metrics['total_weeks']}",
            delta=f"{metrics['days_remaining']} Days to Target"
        )
    with kpi_col4:
        st.metric(
            label="Total Study Logged",
            value=f"{metrics['total_hours']} hrs",
            delta=f"🔥 {metrics['streak_days']} Day Streak"
        )

    # Lagging Recovery Banner
    if recovery["is_lagging"]:
        st.warning(
            f"⚠️ **Backlog Recovery Alert**: You are currently lagging behind the 23-week baseline pace. "
            f"To complete the syllabus comfortably, target **{recovery['required_topics_per_week']} topics/week** "
            f"with a recommended daily study window of **{recovery['recommended_daily_window']} hours**."
        )

    st.markdown("---")

    # Visual Charts Row 1: Pacing Gauge & Domain Progress
    row1_col1, row1_col2 = st.columns([1, 1.2])

    with row1_col1:
        st.markdown("#### 🎯 Velocity Gauge vs 23-Week Baseline")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=metrics["completed_count"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Expected Target: {metrics['target_topics']} Topics", 'font': {'size': 14}},
            delta={'reference': metrics["target_topics"], 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge={
                'axis': {'range': [0, metrics["total_topics"]], 'tickwidth': 1},
                'bar': {'color': metrics["pacing_color"]},
                'steps': [
                    {'range': [0, metrics["target_topics"] * 0.8], 'color': "rgba(239, 68, 68, 0.15)"},
                    {'range': [metrics["target_topics"] * 0.8, metrics["target_topics"]], 'color': "rgba(245, 158, 11, 0.15)"},
                    {'range': [metrics["target_topics"], metrics["total_topics"]], 'color': "rgba(16, 185, 129, 0.15)"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 3},
                    'thickness': 0.8,
                    'value': metrics["target_topics"]
                }
            }
        ))
        fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with row1_col2:
        st.markdown("#### 📚 Domain-Wise Syllabus Completion")
        domain_names = list(metrics["domain_stats"].keys())
        domain_pcts = [metrics["domain_stats"][d]["pct"] for d in domain_names]
        domain_labels = [f"{d} ({metrics['domain_stats'][d]['completed']}/{metrics['domain_stats'][d]['total']})" for d in domain_names]

        fig_domain = go.Figure(go.Bar(
            x=domain_pcts,
            y=domain_labels,
            orientation='h',
            marker=dict(
                color=domain_pcts,
                colorscale='Viridis',
                showscale=False
            ),
            text=[f"{p}%" for p in domain_pcts],
            textposition='outside'
        ))
        fig_domain.update_layout(
            xaxis=dict(range=[0, 105], title="Completion (%)"),
            yaxis=dict(autorange="reversed"),
            height=280,
            margin=dict(l=10, r=20, t=10, b=30)
        )
        st.plotly_chart(fig_domain, use_container_width=True)

    st.markdown("---")

    # Visual Charts Row 2: Error Pareto & Taxonomy Insights
    st.markdown("#### 🔬 Diagnostic Error Pareto Analysis (Root-Cause Breakdown)")
    st.caption("Distribution of practice errors across all logged sessions. Focus your active recall on the tallest bars.")

    if errors["total_errors"] > 0:
        error_df_codes = [f"{e['icon']} [{e['code']}] {e['name']}" for e in errors["breakdown"]]
        error_df_counts = [e["count"] for e in errors["breakdown"]]
        error_df_colors = [e["color"] for e in errors["breakdown"]]

        fig_error = go.Figure(go.Bar(
            x=error_df_codes,
            y=error_df_counts,
            marker_color=error_df_colors,
            text=error_df_counts,
            textposition='auto'
        ))
        fig_error.update_layout(
            xaxis_title="Diagnostic Error Classification",
            yaxis_title="Total Errors Logged",
            height=280,
            margin=dict(l=20, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_error, use_container_width=True)
    else:
        st.info("No practice errors logged yet. Check off errors in the Daily Check-In tab to generate your diagnostic Pareto chart.")
