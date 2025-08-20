import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Get Wazuh Dashboard IP from environment variable
runner_ip = os.getenv("RUNNER_IP")
if not runner_ip:
    raise ValueError("RUNNER_IP environment variable is not set")

# Start browser (headless mode so no GUI needed)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--allow-insecure-localhost")
driver = webdriver.Chrome(options=options)

try:
    url = f"https://{runner_ip}:443/app/login?"
    driver.get(url)
    print("Page title is:", driver.title)

    # Create WebDriverWait object
    wait = WebDriverWait(driver, 20)  # wait up to 20 seconds

    # Wait for password field
    password = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[data-test-subj="password"]')
        )
    )

    # Wait for username field
    username = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[data-test-subj="user-name"]')
        )
    )

    print("✅ Username and password fields exist!")

finally:
    driver.quit()
