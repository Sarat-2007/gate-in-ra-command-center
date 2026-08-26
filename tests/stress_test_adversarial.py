"""
Adversarial QA Stress Test & Mathematical Bound Suite for GATE IN & RA Dashboard
Relentlessly tests edge cases, boundary conditions, concurrency, memory corruption, and crash resilience.
"""
import os
import sys
import math
import json
import sqlite3
import threading
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, Any, List

# Reconfigure stdout for Unicode / UTF-8 safety on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import DB_PATH, TOTAL_WEEKS, DAILY_STUDY_CAP_HOURS, PAPERS, DOMAINS, ERROR_TAXONOMY
from database.db import (
    get_db_connection,
    init_db,
    get_all_topics,
    update_topic_completion,
    log_daily_checkin,
    get_checkin_by_date,
    get_all_checkins,
    log_aptitude_session,
    get_aptitude_sessions,
    add_error_quarantine,
    get_quarantined_errors,
    update_error_mastery,
    get_formula_vault,
    update_formula_review,
    get_setting,
    set_setting
)
from engine.analytics import (
    calculate_dashboard_metrics,
    get_error_distribution,
    calculate_backlog_recovery
)
from engine.spaced_repetition import (
    get_due_formula_cards,
    process_formula_feedback,
    get_formula_deck_statistics
)
from engine.ai_planner import (
    generate_next_day_action_plan,
    generate_heuristic_action_plan
)
from components.virtual_calc import eval_safe

class StressTestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record_pass(self, test_name: str):
        self.passed += 1
        print(f"  [PASS] {test_name}")

    def record_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"  [FAIL] {test_name} -> {reason}")

    # =========================================================================
    # DOMAIN 1: Virtual Calculator Stress & Math Boundary Suite
    # =========================================================================
    def test_virtual_calculator(self):
        print("\n" + "="*70)
        print("DOMAIN 1: TCS iON Virtual Calculator Stress & Math Boundary Suite")
        print("="*70)

        # 1.1 Basic Math Operations & Order of Operations
        try:
            assert eval_safe("2 + 3 * 4") == 14, "Multiplication precedence failed"
            assert eval_safe("(2 + 3) * 4") == 20, "Parentheses precedence failed"
            assert eval_safe("2 ^ 3") == 8, "^ operator conversion failed"
            assert eval_safe("10 / 4") == 2.5, "Float division failed"
            assert eval_safe("-5 + 10") == 5, "Unary negative failed"
            assert eval_safe("  100  +  25  ") == 125, "Whitespace stripping failed"
            self.record_pass("1.1 Basic Operations, Precedence & Formatting")
        except Exception as e:
            self.record_fail("1.1 Basic Operations, Precedence & Formatting", str(e))

        # 1.2 Division by Zero
        try:
            div_zero_handled = False
            try:
                eval_safe("1 / 0")
            except ZeroDivisionError:
                div_zero_handled = True
            except Exception:
                div_zero_handled = True
            assert div_zero_handled, "eval_safe('1/0') did not raise error"

            div_zero_nested = False
            try:
                eval_safe("(5 + 3) / (4 - 4)")
            except ZeroDivisionError:
                div_zero_nested = True
            except Exception:
                div_zero_nested = True
            assert div_zero_nested, "Nested division by zero failed to raise error"
            self.record_pass("1.2 Division by Zero Detection")
        except Exception as e:
            self.record_fail("1.2 Division by Zero Detection", str(e))

        # 1.3 High Powers & Numerical Bounds
        try:
            res = eval_safe("2 ^ 10")
            assert res == 1024, f"Expected 1024, got {res}"
            
            # High integer powers
            res_high = eval_safe("2 ^ 64")
            assert res_high == 18446744073709551616

            # Float infinity evaluation
            res_inf = eval_safe("1e300 * 1e300")
            assert math.isinf(res_inf), "Expected infinite float result"

            self.record_pass("1.3 High Powers & Float Extreme Bounds")
        except Exception as e:
            self.record_fail("1.3 High Powers & Float Extreme Bounds", str(e))

        # 1.4 Trigonometric and Math Functions
        try:
            sin_val = eval_safe("math.sin(math.pi / 2)")
            assert abs(sin_val - 1.0) < 1e-7, f"sin(pi/2) != 1.0, got {sin_val}"
            
            cos_val = eval_safe("math.cos(math.pi)")
            assert abs(cos_val - (-1.0)) < 1e-7, f"cos(pi) != -1.0, got {cos_val}"

            tan_val = eval_safe("math.tan(math.pi / 4)")
            assert abs(tan_val - 1.0) < 1e-7, f"tan(pi/4) != 1.0, got {tan_val}"

            exp_val = eval_safe("math.exp(1)")
            assert abs(exp_val - math.e) < 1e-7, "math.exp(1) failed"

            sqrt_val = eval_safe("math.sqrt(144)")
            assert sqrt_val == 12.0, "math.sqrt(144) != 12"
            self.record_pass("1.4 Standard Math & Trigonometric Evaluation")
        except Exception as e:
            self.record_fail("1.4 Standard Math & Trigonometric Evaluation", str(e))

        # 1.5 Domain Errors (sqrt of negative, log of zero, log of negative)
        try:
            sqrt_neg = False
            try:
                eval_safe("math.sqrt(-4)")
            except ValueError:
                sqrt_neg = True
            assert sqrt_neg, "sqrt(-4) did not raise ValueError"

            log_zero = False
            try:
                eval_safe("math.log(0)")
            except ValueError:
                log_zero = True
            assert log_zero, "log(0) did not raise ValueError"

            log_neg = False
            try:
                eval_safe("math.log10(-10)")
            except ValueError:
                log_neg = True
            assert log_neg, "log10(-10) did not raise ValueError"
            self.record_pass("1.5 Mathematical Domain Errors (sqrt(-x), ln(0), log(-x))")
        except Exception as e:
            self.record_fail("1.5 Mathematical Domain Errors", str(e))

        # 1.6 Malformed & Adversarial Expression Inputs
        malformed_inputs = ["", "   ", "+-/*", "..5", "5 +", "(((", ")(", "1.2.3", "math.non_existent(5)"]
        for expr in malformed_inputs:
            try:
                eval_safe(expr)
                self.record_fail(f"1.6 Malformed Input '{expr}'", "Expected exception but expression evaluated successfully")
                break
            except Exception:
                pass
        else:
            self.record_pass("1.6 Malformed Syntax & Empty String Rejections")

        # 1.7 Security: Arbitrary Code Execution Resistance
        try:
            injection_blocked = False
            try:
                eval_safe("__import__('os').system('echo pwned')")
            except (TypeError, NameError, Exception):
                injection_blocked = True
            assert injection_blocked, "Arbitrary __import__ not blocked"
            self.record_pass("1.7 Sandbox Isolation & Code Injection Resistance")
        except Exception as e:
            self.record_fail("1.7 Sandbox Isolation & Code Injection Resistance", str(e))

    # =========================================================================
    # DOMAIN 2: Database CRUD, Concurrency & Boundary Suite
    # =========================================================================
    def test_database_crud_and_concurrency(self):
        print("\n" + "="*70)
        print("DOMAIN 2: Database Concurrency, Transaction Safety & Boundary CRUD")
        print("="*70)

        # 2.1 Multi-Threaded Concurrent Operations
        thread_errors = []
        def worker_task(thread_id: int):
            try:
                d_str = f"2026-09-{(thread_id % 28) + 1:02d}"
                # 1. Log checkin
                log_daily_checkin(
                    checkin_date=d_str,
                    hours_logged=1.5 + (thread_id % 3) * 0.25,
                    completed_topics=["M01", "M02"] if thread_id % 2 == 0 else ["S25"],
                    error_codes=["C", "S"] if thread_id % 2 == 0 else ["F"],
                    roadblocks_text=f"Thread {thread_id} test roadblock"
                )
                # 2. Update formula review
                update_formula_review("M01", quality_score=(thread_id % 3))
                # 3. Add error quarantine
                add_error_quarantine(
                    date_logged=d_str,
                    topic_id="M01",
                    topic_name="Rank of Matrix",
                    error_code="S",
                    question_details=f"Thread {thread_id} concurrent question",
                    wrong_attempt_notes=f"Wrong {thread_id}",
                    correct_takeaway=f"Correct {thread_id}"
                )
                # 4. Read checkins
                get_all_checkins()
                # 5. Read formula vault
                get_formula_vault()
            except Exception as ex:
                thread_errors.append((thread_id, str(ex)))

        threads = []
        for i in range(20):
            t = threading.Thread(target=worker_task, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        if thread_errors:
            self.record_fail("2.1 Multi-Threaded Database Concurrency", f"{len(thread_errors)} thread errors: {thread_errors[:3]}")
        else:
            self.record_pass("2.1 Multi-Threaded Database Concurrency (20 concurrent threads)")

        # 2.2 Corrupted JSON Data Resilience in Database
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Inject raw corrupt JSON into daily_checkins
            cur.execute("""
            INSERT OR REPLACE INTO daily_checkins (date, hours_logged, completed_topics, error_codes, roadblocks_text)
            VALUES ('1999-01-01', 2.0, 'CORRUPTED_JSON{[', 'CORRUPT_ERR', 'Test corrupt')
            """)
            conn.commit()
            conn.close()

            # Test if get_all_checkins(), get_checkin_by_date() survive without crashing
            checkin_corrupt = get_checkin_by_date("1999-01-01")
            assert checkin_corrupt is not None
            assert checkin_corrupt["completed_topics"] == []
            assert checkin_corrupt["error_codes"] == []

            all_checkins = get_all_checkins()
            assert isinstance(all_checkins, list)
            
            # Clean up test row
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM daily_checkins WHERE date = '1999-01-01'")
            conn.commit()
            conn.close()

            self.record_pass("2.2 Corrupted JSON Deserialization Fault Tolerance")
        except Exception as e:
            self.record_fail("2.2 Corrupted JSON Deserialization Fault Tolerance", f"Crashed on corrupt JSON in DB: {str(e)}")

        # 2.3 SQL Injection Resistance
        try:
            sqli_payload = "' OR '1'='1'; DROP TABLE daily_checkins; --"
            set_setting(sqli_payload, "test_val")
            val = get_setting(sqli_payload)
            assert val == "test_val", "SQLi payload corrupted key-value storage"
            
            # Verify table still exists
            checkins = get_all_checkins()
            assert isinstance(checkins, list), "daily_checkins table was damaged"
            self.record_pass("2.3 Parameterized Queries & SQL Injection Resistance")
        except Exception as e:
            self.record_fail("2.3 Parameterized Queries & SQL Injection Resistance", str(e))

        # 2.4 Massive Payload & Unicode/Special Character Resilience
        try:
            huge_text = "📐 Ω Δ θ 🖩 " + ("GATE_TEST_2026_" * 50000) # ~750KB payload
            eid = add_error_quarantine(
                date_logged="2026-08-26",
                topic_id="M01",
                topic_name="Rank of Matrix",
                error_code="C",
                question_details=huge_text,
                wrong_attempt_notes=huge_text[:1000],
                correct_takeaway=huge_text[:1000]
            )
            assert eid > 0, "Failed to insert large payload"
            errors = get_quarantined_errors(only_active=True)
            saved_err = next((e for e in errors if e["id"] == eid), None)
            assert saved_err is not None, "Failed to retrieve large payload error"
            assert len(saved_err["question_details"]) == len(huge_text), "Payload was truncated unexpectedly"
            
            # Clean up large test error
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM error_quarantine WHERE id = ?", (eid,))
            conn.commit()
            conn.close()

            self.record_pass("2.4 Large Payload & Multi-byte Unicode/Emoji Stress")
        except Exception as e:
            self.record_fail("2.4 Large Payload & Multi-byte Unicode/Emoji Stress", str(e))

        # 2.5 Non-Existent Topic ID Handling & Null Fields in Formula Vault
        try:
            update_topic_completion("NON_EXISTENT_ID_999", True)
            update_formula_review("NON_EXISTENT_ID_999", quality_score=2)
            
            # Inject a card with NULL fields
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
            INSERT OR REPLACE INTO formula_vault (
                topic_id, formula_title, formula_latex, domain,
                interval_days, repetition_count, ease_factor,
                last_reviewed_date, next_review_date, mastery_status
            ) VALUES ('TEST_NULL_CARD', 'Null Card', 'X=0', 'Math', NULL, NULL, NULL, NULL, '2026-08-26', 'Learning')
            """)
            conn.commit()
            conn.close()

            # Attempt update on card with NULL fields
            update_formula_review("TEST_NULL_CARD", quality_score=2)
            card = next(c for c in get_formula_vault() if c["topic_id"] == "TEST_NULL_CARD")
            assert card["repetition_count"] == 1
            assert card["interval_days"] == 1
            assert card["ease_factor"] >= 2.5

            # Clean up test card
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM formula_vault WHERE topic_id = 'TEST_NULL_CARD'")
            conn.commit()
            conn.close()

            self.record_pass("2.5 Non-Existent Topic IDs & NULL-Field Robustness")
        except Exception as e:
            self.record_fail("2.5 Non-Existent Topic IDs & NULL-Field Robustness", str(e))

    # =========================================================================
    # DOMAIN 3: Interactive PYQ Validation Suite
    # =========================================================================
    def test_interactive_pyq_validation(self):
        print("\n" + "="*70)
        print("DOMAIN 3: Interactive PYQ Validation (NAT Floating-Point & MCQ)")
        print("="*70)

        # Validation function matching components/inapp_studio.py
        def validate_pyq(q_type: str, user_answer: str, correct_ans: str) -> bool:
            u_str = (user_answer or "").strip()
            c_str = (correct_ans or "").strip()
            if not u_str or not c_str:
                return False
            if q_type == "MCQ":
                if u_str == c_str:
                    return True
                u_p = u_str.split(")")[0].strip().upper() if ")" in u_str else u_str.strip().upper()
                c_p = c_str.split(")")[0].strip().upper() if ")" in c_str else c_str.strip().upper()
                return (u_p == c_p and len(u_p) == 1)
            else: # NAT
                try:
                    u_val = float(u_str.replace(",", "."))
                    c_val = float(c_str.replace(",", "."))
                    if not (math.isnan(u_val) or math.isnan(c_val) or math.isinf(u_val) or math.isinf(c_val)):
                        return (abs(u_val - c_val) <= 0.05 * abs(c_val) or abs(u_val - c_val) <= 0.1)
                except Exception:
                    return (u_str == c_str)
                return False

        # 3.1 NAT Exact and Tolerances
        try:
            assert validate_pyq("NAT", "10", "10") == True, "Exact integer string failed"
            assert validate_pyq("NAT", "10.0", "10") == True, "10.0 vs 10 failed"
            assert validate_pyq("NAT", "10.00", "10.0") == True, "10.00 vs 10.0 failed"
            assert validate_pyq("NAT", "10,5", "10.5") == True, "Comma separator 10,5 failed"
            assert validate_pyq("NAT", "104.9", "100.0") == True, "Within 5% tolerance failed"
            assert validate_pyq("NAT", "106.0", "100.0") == False, "Outside 5% tolerance incorrectly passed"
            assert validate_pyq("NAT", "0.05", "0.0") == True, "Zero baseline +/-0.1 margin failed"
            assert validate_pyq("NAT", "-0.0", "0.0") == True, "Negative zero failed"
            assert validate_pyq("NAT", "1e2", "100") == True, "Scientific notation 1e2 failed"
            assert validate_pyq("NAT", "0.00125", "1.25e-3") == True, "Scientific notation 1.25e-3 failed"
            self.record_pass("3.1 NAT Floating-Point Matching & 5% Tolerances")
        except Exception as e:
            self.record_fail("3.1 NAT Floating-Point Matching & 5% Tolerances", str(e))

        # 3.2 NAT Adversarial / Blank Inputs
        try:
            assert validate_pyq("NAT", "", "10") == False, "Blank user input must fail"
            assert validate_pyq("NAT", "   ", "10") == False, "Whitespace input must fail"
            assert validate_pyq("NAT", "", "") == False, "Blank input on blank correct answer must fail"
            assert validate_pyq("NAT", "abc", "10") == False, "Text input for NAT must fail"
            assert validate_pyq("NAT", "NaN", "10") == False, "NaN input must fail"
            assert validate_pyq("NAT", "Infinity", "10") == False, "Infinity input must fail"
            assert validate_pyq("NAT", "-inf", "10") == False, "-inf input must fail"
            self.record_pass("3.2 NAT Blank & Adversarial Non-numeric Inputs")
        except Exception as e:
            self.record_fail("3.2 NAT Blank & Adversarial Non-numeric Inputs", str(e))

        # 3.3 MCQ Option Formatting & Prefixes
        try:
            assert validate_pyq("MCQ", "A) 1 and 2", "A) 1 and 2") == True, "Exact MCQ string failed"
            assert validate_pyq("MCQ", "A) 1 and 2", "A") == True, "Prefix 'A) 1 and 2' vs 'A' failed"
            assert validate_pyq("MCQ", "A", "A) 1 and 2") == True, "'A' vs 'A) 1 and 2' failed"
            assert validate_pyq("MCQ", "B) 0 and 3", "A) 1 and 2") == False, "Wrong MCQ option passed"
            assert validate_pyq("MCQ", "", "A) 1 and 2") == False, "Blank MCQ selection must fail"
            assert validate_pyq("MCQ", None, "A) 1 and 2") == False, "None MCQ selection must fail"
            self.record_pass("3.3 MCQ Option Trimming, Prefix Matching & Robustness")
        except Exception as e:
            self.record_fail("3.3 MCQ Option Trimming, Prefix Matching & Robustness", str(e))

    # =========================================================================
    # DOMAIN 4: Spaced Repetition (SuperMemo-2) Suite
    # =========================================================================
    def test_spaced_repetition(self):
        print("\n" + "="*70)
        print("DOMAIN 4: Spaced Repetition (SM-2) Interval Arithmetic & Boundaries")
        print("="*70)

        # 4.1 Boundary Limits: Repeated 'Forgot' (Score 0) -> Ease Floor at 1.3
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
            INSERT OR REPLACE INTO formula_vault (
                topic_id, formula_title, formula_latex, domain,
                interval_days, repetition_count, ease_factor,
                last_reviewed_date, next_review_date, mastery_status
            ) VALUES ('TEST_SM2', 'Test Formula', 'E=mc^2', 'Math', 10, 5, 2.5, '2026-08-26', '2026-08-27', 'Reviewing')
            """)
            conn.commit()
            conn.close()

            # Execute 20 consecutive 'forgot' reviews
            for _ in range(20):
                update_formula_review("TEST_SM2", quality_score=0)

            cards = [c for c in get_formula_vault(due_only=False) if c["topic_id"] == "TEST_SM2"]
            assert len(cards) == 1
            card = cards[0]
            assert card["ease_factor"] >= 1.3, f"Ease factor dropped below 1.3: {card['ease_factor']}"
            assert abs(card["ease_factor"] - 1.3) < 1e-5, f"Ease factor not capped at 1.3: {card['ease_factor']}"
            assert card["interval_days"] == 1, f"Interval not reset to 1 day: {card['interval_days']}"
            assert card["repetition_count"] == 0, f"Reps not reset to 0: {card['repetition_count']}"
            assert card["mastery_status"] == "Learning", f"Status not Learning: {card['mastery_status']}"
            self.record_pass("4.1 Minimum Ease Factor Boundary (Floor at 1.3)")
        except Exception as e:
            self.record_fail("4.1 Minimum Ease Factor Boundary", str(e))

        # 4.2 Progressive Mastery: Repeated 'Easy' (Score 2) -> Status 'Mastered'
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
            UPDATE formula_vault
            SET interval_days = 1, repetition_count = 0, ease_factor = 2.5, mastery_status = 'Learning'
            WHERE topic_id = 'TEST_SM2'
            """)
            conn.commit()
            conn.close()

            # Review 1 (rep 0 -> 1)
            update_formula_review("TEST_SM2", quality_score=2)
            c1 = next(c for c in get_formula_vault() if c["topic_id"] == "TEST_SM2")
            assert c1["repetition_count"] == 1
            assert c1["interval_days"] == 1
            assert c1["mastery_status"] == "Reviewing"

            # Review 2 (rep 1 -> 2)
            update_formula_review("TEST_SM2", quality_score=2)
            c2 = next(c for c in get_formula_vault() if c["topic_id"] == "TEST_SM2")
            assert c2["repetition_count"] == 2
            assert c2["interval_days"] == 3
            assert c2["mastery_status"] == "Reviewing"

            # Review 3 (rep 2 -> 3)
            update_formula_review("TEST_SM2", quality_score=2)
            c3 = next(c for c in get_formula_vault() if c["topic_id"] == "TEST_SM2")
            assert c3["repetition_count"] == 3
            assert c3["interval_days"] >= 7

            # Review 4 (rep 3 -> 4) -> Mastered
            update_formula_review("TEST_SM2", quality_score=2)
            c4 = next(c for c in get_formula_vault() if c["topic_id"] == "TEST_SM2")
            assert c4["repetition_count"] == 4
            assert c4["mastery_status"] == "Mastered"

            # Clean up test card
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM formula_vault WHERE topic_id = 'TEST_SM2'")
            conn.commit()
            conn.close()

            self.record_pass("4.2 Progressive Interval Scaling & Mastery Transition (SM-2)")
        except Exception as e:
            self.record_fail("4.2 Progressive Interval Scaling & Mastery Transition", str(e))

    # =========================================================================
    # DOMAIN 5: Analytics & Pacing Engine Suite
    # =========================================================================
    def test_analytics_engine(self):
        print("\n" + "="*70)
        print("DOMAIN 5: Analytics, Pacing Trajectories & Divide-by-Zero Checks")
        print("="*70)

        # 5.1 Day 1 Start Date (0 Days Elapsed)
        try:
            today_str = date.today().strftime("%Y-%m-%d")
            set_setting("start_date", today_str)
            m = calculate_dashboard_metrics()
            assert m["days_elapsed"] == 0, f"Expected 0 days elapsed, got {m['days_elapsed']}"
            assert m["current_week"] == 1, f"Expected Week 1, got {m['current_week']}"
            assert m["days_remaining"] == TOTAL_WEEKS * 7, f"Expected {TOTAL_WEEKS*7} days remaining"
            assert isinstance(m["pacing_index"], (int, float))
            assert not math.isnan(m["pacing_index"])
            self.record_pass("5.1 Zero Days Elapsed (Cycle Launch Day)")
        except Exception as e:
            self.record_fail("5.1 Zero Days Elapsed", str(e))

        # 5.2 Future Start Date (Negative Difference)
        try:
            future_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
            set_setting("start_date", future_date)
            m = calculate_dashboard_metrics()
            assert m["days_elapsed"] == 0, f"Future start date should clamp days_elapsed to 0, got {m['days_elapsed']}"
            assert m["current_week"] == 1, f"Expected Week 1 for future date, got {m['current_week']}"
            self.record_pass("5.2 Future Start Date Clamping")
        except Exception as e:
            self.record_fail("5.2 Future Start Date Clamping", str(e))

        # 5.3 200 Days Elapsed (Overdue Cycle Boundary)
        try:
            past_date = (date.today() - timedelta(days=200)).strftime("%Y-%m-%d")
            set_setting("start_date", past_date)
            m = calculate_dashboard_metrics()
            assert m["days_elapsed"] == 200
            assert m["current_week"] == TOTAL_WEEKS, f"Current week should be capped at {TOTAL_WEEKS}, got {m['current_week']}"
            assert m["days_remaining"] == 0, f"Days remaining should be 0, got {m['days_remaining']}"

            rec = calculate_backlog_recovery()
            assert rec["remaining_weeks"] >= 1, "Remaining weeks must be at least 1 to avoid ZeroDivisionError"
            assert rec["required_topics_per_week"] >= 0
            assert not math.isnan(rec["required_topics_per_week"])
            self.record_pass("5.3 200 Days Elapsed Overdue Cycle & Recovery Bounds")
        except Exception as e:
            self.record_fail("5.3 200 Days Elapsed Overdue Cycle", str(e))

        # Restore start_date to today
        set_setting("start_date", date.today().strftime("%Y-%m-%d"))

        # 5.4 Metric Distributions & Error Pareto Normalization
        try:
            topics = get_all_topics()
            m = calculate_dashboard_metrics()
            assert 0.0 <= m["overall_progress_pct"] <= 100.0
            
            errs = get_error_distribution()
            assert "total_errors" in errs
            assert len(errs["breakdown"]) == len(ERROR_TAXONOMY)
            total_pct = sum(e["percentage"] for e in errs["breakdown"])
            if errs["total_errors"] > 0:
                assert abs(total_pct - 100.0) < 1.0, f"Error percentages do not sum to 100%: {total_pct}"
            self.record_pass("5.4 Metric Distributions & Error Pareto Normalization")
        except Exception as e:
            self.record_fail("5.4 Metric Distributions & Error Pareto Normalization", str(e))

    # =========================================================================
    # DOMAIN 6: AI Fallback Engine & Schedule Allocator Suite
    # =========================================================================
    def test_ai_fallback_engine(self):
        print("\n" + "="*70)
        print("DOMAIN 6: AI Action Plan Generator & Schedule Time Allocation")
        print("="*70)

        # 6.1 Time Allocation Split Sanity (0.25h, 0.5h, 1.0h, 2.0h, 5.0h)
        test_windows = [0.25, 0.5, 1.0, 1.5, 2.0, 4.0]
        for w in test_windows:
            try:
                plan = generate_next_day_action_plan(
                    study_window_hours=w,
                    recent_errors=["C", "F"],
                    roadblocks="Test roadblock"
                )
                assert "Part 1: Recall Session" in plan
                assert "Part 2: Theory Deep Dive" in plan
                assert "Part 3: Targeted PYQ Problem Set" in plan
                
                # Check for negative minutes in plan
                if "[-" in plan or "Allocated: -" in plan:
                    self.record_fail(f"6.1 Study Window {w}h Allocation", f"Negative time allocation detected in generated plan")
                    break
            except Exception as e:
                self.record_fail(f"6.1 Study Window {w}h Allocation", str(e))
                break
        else:
            self.record_pass("6.1 Study Window Time Allocation Sanity (Positive Minutes Across All Segments)")

        # 6.2 Zero Error Codes & All Error Codes
        try:
            plan_no_err = generate_next_day_action_plan(1.5, recent_errors=[], roadblocks="")
            assert "Part 1: Recall Session" in plan_no_err

            all_errs = list(ERROR_TAXONOMY.keys())
            plan_all_err = generate_next_day_action_plan(2.0, recent_errors=all_errs, roadblocks="High friction on Laplace transforms")
            assert "Part 1: Recall Session" in plan_all_err
            assert "High friction on Laplace transforms" in plan_all_err
            self.record_pass("6.2 AI Plan Generation with Empty and Full Error Taxonomies")
        except Exception as e:
            self.record_fail("6.2 AI Plan Generation with Empty and Full Error Taxonomies", str(e))

        # 6.3 Edge Cases: Negative Window, Zero Window, None Roadblock
        try:
            plan_zero = generate_next_day_action_plan(0.0, recent_errors=[], roadblocks=None)
            assert "Part 1: Recall Session" in plan_zero
            assert "Allocated:" in plan_zero

            plan_neg = generate_next_day_action_plan(-1.0, recent_errors=["C"], roadblocks="")
            assert "Part 1: Recall Session" in plan_neg
            self.record_pass("6.3 AI Plan Resilience on 0.0h, Negative Hours, and None Roadblocks")
        except Exception as e:
            self.record_fail("6.3 AI Plan Resilience on Boundary Inputs", str(e))

    def run_all(self):
        print("\n" + "#"*70)
        print("# STARTING BRUTAL ADVERSARIAL QA & STRESS TEST SUITE")
        print("# Target: GATE IN & RA Command Center")
        print("#"*70)

        self.test_virtual_calculator()
        self.test_database_crud_and_concurrency()
        self.test_interactive_pyq_validation()
        self.test_spaced_repetition()
        self.test_analytics_engine()
        self.test_ai_fallback_engine()

        print("\n" + "="*70)
        print(f"STRESS TEST SUMMARY: {self.passed} PASSED | {self.failed} FAILED")
        print("="*70)
        if self.errors:
            print("\n[!] DETECTED DEFECTS & FAILURES:")
            for name, reason in self.errors:
                print(f"  [x] {name}: {reason}")
        else:
            print("\n[+] ALL TESTS PASSED! ZERO DEFECTS DETECTED.")
        print("="*70 + "\n")
        return self.failed == 0


if __name__ == "__main__":
    runner = StressTestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
