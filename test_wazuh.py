from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Start browser (headless mode so no GUI needed)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--allow-insecure-localhost")
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://192.168.24.101:443/app/login?")  # adjust to your Wazuh Dashboard address
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
