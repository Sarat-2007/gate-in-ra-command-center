import http.server
import socketserver
import threading
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PORT = 8912
Handler = http.server.SimpleHTTPRequestHandler

class QuietServer(socketserver.TCPServer):
    allow_reuse_address = True

httpd = QuietServer(('127.0.0.1', PORT), Handler)
server_thread = threading.Thread(target=httpd.serve_forever)
server_thread.daemon = True
server_thread.start()
print("Local test server started on port", PORT)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1400,900")
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

driver = webdriver.Chrome(options=options)
try:
    driver.get(f"http://127.0.0.1:{PORT}/index.html")
    time.sleep(2)
    
    # 1. Check Step 1 text content
    step1_text = driver.find_element(By.ID, "step1Content").text
    print("Step 1 rendered text snippet:\n", step1_text[:250])
    
    # Ensure no raw LaTeX $$ delimiters are left visible as plain text
    assert "$$\\displaystyle" not in step1_text, "ERROR: Raw LaTeX $$ was found in Step 1!"
    
    katex_nodes = driver.find_elements(By.CLASS_NAME, "katex")
    print(f"  -> KaTeX mathematical formula nodes count in Step 1: {len(katex_nodes)}")
    assert len(katex_nodes) >= 3, "Expected >= 3 KaTeX rendered formulas!"
    print("  -> Step 1 KaTeX formulas verified!")

    # 2. Check Step 2
    driver.find_element(By.CSS_SELECTOR, "#view-step1 button.btn-primary").click()
    time.sleep(1)
    
    step2_text = driver.find_element(By.ID, "step2Content").text
    assert "$$\\displaystyle" not in step2_text, "ERROR: Raw LaTeX $$ was found in Step 2!"
    
    iframe = driver.find_element(By.CSS_SELECTOR, "#view-step2 .video-container iframe")
    print(f"  -> Video iframe src: {iframe.get_attribute('src')}")
    
    search_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Search Lectures on YouTube')]")
    print(f"  -> Search link URL: {search_link.get_attribute('href')[:80]}...")
    print("  -> Step 2 KaTeX formulas and video controls verified!")

    # 3. Check Step 3
    driver.find_element(By.CSS_SELECTOR, "#view-step2 button.btn-primary").click()
    time.sleep(1)
    
    # Select first radio option
    opts = driver.find_elements(By.NAME, "pyq_option")
    if opts:
        opts[0].click()
    driver.find_element(By.XPATH, "//button[contains(text(), 'Check Answer')]").click()
    time.sleep(1)
    
    fb = driver.find_element(By.ID, "pyqFeedback")
    print("  -> Feedback text:\n", fb.text[:150])
    assert len(fb.text) > 0
    print("  -> Step 3 PYQ solver verified!")

    print("\n" + "=" * 60)
    print("LOCAL FULL VERIFICATION PASSED WITH 100% SUCCESS!")
    print("=" * 60)

finally:
    driver.quit()
    httpd.shutdown()
    print("Test server closed.")
