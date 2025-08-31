import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


runner_ip = os.getenv("RUNNER_IP")
if not runner_ip:
    raise ValueError("RUNNER_IP environment variable is not set")

manager_ip = os.getenv("MANAGER_IP", runner_ip)
indexer_ip = os.getenv("INDEXER_IP", runner_ip)


# Wazuh Manager API credentials
manager_user = "wazuh-wui"
manager_pass = os.getenv("WAZUH_API_PASSWORD")

# Indexer credentials (if basic auth)
indexer_user ="admin"
indexer_pass = os.getenv("WAZUH_INDEXER_PASSWORD") 


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
