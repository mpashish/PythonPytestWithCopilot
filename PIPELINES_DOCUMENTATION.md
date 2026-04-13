# 🚀 CI/CD Pipelines Documentation

## Overview

This document describes the complete CI/CD pipeline setup for the **BlazeDemo Flight Automation Framework**. The framework uses GitHub Actions to automate testing, reporting, and deployment processes.

## 📋 Pipeline Architecture

### 5 Core Pipelines:
1. **CI Pipeline** - Code quality and basic validation
2. **Test Execution Pipeline** - Full test suite execution
3. **Report Generation Pipeline** - Allure report creation
4. **Nightly Regression Pipeline** - Scheduled automated testing
5. **Release Pipeline** - Framework packaging and distribution

---

## 1. 🔄 CI Pipeline (`ci.yml`)

### Purpose
- **Fast feedback** on code changes
- **Code quality checks** (linting, formatting)
- **Basic smoke tests** to ensure functionality
- **Runs on every push/PR** to main/develop branches

### Triggers
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

### Steps Executed

#### Step 1: Environment Setup
```yaml
- name: Checkout code
  uses: actions/checkout@v4

- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'
```

#### Step 2: Dependency Management
```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

#### Step 3: Code Quality Checks
```yaml
- name: Run linting (flake8)
  run: |
    pip install flake8
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

#### Step 4: Basic Testing
```yaml
- name: Run basic smoke tests
  run: |
    pytest tests/test_find_flights.py::TestFindFlights::test_find_flights_valid -v --tb=short
```

#### Step 5: Artifact Upload
```yaml
- name: Upload test results
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: ci-test-results
    path: |
      allure-results/
      *.log
```

### Expected Duration: 2-5 minutes
### Artifacts: `ci-test-results`

---

## 2. 🧪 Test Execution Pipeline (`test-execution.yml`)

### Purpose
- **Complete test suite execution** across multiple browsers
- **Parallel test execution** for faster results
- **Cross-browser testing** (Chrome + Firefox)
- **Manual trigger capability** for on-demand testing

### Triggers
```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      browser:
        description: 'Browser to run tests on'
        default: 'chrome'
        options: [chrome, firefox]
      environment:
        description: 'Test environment'
        default: 'staging'
```

### Matrix Strategy
```yaml
strategy:
  matrix:
    browser: [chrome, firefox]
```

### Steps Executed

#### Step 1: Environment Setup
```yaml
- name: Checkout code
  uses: actions/checkout@v4

- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'
```

#### Step 2: Browser Setup
```yaml
- name: Install browser dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y wget gnupg
    # Chrome installation
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
```

#### Step 3: Full Test Execution
```yaml
- name: Run full test suite
  run: |
    export BROWSER=${{ matrix.browser }}
    pytest tests/ -v --tb=short --alluredir=allure-results --maxfail=5 -n 2
```

#### Step 4: Report Generation
```yaml
- name: Generate Allure report
  if: always()
  run: |
    pip install allure-pytest
    allure generate allure-results/ -o allure-report/ --clean
```

#### Step 5: Artifact Management
```yaml
- name: Upload test results
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: test-results-${{ matrix.browser }}
    path: |
      allure-results/
      allure-report/
```

### Expected Duration: 5-15 minutes
### Artifacts: `test-results-chrome`, `test-results-firefox`

---

## 3. 📊 Report Generation Pipeline (`generate-reports.yml`)

### Purpose
- **Consolidate test results** from multiple browsers
- **Generate unified Allure reports**
- **Publish reports** for stakeholder access
- **Triggered automatically** after test execution

### Triggers
```yaml
on:
  workflow_run:
    workflows: ["Test Execution Pipeline"]
    types: [completed]
  workflow_dispatch:
```

### Steps Executed

#### Step 1: Download Previous Results
```yaml
- name: Download test results from previous workflow
  uses: actions/download-artifact@v3
  with:
    name: test-results-chrome
    path: allure-results-chrome/
```

#### Step 2: Merge Results
```yaml
- name: Merge Allure results
  run: |
    mkdir -p merged-allure-results
    cp -r allure-results-chrome/allure-results/* merged-allure-results/ 2>/dev/null || true
    cp -r allure-results-firefox/allure-results/* merged-allure-results/ 2>/dev/null || true
```

#### Step 3: Generate Consolidated Report
```yaml
- name: Generate consolidated Allure report
  run: |
    pip install allure-pytest
    allure generate merged-allure-results/ -o allure-report/ --clean
```

#### Step 4: Publish Report
```yaml
- name: Deploy to GitHub Pages (Optional)
  if: github.ref == 'refs/heads/main'
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: allure-report/
    destination_dir: test-reports/${{ github.run_number }}
```

### Expected Duration: 1-2 minutes
### Artifacts: `allure-report`

---

## 4. ⏰ Nightly Regression Pipeline (`nightly-regression.yml`)

### Purpose
- **Automated nightly testing** to catch regressions
- **Environment health monitoring**
- **Scheduled execution** (daily at 2 AM UTC)
- **Notification system** for failures

### Triggers
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:
    inputs:
      environment:
        description: 'Test environment'
        default: 'staging'
      notify_on_failure:
        description: 'Send notifications'
        default: true
```

### Steps Executed

#### Step 1: Environment Setup
```yaml
- name: Create test run metadata
  run: |
    echo "REGRESSION_RUN=true" >> $GITHUB_ENV
    echo "RUN_DATE=$(date +'%Y-%m-%d_%H-%M-%S')" >> $GITHUB_ENV
    echo "ENVIRONMENT=${{ github.event.inputs.environment || 'staging' }}" >> $GITHUB_ENV
