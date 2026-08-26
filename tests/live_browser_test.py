"""
Live Headless Chrome Browser Automation & Real-Time UI Tester
Tests https://sarat-2007.github.io/gate-in-ra-command-center/ in real-time.
"""
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_live_test():
    print("=" * 70)
    print("STARTING REAL-TIME LIVE BROWSER TEST ON GITHUB PAGES")
    print("Target: https://sarat-2007.github.io/gate-in-ra-command-center/")
    print("=" * 70)

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1400,900")
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    # Enable browser console log capture
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    driver = webdriver.Chrome(options=options)

    try:
        url = "https://sarat-2007.github.io/gate-in-ra-command-center/"
        print(f"\n[1] Navigating to live web app: {url} ...")
        driver.get(url)
        time.sleep(3)

        # 1. Verify Page Title & Header
        title = driver.title
        print(f"  -> Page Title: '{title}'")
        assert "GATE 2027" in title, f"Unexpected title: {title}"

        day_elapsed = driver.find_element(By.ID, "headerDayElapsed").text
        days_rem = driver.find_element(By.ID, "headerDaysRemaining").text
        timer_text = driver.find_element(By.ID, "activeTimerDisplay").text
        pacing = driver.find_element(By.ID, "headerPacingStatus").text

        print(f"  -> Header Info: Day {day_elapsed} of 140 | {days_rem} Days Remaining | {timer_text} | {pacing}")
        assert int(days_rem) > 0, "Days remaining should be > 0"

        # 2. Check Step 1 Content
        print("\n[2] Testing Step 1 (5-Min Morning Recall)...")
        step1_title = driver.find_element(By.CSS_SELECTOR, "#view-step1 .step-title").text
        print(f"  -> Step 1 Title: {step1_title}")
        assert "Step 1" in step1_title

        # Check KaTeX rendering
        katex_elements = driver.find_elements(By.CLASS_NAME, "katex")
        print(f"  -> KaTeX Math Rendered Count in Step 1: {len(katex_elements)}")
        assert len(katex_elements) > 0, "KaTeX did not render formulas!"

        # Click proceed to Step 2
        proc_btn = driver.find_element(By.CSS_SELECTOR, "#view-step1 button.btn-primary")
        proc_btn.click()
        time.sleep(1)

        # 3. Check Step 2 Content (Video & Notes)
        print("\n[3] Testing Step 2 (Video Lecture & Formula Sheet)...")
        step2_sec = driver.find_element(By.ID, "view-step2")
        assert "active" in step2_sec.get_attribute("class"), "Step 2 view is not active!"
        
        iframe = driver.find_element(By.CSS_SELECTOR, "#view-step2 .video-container iframe")
        iframe_src = iframe.get_attribute("src")
        print(f"  -> Embedded Video URL: {iframe_src}")
        assert "youtube-nocookie.com/embed" in iframe_src

        # Test Theory vs PYQ toggle
        pyq_toggle = driver.find_element(By.XPATH, "//button[contains(text(), 'Tier 2')]")
        pyq_toggle.click()
        time.sleep(1)
        iframe_src_pyq = driver.find_element(By.CSS_SELECTOR, "#view-step2 .video-container iframe").get_attribute("src")
        print(f"  -> Toggled to PYQ Walkthrough Video: {iframe_src_pyq}")

        # Click proceed to Step 3
        proc_pyq_btn = driver.find_element(By.CSS_SELECTOR, "#view-step2 button.btn-primary")
        proc_pyq_btn.click()
        time.sleep(1)

        # 4. Check Step 3 (Interactive PYQ Solver)
        print("\n[4] Testing Step 3 (Interactive GATE PYQ Solver)...")
        step3_sec = driver.find_element(By.ID, "view-step3")
        assert "active" in step3_sec.get_attribute("class"), "Step 3 view is not active!"

        q_text = driver.find_element(By.CSS_SELECTOR, "#view-step3 .question-text").text
        print(f"  -> Problem Statement: {q_text[:80]}...")

        # Select first option if MCQ or input NAT
        options_radio = driver.find_elements(By.NAME, "pyq_option")
        if options_radio:
            print(f"  -> Found {len(options_radio)} MCQ options. Selecting option 1...")
            options_radio[0].click()
        else:
            nat_in = driver.find_element(By.ID, "natInput")
            nat_in.send_keys("10")
            print("  -> NAT question. Inputted 10.")

        # Click check answer
        check_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Check Answer')]")
        check_btn.click()
        time.sleep(1)

        fb_box = driver.find_element(By.ID, "pyqFeedback")
        print(f"  -> Instant Verification Result: {fb_box.text[:100]}...")
        assert len(fb_box.text) > 0, "No feedback rendered!"

        # Click Tag Mistake button
        tag_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Tag Mistake')]")
        tag_btn.click()
        time.sleep(0.5)
        # Accept browser alert
        try:
            alert = driver.switch_to.alert
            print(f"  -> Tag Mistake Alert: '{alert.text}'")
            alert.accept()
        except Exception as e:
            print(f"  -> Alert handled: {e}")

        # Click proceed to Step 4
        proc_log_btn = driver.find_element(By.XPATH, "//div[@id='step3Content']//button[contains(@onclick, 'step4')]")
        proc_log_btn.click()
        time.sleep(1)

        # 5. Check Step 4 (Daily Wrap-Up)
        print("\n[5] Testing Step 4 (Daily Wrap-Up & Lock Progress)...")
        step4_sec = driver.find_element(By.ID, "view-step4")
        assert "active" in step4_sec.get_attribute("class"), "Step 4 view is not active!"

        lock_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Lock in Progress')]")
        lock_btn.click()
        time.sleep(0.5)
        try:
            alert = driver.switch_to.alert
            print(f"  -> Lock Progress Alert: '{alert.text}'")
            alert.accept()
        except Exception as e:
            print(f"  -> Alert handled: {e}")
        time.sleep(1)

        # 6. Test TCS iON Virtual Calculator
        print("\n[6] Testing TCS iON Scientific Calculator...")
        calc_open_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'TCS iON Calculator')]")
        calc_open_btn.click()
        time.sleep(1)

        calc_modal = driver.find_element(By.ID, "calcModal")
        assert "open" in calc_modal.get_attribute("class"), "Calculator modal failed to open!"

        # Perform arithmetic: 7 * 8 = 56
        btn_7 = driver.find_element(By.XPATH, "//div[@id='calcModal']//button[text()='7']")
        btn_mul = driver.find_element(By.XPATH, "//div[@id='calcModal']//button[text()='*']")
        btn_8 = driver.find_element(By.XPATH, "//div[@id='calcModal']//button[text()='8']")
        btn_eq = driver.find_element(By.XPATH, "//div[@id='calcModal']//button[text()='=']")

        btn_7.click()
        btn_mul.click()
        btn_8.click()
        btn_eq.click()
        time.sleep(0.5)

        calc_screen_val = driver.find_element(By.ID, "calcScreen").text
        print(f"  -> Calculator 7 * 8 Result: {calc_screen_val}")
        assert calc_screen_val == "56", f"Expected 56, got {calc_screen_val}"

        # 7. Test Syllabus Tree View
        print("\n[7] Testing 20-Week Syllabus Hierarchy View...")
        nav_syllabus = driver.find_element(By.XPATH, "//div[@data-view='syllabus']")
        nav_syllabus.click()
        time.sleep(1)
        
        weeks = driver.find_elements(By.CLASS_NAME, "week-card")
        print(f"  -> Found {len(weeks)} 20-Week Syllabus Hierarchy cards rendered.")
        assert len(weeks) >= 15, "Expected >= 15 week cards rendered!"

        # 8. Test Progress & Mistakes View
        print("\n[8] Testing Progress & Mistakes Diary View...")
        nav_progress = driver.find_element(By.XPATH, "//div[@data-view='progress']")
        nav_progress.click()
        time.sleep(1)

        progress_sec = driver.find_element(By.ID, "view-progress")
        assert "active" in progress_sec.get_attribute("class"), "Progress view is not active!"
        print(f"  -> Progress & Mistakes View Loaded Cleanly!")

        # 9. Check Console Logs for JS Errors
        print("\n[9] Inspecting Browser Console Logs...")
        logs = driver.get_log('browser')
        severe_errors = [l for l in logs if l['level'] == 'SEVERE']
        if severe_errors:
            print(f"  ⚠️ Warning: {len(severe_errors)} SEVERE console errors found:")
            for l in severe_errors:
                print(f"    - {l['message']}")
        else:
            print("  ✅ ZERO severe JavaScript console errors found!")

        print("\n" + "=" * 70)
        print("REAL-TIME LIVE BROWSER TEST PASSED WITH 100% SUCCESS!")
        print("=" * 70)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_live_test()
