# Fitness & Gym Management System

A Flask web application for managing fitness clients, workout programs, and progress tracking with automated testing and CI/CD integration.

## Quick Links

- [Local Setup](#local-setup)
- [Running Tests](#running-tests)
- [CI/CD Integration](#cicd-integration)
- [API Endpoints](#api-endpoints)
- [Project Files](#project-files)

## Local Setup

### Prerequisites

- Python 3.11+
- pip 23.0+
- Docker
- Git 2.30+

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fitness-gym-management.git
cd fitness-gym-management
```

2. Create and activate virtual environment:
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The application starts on `http://localhost:5000`

5. Verify it's running:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2024-03-04T10:30:45.123456"}
```

## Running Tests

### Run All Tests

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Run all tests with verbose output
pytest test_app.py -v

# Run tests with coverage report
pytest test_app.py -v --cov=app --cov-report=html --cov-report=term

# Run tests with coverage and detailed missing lines
pytest test_app.py --cov=app --cov-report=term-missing
```

### Run Specific Tests

```bash
# Run a specific test class
pytest test_app.py::TestClientEndpoints -v

# Run a specific test method
pytest test_app.py::TestClientEndpoints::test_create_client_success -v
```

## CI/CD Integration

### High-Level Overview

This project uses two complementary CI/CD systems:

**GitHub Actions** - Primary automated pipeline for every code push/PR
- Runs immediately when code is pushed to GitHub
- Fast feedback loop (5-10 minutes typical)
- Blocks merge if tests or quality gates fail
- Ideal for development and pre-merge validation

**Jenkins** - Enterprise-grade secondary validation pipeline
- Optional manual or webhook-triggered execution
- Comprehensive artifact retention and reporting
- Advanced scheduling capabilities
- Suitable for production deployment workflows

Both systems execute the same core tasks: dependency installation, linting, testing, Docker build, and quality validation. They ensure code quality and container readiness before deployment.

### GitHub Actions Workflow

The GitHub Actions pipeline (`.github/workflows/main.yml`) runs automatically on:
- Every push to `main` or `develop` branches
- Every pull request

**Workflow Execution Flow:**

```
Code Push / Pull Request
         ↓
    GitHub Webhook
         ↓
  ┌─────────────────────────────────────────┐
  │   Stage 1: Build & Lint                 │
  │   - Install Python dependencies         │
  │   - Run flake8 linter                   │
  │   - Check Python syntax                 │
  └─────────────────────────────────────────┘
         ↓ (success)
  ┌─────────────────────────────────────────┐
  │   Stage 2: Unit Tests                   │
  │   - Run Pytest (42 tests)               │
  │   - Generate coverage reports           │
  │   - Upload to Codecov                   │
  └─────────────────────────────────────────┘
         ↓ (success)
  ┌─────────────────────────────────────────┐
  │   Stage 3: Docker Build                 │
  │   - Build container image               │
  │   - Tag with Git SHA                    │
  │   - Push to registry (optional)         │
  └─────────────────────────────────────────┘
         ↓ (success)
  ┌─────────────────────────────────────────┐
  │   Stage 4: Container Testing            │
  │   - Run tests inside Docker             │
  │   - Test health check endpoint          │
  │   - Validate container startup          │
  └─────────────────────────────────────────┘
         ↓ (success)
  ┌─────────────────────────────────────────┐
  │   Stage 5: Quality Gate                 │
  │   - Verify all stages passed            │
  │   - Check coverage threshold (81%)      │
  │   - Approve/reject merge                │
  └─────────────────────────────────────────┘
         ↓ (success)
    ✓ Pull Request Approved
    ✓ Allow Merge to Main
```

Pipeline stages:
1. **Build & Lint**: Installs dependencies and checks code syntax
2. **Unit Tests**: Runs Pytest suite and generates coverage reports
3. **Docker Build**: Builds and tags Docker image
4. **Container Testing**: Runs tests inside Docker container
5. **Quality Gate**: Validates all stages passed before allowing merge

To trigger:
```bash
git push origin main
```

### Jenkins Pipeline

Jenkins configuration is defined in `Jenkinsfile`. It provides enterprise-grade CI/CD with comprehensive logging and artifact management.

**Pipeline Execution Flow:**

```
Manual Trigger / Build Now Button
       ↓
  ┌───────────────────────────────────────────┐
  │  Stage 1: Checkout                        │
  │  - Clone from GitHub repository           │
  │  - Checkout specific branch               │
  └───────────────────────────────────────────┘
       ↓ (success)
  ┌───────────────────────────────────────────┐
  │  Stage 2: Setup Environment               │
  │  - Create Python virtual environment      │
  │  - Prepare workspace                      │
  └───────────────────────────────────────────┘
       ↓ (success)
  ┌───────────────────────────────────────────┐
  │  Stage 3: Install Dependencies            │
  │  - pip install -r requirements.txt        │
  │  - Verify package versions                │
  └───────────────────────────────────────────┘
       ↓ (success)
  ┌───────────────────────────────────────────┐
  │  Stage 4: Code Quality (Lint)             │
  │  - Run flake8 syntax checker              │
  │  - Report style violations                │
  └───────────────────────────────────────────┘
       ↓ (success)
  ┌───────────────────────────────────────────┐
  │  Stage 5: Syntax Check                    │
  │  - Python py_compile validation           │
  │  - Compile all Python modules             │
  └───────────────────────────────────────────┘
       ↓ (success)
  ┌───────────────────────────────────────────┐
  │  Stage 6: Unit Tests                      │
  │  - Run Pytest (42 tests)                  │
  │  - Generate JUnit XML reports             │
  │  - Publish coverage metrics               │
  └───────────────────────────────────────────┘
       ↓ (success)
  ┌───────────────────────────────────────────┐
  │  Stage 7: Build Docker                    │
  │  - Build Docker image                     │
  │  - Tag with build number                  │
  └───────────────────────────────────────────┘
       ↓ (success)
  ┌───────────────────────────────────────────┐
  │  Stage 8: Test Docker                     │
  │  - Run container from built image         │
  │  - Execute tests inside container         │
  │  - Validate health endpoints              │
  └───────────────────────────────────────────┘
       ↓ (success)
  ┌───────────────────────────────────────────┐
  │  Stage 9: Quality Gate                    │
  │  - Verify all stages completed            │
  │  - Validate test pass rate                │
  │  - Check coverage requirements            │
  └───────────────────────────────────────────┘
       ↓ (success)
  ┌───────────────────────────────────────────┐
  │  Stage 10: Archive Artifacts              │
  │  - Store test reports                     │
  │  - Save coverage HTML reports             │
  │  - Preserve Docker build logs             │
  └───────────────────────────────────────────┘
       ↓
    ✓ Build Successful
    ✓ Artifacts Available
```

#### Setup Steps

1. Install required plugins in Jenkins:
   - Pipeline
   - GitHub Integration
   - Docker Plugin
   - Email Extension

2. Create new Pipeline job:
   - Name: `fitness-gym-management`
   - Type: Pipeline
   - Source: Git (SCM)
   - Repository URL: Your GitHub repository
   - Branch: `*/main`

3. (Optional) Configure GitHub Webhook:
   - GitHub Repo → Settings → Webhooks → Add webhook
   - Payload URL: `http://your-jenkins-server/github-webhook/`
   - Content type: `application/json`
   - Events: Push events and Pull requests

4. Run pipeline:
   - Manual: Click "Build Now" in Jenkins
   - Automatic: Push code to GitHub (if webhook enabled)


## Docker Usage

Build Docker image:
```bash
docker build -t fitness-gym-app:latest .
```

Run container:
```bash
docker run -d -p 5000:5000 --name fitness-app fitness-gym-app:latest
```