```

#### Step 2: Regression Testing
```yaml
- name: Run regression test suite
  run: |
    export REGRESSION_RUN=true
    export ENVIRONMENT=${{ github.event.inputs.environment || 'staging' }}
    pytest tests/ -v --tb=short --alluredir=allure-results \
      --maxfail=3 -n 2 \
      -m "not skip_ci"
```

#### Step 3: Notifications
```yaml
- name: Send Slack notification on failure
  if: failure() && (github.event.inputs.notify_on_failure == true || github.event_name == 'schedule')
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    text: |
      🚨 Nightly Regression Failed
      Repository: ${{ github.repository }}
      Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Expected Duration: 10-30 minutes
### Artifacts: `nightly-regression-{date}`

---

## 5. 🚀 Release Pipeline (`release.yml`)

### Purpose
- **Automated framework releases**
- **Package creation and distribution**
- **Version management**
- **Release notes and documentation**

### Triggers
```yaml
on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Release version (e.g., v1.0.0)'
        required: true
```

### Steps Executed

#### Step 1: Pre-release Validation
```yaml
- name: Run tests before release
  run: |
    pytest tests/ -v --tb=short --maxfail=1
```

#### Step 2: Package Building
```yaml
- name: Build package
  run: |
    pip install build twine
    python -m build
```

#### Step 3: GitHub Release Creation
```yaml
- name: Create GitHub Release
  uses: actions/create-release@v1
  with:
    tag_name: ${{ github.ref_name || github.event.inputs.version }}
    release_name: Release ${{ github.ref_name || github.event.inputs.version }}
    body: |
      ## 🚀 Release ${{ github.ref_name || github.event.inputs.version }}

      ### What's Included
      - ✅ Complete test automation framework
      - ✅ Page Object Model implementation
      - ✅ Allure reporting integration
      - ✅ CI/CD pipelines
      - ✅ Cross-browser support
```

#### Step 4: Asset Upload
```yaml
- name: Upload release assets
  uses: actions/upload-release-asset@v1
  with:
    upload_url: ${{ steps.create_release.outputs.upload_url }}
    asset_path: ./dist/blazedemo-automation-${{ github.ref_name || github.event.inputs.version }}.tar.gz
    asset_name: blazedemo-automation-${{ github.ref_name || github.event.inputs.version }}.tar.gz
    asset_content_type: application/gzip
```

### Expected Duration: 2-5 minutes
### Output: GitHub Release with downloadable assets

---

## 🔧 Setup Instructions

### Step 1: Create Required Secrets
Navigate to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `SLACK_WEBHOOK_URL` - For nightly regression notifications
- `PYPI_API_TOKEN` - For PyPI publishing (optional)

### Step 2: Enable GitHub Pages (Optional)
Repository Settings → Pages → Source: "GitHub Actions"

### Step 3: Configure Branch Protection (Recommended)
Repository Settings → Branches → Add rule for `main`:
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Include administrators

### Step 4: Test the Pipelines
1. Push a small change to trigger CI pipeline
2. Manually run Test Execution pipeline
3. Create a test tag to trigger Release pipeline

---

## 📊 Pipeline Monitoring

### GitHub Actions Dashboard
- Repository → Actions tab
- View workflow runs and their status
- Download artifacts and logs

### Key Metrics to Monitor
- **Pipeline Success Rate**
- **Average Execution Time**
- **Test Pass/Fail Rates**
- **Artifact Sizes**

### Alerts and Notifications
- Slack notifications for nightly regression failures
- Email notifications for workflow failures
- GitHub commit status checks

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Browser Installation Failures
```bash
# Check browser versions
google-chrome --version
firefox --version
```

#### 2. Dependency Conflicts
```yaml
# Clear cache and retry
- name: Clear pip cache
  run: pip cache purge
```

#### 3. Allure Report Issues
```yaml
# Ensure proper directory structure
- name: Debug allure results
  run: ls -la allure-results/
```

#### 4. Permission Issues
- Check repository settings for Actions permissions
- Verify secret configurations

---

## 📈 Optimization Tips

### 1. Caching Strategies
```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### 2. Parallel Execution
```yaml
- name: Run tests in parallel
  run: pytest tests/ -n 2  # Use 2 workers
```

### 3. Conditional Execution
```yaml
- name: Skip on documentation changes
  if: "!contains(github.event.head_commit.modified, 'docs/')"
```

---

## 🔄 Pipeline Flow Diagram

```
┌─────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Code Push │───▶│   CI Pipeline   │───▶│ Test Execution   │
│   / PR       │    │   (2-5 min)     │    │   Pipeline       │
└─────────────┘    └─────────────────┘    │   (5-15 min)     │
                                          └──────────────────┘
                                                 │
                                                 ▼
                                       ┌──────────────────┐
                                       │ Report Generation │
                                       │   Pipeline       │
                                       │   (1-2 min)      │
                                       └──────────────────┘
                                                 │
                    ┌─────────────────┐          │
                    │ Nightly         │          │
                    │ Regression      │◀─────────┘
                    │ (10-30 min)     │
                    └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Release       │
                    │   Pipeline      │
                    │   (2-5 min)     │
                    └─────────────────┘
```

---

## 📞 Support

For pipeline issues:
1. Check GitHub Actions logs
2. Review workflow YAML syntax
3. Verify secret configurations
4. Test locally before pushing changes

---

*Last Updated: April 13, 2026*
*Framework Version: 1.0.0*
