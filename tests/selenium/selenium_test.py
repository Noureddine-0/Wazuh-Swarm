import os
import requests
import urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

runner_ip = os.getenv("RUNNER_IP")
if not runner_ip:
    raise ValueError("RUNNER_IP environment variable is not set")



# --- Selenium test for Dashboard ---

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--allow-insecure-localhost")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    url = f"https://{runner_ip}:443/app/login?"
    driver.get(url)
    print("Page title is:", driver.title)

    wait = WebDriverWait(driver, 20)

    password = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[data-test-subj="password"]')
        )
    )
    username = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[data-test-subj="user-name"]')
        )
    )

    print("✅ Dashboard login page fields exist!")

finally:
    driver.quit()

