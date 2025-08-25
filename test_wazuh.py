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


manager_ip = os.getenv("MANAGER_IP", runner_ip)
indexer_ip = os.getenv("INDEXER_IP", runner_ip)


# Wazuh Manager API credentials
manager_user = "wazuh-wui"
manager_pass = os.getenv("MANAGER_PASSWORD")

# Indexer credentials (if basic auth)
indexer_user ="admin"
indexer_pass = os.getenv("INDEXER_PASSWORD") 
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

# --- Wazuh Manager API Health Check ---
manager_api_url = f"https://{manager_ip}:55000/security/user/authenticate"
try:
    resp = requests.get(manager_api_url, auth=(manager_user, manager_pass), verify=False)
    if resp.status_code == 200:
        print("✅ Wazuh Manager API reachable!")
    else:
        print(f"❌ Wazuh Manager API returned {resp.status_code}: {resp.text}")
except Exception as e:
    print(f"❌ Error connecting to Wazuh Manager API: {e}")

# --- Indexer API Health Check ---
indexer_api_url = f"https://{indexer_ip}:9200/"
try:
    resp = requests.get(indexer_api_url, auth=(indexer_user, indexer_pass), verify=False)
    if resp.status_code == 200:
        print("✅ Wazuh Indexer API reachable!")
    else:
        print(f"❌ Wazuh Indexer API returned {resp.status_code}: {resp.text}")
except Exception as e:
    print(f"❌ Error connecting to Wazuh Indexer API: {e}")
