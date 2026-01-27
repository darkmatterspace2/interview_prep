# CI/CD Concepts (Data Engineering Focus)

## Key Concepts

### 1. Continuous Integration (CI)
The practice of frequently merging code changes into a central repository.
*   **Goal:** Detect errors quickly, avoid "integration hell".
*   **Key Steps:**
    *   **Checkout:** Pull code from Git.
    *   **Linting & Formatting:** Check code style (Pylint, Black, Flake8).
    *   **Dependency Installation:** Install libraries in a minimal environment.
    *   **Unit Tests:** Run tests (Pytest) to ensure logic is correct.
    *   **Build/Compile:** Create artifacts (Wheel files, Docker images).

### 2. Continuous Delivery (CD) vs Continuous Deployment
*   **Continuous Delivery:** Code is automatically built, tested, and prepared for production release. The final deployment to Production is triggered manually (approval gate).
*   **Continuous Deployment:** Every change that passes all tests is deployed to Production automatically without human intervention.

### 3. Code Quality Checks (Static Analysis)
*   **Linting:** Analyzes code for potential errors, stylistic errors, and suspicious constructs (e.g., `pylint`, `eslint`).
*   **Formatting:** Enforces a consistent style (e.g., `black`, `prettier`).
*   **SAST (Static Application Security Testing):** Scans source code for security vulnerabilities (e.g., SonarQube, Bandit).

### 4. Dependency Management
Handling external libraries required for the project.
*   **Lock Files:** (`poetry.lock`, `package-lock.json`) Ensure exactly the same versions are installed in CI as on the developer's machine.
*   **Caching:** Storing downloaded packages (e.g., `~/.cache/pip`) to speed up subsequent pipeline runs.

---

# CI/CD Interview Questions

## Beginner Level

1.  **What is the difference between CI and CD?**
    *   **Answer:** CI (Continuous Integration) is about automating the build and testing of code every time a team member commits changes to version control. CD (Continuous Delivery/Deployment) is about automating the release of that validated code to a repository or production environment.

2.  **What is the purpose of "Linting" in a pipeline?**
    *   **Answer:** Linting (using tools like `pylint` or `flake8`) statically analyzes code to catch syntax errors, stylistic issues (PEP8), and identifying code smells (unused variables, complex functions) *before* the code is run or tested.

3.  **Why should you use a `requirements.txt` or `poetry.lock` file in CI?**
    *   **Answer:** To ensure reproducibility. These files specify the exact versions of dependencies. Without them, the CI environment might install a newer version of a library that introduces breaking changes, causing the build to fail or behave differently than in development.

4.  **What is a "Build Artifact"?**
    *   **Answer:** An artifact is the compiled or packaged result of the build process (e.g., a `.jar` file, a Python `.whl` file, a Docker image, or a ZIP of the source code) that is ready to be deployed.

5.  **Explain the concept of a "Pipeline" in tools like Jenkins or GitHub Actions.**
    *   **Answer:** A pipeline is a defined series of steps (jobs/stages) that execute automatically. Common stages include: Checkout -> Install Deps -> Lint -> Test -> Build -> Deploy Staging.

6.  **What is Git and why is it essential for CI/CD?**
    *   **Answer:** Git is a version control system. It is the foundation of CI/CD because the pipeline is triggered by events in Git (Push, Pull Request). It allows teams to collaborate and revert changes if deployments fail.

7.  **What is "Blue-Green Deployment"?**
    *   **Answer:** A technique where two identical environments exist: Blue (running production) and Green (idle). You deploy the new version to Green, test it, and then switch the router/load balancer to point to Green. Blue becomes the new idle/backup.

8.  **What is a "Canary Deployment"?**
    *   **Answer:** Releasing the new version to a small subset of users (e.g., 5% traffic) first. If metrics look good, roll it out to the rest. If errors spike, rollback immediately affecting only a few users.

9.  **What is a "Merge Conflict"?**
    *   **Answer:** When two developers edit the same lines of code in a file and try to merge them. Git cannot automatically resolve it, so manual intervention is required. CI pipelines usually fail if a merge conflict exists.

10. **Why are Unit Tests important in CI?**
    *   **Answer:** They validate that individual components work as expected. Running them automatically in CI prevents "regressions" (breaking existing features) from merging into the main codebase.

## Medium Level

11. **How do you speed up a slow CI pipeline that installs many dependencies every time?**
    *   **Answer:** Implement **Caching**.
        *   In GitHub Actions: `uses: actions/cache@v3` for `~/.cache/pip` or `node_modules`.
        *   The pipeline checks if the `lock` file hasn't changed; if so, it restores dependencies from the cache instead of downloading them again.

12. **How does Docker help in CI/CD?**
    *   **Answer:** Docker containers provide a consistent environment. "It works on my machine" issues are eliminated because the CI runner builds and tests inside the exact same container image that will run in production.

13. **What is Dependabot (or Renovate)?**
    *   **Answer:** An automation tool that scans your dependency files (`requirements.txt`, `package.json`) for outdated or insecure packages. It automatically opens Pull Requests to update them.

