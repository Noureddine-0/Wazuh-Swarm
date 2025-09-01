## Table of Contents
- [Architecture](#Architecture)

- [Prerequisites](#Prerequisites)

- [How to run](#How-to-run)

- [Secrets/TLS](#SecretsTLS)

- [Rollback/Recovery](#RollbackRecovery)

- [Wazuh Dashboard](#Wazuh-Dashboard)

- [SSH rule](#SSH-rule)

- [CI/CD Pipeline](#CI/CD-Pipeline)

- [Trivy Scans](#Trivy-Scans)




## Architecture
![Diagram of Wazuh Stack](/images/Diagram.png)
This setup runs on a single Ubuntu host where all the Wazuh components are containerized and orchestrated with Docker Swarm. The deployment includes a Wazuh manager cluster (one master and one worker), an indexer for storing and searching events, and the Wazuh dashboard for visualization and management. On top of that, an NGINX container ties everything together by acting as a load balancer for the managers and as a reverse proxy in front of the dashboard. Even though everything is running on one machine, the architecture is designed to mimic a distributed setup, making it easier to scale or move to multiple hosts later if needed.

## Prerequisites
- A Linux machine (tested on Ubuntu 22.04)
- Python installed
- Docker and Docker Compose installed
- Ansible installed for deployment automation

## How to run
### Using CI
If you’re running this through the provided CI pipeline, the process is straightforward. All you need is a machine configured as a CI runner the pipeline will handle the rest, including container orchestration and deployment of the full Wazuh stack. This is the simplest option since it doesn’t require any manual setup of dependencies or secrets on your side.

### Running Locally
To run the stack manually on your own machine, you’ll need a bit of preparation. First, make sure that the required dependencies are installed: Python, Docker, Docker Compose, and Ansible. You’ll also need to provide the necessary Wazuh passwords and Wazuh certificates, which must be stored as Docker Swarm secrets before starting the deployment. Once the environment is ready, you can use the Ansible playbook to spin up the containers and manage the Wazuh stack locally.

## Secrets/TLS
In this setup, sensitive data is managed securely using GitHub Secrets. The wazuh passwords are stored as GitHub Secrets and injected into the CI pipeline as environment variables during runtime. The TLS certificates and keys are also stored as base64-encoded GitHub Secrets and decoded when the pipeline runs. Once the secrets are available in the pipeline, they are converted into Docker Swarm secrets, which are then used by the containers for secure communication between the Wazuh components. This approach ensures that credentials and certificates are never exposed in plaintext within the repository or logs, while allowing seamless deployment in a containerized environment.

## Rollback/Recovery
The playbook includes a safe deployment strategy with automatic rollback to ensure that the Wazuh environment remains consistent. 

```yaml
- name: Deploy Wazuh stack safely with rollback
  block:
    - name: Deploy or update Wazuh stack
      community.docker.docker_stack:
        name: wazuh
        state: present
        compose:
          - "{{ playbook_dir }}/../stack/wazuh-stack.yml"
        prune: yes
  rescue:
    - name: Rollback in case of failure
      ansible.builtin.debug:
        msg: "Deployment failed, rolling back stack"
    - name: Remove partial/failed stack
      community.docker.docker_stack:
        name: wazuh
        state: absent
    - name: Fail the playbook after rollback
      ansible.builtin.fail:
        msg: "Wazuh stack deployment failed. Rollback complete."
```
If the deployment encounters any errors, the playbook immediately enters the rescue block. It first logs a message indicating that the deployment failed, then removes any partially deployed or inconsistent stack to ensure the environment is clean. Finally, the playbook explicitly fails using ansible.builtin.fail, causing the entire deployment process to exit with an error. This guarantees that no partial or inconsistent state remains and that the CI/CD pipeline reflects the failure, providing a reliable and safe deployment process with a clear rollback mechanism.

## Wazuh Dashboard
The screenshot below confirms that the Wazuh dashboard is up and running
![Dashboard](/images/Dashboard.jpg)

## SSH rule

```xml
<group name="local,ssh,brute_force,successful_brute_force">
	<rule id="100001" level="12">
		<if_sid>5715</if_sid>
		<if_matched_sid>5712</if_matched_sid>
		<same_source_ip />
		<description>sshd: Successful ssh login after multiple fails from non-existent users</description>
		<mitre>
      		<id>T1110</id>
   		 </mitre>
	</rule>
</group>
```

We created this rule to detect successful SSH logins that occur after multiple failed attempts from non-existent users. By correlating prior failed login attempts (rule 5712) with a current successful login (rule 5715) from the same source IP, this rule helps identify potential brute-force attacks that ultimately succeed. Assigned a high alert level of 12 and mapped to MITRE ATT&CK technique T1110, it ensures that such suspicious authentication events are promptly flagged for security monitoring.

The following image shows the process of triggering the rule by trying multiple logins with non-existent user,then a successful login

![aler-Triggering](/images/aler-Triggering.jpg)

And here we can clearly see the alert with id 100001

![Alert-Triggered](/images/Alert-Triggered.jpg)

## CI/CD Pipeline
The pipeline begins with a lint job, which validates the syntax and formatting of Ansible playbooks and YAML configuration files to ensure code quality and prevent errors early. Next, the build job constructs the Wazuh Docker images and scans them using Trivy for known vulnerabilities. Finally, the deploy-test job uses Ansible to deploy the Wazuh stack in a controlled environment and verifies its functionality. Testing is performed through automated checks, including Selenium-based UI tests and direct API probes, confirming that the deployment is operational and responsive. This structured workflow ensures reliability, security, and correctness of the Wazuh deployment from code commit to tested deployment.<a href="https://github.com/Noureddine-0/Wazuh-Swarm/actions/runs/17365984718" target="_blank">This</a> is the link for the pipeline.

![Pipeline](/images/Ci.jpg)

## Trivy scans
As part of our pipeline, we integrated Trivy to scan the Wazuh Docker images for known vulnerabilities. The scans were configured to detect Critical and High severity issues; however, the pipeline does not fail or exit when such vulnerabilities are found. For example, our Wazuh Manager 4.12.0 (the latest version) depends on a specific version of Filebeat, which includes some vulnerabilities in its Go binary. These vulnerabilities are reported by Trivy but are not exploitable in our deployment context, as they do not affect the functionality or security of Wazuh in practice. This approach allows us to monitor vulnerabilities continuously without blocking the CI/CD workflow, acknowledging that some reported issues may be false positives or non-critical for our use case, while still maintaining visibility for future mitigation.