14. **How do you handle secrets (API keys, DB passwords) in a CI/CD pipeline?**
    *   **Answer:** Never commit them to Git. Use the CI tool's Secrets Management (GitHub Secrets, Jenkins Credentials). These are injected into the pipeline as Environment Variables (`$DB_PASSWORD`) only at runtime.

15. **What happens if the "Lint" stage fails?**
    *   **Answer:** The pipeline should stop (Fail Fast). The build is marked as failed, and the developer must fix the code style/errors and push again. Badly formatted code should not proceed to the Testing or Deployment stages.

16. **Explain the difference between "Integration Tests" and "Unit Tests".**
    *   **Answer:**
        *   **Unit Tests:** Test a single function/class in isolation (mocking external calls). Fast.
        *   **Integration Tests:** Test how modules work together (e.g., connecting to a test database). Slower.

17. **What is Infrastructure as Code (IaC) and how does it fit into CI/CD?**
    *   **Answer:** Managing infrastructure (servers, databases, buckets) using code (Terraform, CloudFormation). IaC allows you to review infrastructure changes via PRs and deploy infrastructure updates automatically using the pipeline (`terraform apply`).

18. **How would you debug a build that passes locally but fails in the CI pipeline?**
    *   **Answer:**
        *   Check environment differences (OS, Python version).
        *   Check dependency versions (did I forget to freeze a version?).
        *   Check environment variables (are secrets missing in CI?).
        *   Read the raw CI logs.

19. **What is a "Runner" or "Agent" in CI/CD?**
    *   **Answer:** The server or container that actually executes the pipeline jobs. It can be hosted (e.g., GitHub-hosted runner) or self-hosted (your own VM).

20. **Describe a CI/CD workflow for a Python Data Engineering project.**
    *   **Answer:**
        1.  PR opened.
        2.  **CI Triggered:**
            *   Run `black --check` & `isort` (Formatting).
            *   Run `pylint` or `flake8` (Linting).
            *   Run `pytest` (Unit Tests).
        3.  **Merge:** Code merges to `main`.
        4.  **CD Triggered:**
            *   Build Docker Image.
            *   Push to Container Registry (ACR/ECR).
            *   Deploy to Staging (Terraform/Helm).

## Advanced Level

21. **How do you implement "Atomic Deployments" for a Data Pipeline (e.g., Airflow DAGs)?**
    *   **Answer:** Ensure the code and the DAG definition are updated simultaneously.
        *   Strategy: Package DAGs into a zip/image.
        *   Use a shared volume or object store where the scheduler parses atomically swappable artifacts.
        *   Avoid modifying files in-place while the scheduler is parsing.

22. **What is "Drift Detection" in IaC pipelines?**
    *   **Answer:** detecting when the actual infrastructure state differs from the Terraform state (configuration). A scheduled pipeline can run `terraform plan` just to check for drift and alert if manual changes were made to the cloud environment.

23. **How do you handle Database Migrations (Schema changes) in CD?**
    *   **Answer:** Use tools like Flyway or Liquibase or Alembic.
        *   The migration script is part of the code repo.
        *   The CD pipeline runs the migration command (`alembic upgrade head`) *before* deploying the new application code.
        *   **Backward Compatibility:** Ensure schema changes don't break the *current* running version to allow zero-downtime deployment.

24. **Explain the security risks of "Supply Chain Attacks" in CI/CD.**
    *   **Answer:** Attackers compromising a dependency (e.g., a node package) or the CI pipeline itself (SolarWinds).
    *   **Mitigation:** Verify checksums of packages, use signed commits, minimize external dependencies, pin versions, and use SLSA (Supply-chain Levels for Software Artifacts) framework.

25. **How do you optimize a Docker build in CI to be faster?**
    *   **Answer:** Optimize **Layer Caching**.
        *   Copy `requirements.txt` first.
        *   Run `pip install`.
        *   *Then* copy the rest of the source code.
        *   This way, if only code changes (not requirements), Docker reuses the cached "pip install" layer.

26. **What is "GitOps"?**
    *   **Answer:** A paradigm where the Git repository is the "source of truth" for infrastructure and application state. An agent (like ArgoCD) inside the cluster continuously pulls changes from Git and syncs the cluster state to match. It is Pull-based CD (vs Push-based Jenkins).

27. **How do you handle specific Python versions in a matrix build?**
    *   **Answer:** Configure the pipeline (e.g., GitHub Actions `strategy: matrix`) to run the tests in parallel buckets: one for Python 3.9, one for 3.10, etc. This ensures library compatibility across versions.

28. **What is the difference between SAST and DAST?**
    *   **Answer:**
        *   **SAST (Static):** Scans source code files (White-box). Done early in CI.
        *   **DAST (Dynamic):** Scans the running application (Black-box) by attacking endpoints. Done in Staging/QA.

29. **How would you rollback a failed deployment in a Kubernetes environment?**
    *   **Answer:** `kubectl rollout undo deployment/my-app`. It reverts the deployment to the previous revision. In a proper GitOps setup, you would revert the Git commit, and ArgoCD would sync the cluster back to the previous state.

30. **Explain the concept of "Ephemeral Environments".**
    *   **Answer:** Creating a temporary, isolated environment (database + app) for *every* Pull Request. Allows QA/Product Managers to test the specific feature in a live-like setting before merging. The environment is destroyed automatically when the PR is closed.
