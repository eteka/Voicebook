# CI/CD Pipeline Documentation

This document describes the complete CI/CD pipeline setup for Voicebook.

## 📋 Overview

Voicebook uses GitHub Actions for continuous integration and continuous deployment. Our pipeline ensures code quality, security, and reliability through automated testing and checks.

## 🔄 Workflows

### 1. CI - Tests & Coverage (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**

#### a) Test Matrix
Runs tests across multiple Python versions to ensure compatibility:
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

**Steps:**
1. Checkout code
2. Set up Python environment
3. Install dependencies (with pip cache)
4. Run pytest with coverage
5. Upload coverage to Codecov (Python 3.11 only)
6. Upload coverage HTML report as artifact
7. Verify 80%+ coverage threshold

**Artifacts:**
- Coverage HTML report (30-day retention)
- Coverage XML for Codecov

#### b) Integration Tests
Runs comprehensive integration tests after unit tests pass.

**Steps:**
1. Checkout code
2. Set up Python 3.11
3. Install dependencies
4. Run integration tests

#### c) Test Summary
Aggregates results from all test jobs and fails if any job failed.

**Configuration:**
```yaml
python-version: ["3.9", "3.10", "3.11", "3.12"]
fail-fast: false  # Run all versions even if one fails
```

---

### 2. Code Quality (`code-quality.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**

#### a) Code Quality Checks

**Steps:**
1. **Black** - Code formatting
   - Checks if code follows Black style
   - Line length: 100 characters
   - Fails if unformatted code detected

2. **isort** - Import sorting
   - Verifies imports are sorted correctly
   - Uses Black-compatible profile

3. **Flake8** - Linting
   - Checks for syntax errors (fails build)
   - Reports code quality issues (warnings only)
   - Max line length: 100
   - Max complexity: 10

4. **mypy** - Type checking
   - Static type analysis
   - Continue on error (not blocking initially)

5. **pylint** - Advanced linting
   - Comprehensive code analysis
   - Continue on error (not blocking initially)

6. **interrogate** - Docstring coverage
   - Minimum 70% docstring coverage
   - Continue on error (not blocking initially)

#### b) Complexity Analysis

**Steps:**
1. **Radon CC** - Cyclomatic complexity
   - Analyzes code complexity
   - Reports complex functions

2. **Radon MI** - Maintainability index
   - Calculates maintainability scores
   - Identifies hard-to-maintain code

---

### 3. Security Scanning (`security.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- **Scheduled:** Daily at 2 AM UTC

**Jobs:**

#### a) Security Vulnerability Scan

**Steps:**
1. **Bandit** - Python security issues
   - Scans for common security issues
   - Generates JSON report
   - Shows medium/high severity issues

2. **Safety** - Dependency vulnerabilities
   - Checks dependencies for known CVEs
   - Generates JSON report
   - Continue on error (informational)

3. **pip-audit** - PyPI package audit
   - Audits installed packages
   - Identifies vulnerable dependencies
   - Continue on error (informational)

**Artifacts:**
- `bandit-report.json`
- `safety-report.json`
- `pip-audit-report.json`

#### b) CodeQL Analysis

**GitHub Advanced Security:**
- Semantic code analysis
- Detects security vulnerabilities
- Queries: security-and-quality
- Language: Python

**Permissions Required:**
- actions: read
- contents: read
- security-events: write

#### c) Secrets Scanning

**TruffleHog:**
- Scans for accidentally committed secrets
- Checks entire git history
- Only reports verified secrets
- Runs on every commit

---

### 4. Dependabot (`dependabot.yml`)

**Automated Dependency Updates:**

#### Python Dependencies
- **Schedule:** Weekly on Monday at 9 AM UTC
- **Max PRs:** 10 open at once
- **Grouping:** Patch updates grouped together
- **Labels:** `dependencies`, `python`
- **Versioning:** Increase strategy (security-first)

#### GitHub Actions
- **Schedule:** Weekly on Monday at 9 AM UTC
- **Max PRs:** 5 open at once
- **Labels:** `dependencies`, `github-actions`

**Auto-review:** Assigned to repository owner

---

## 🔧 Pre-commit Hooks

Local git hooks that run before each commit.

**Install:**
```bash
pip install pre-commit
pre-commit install
```

**Hooks:**

1. **General Checks:**
   - Trim trailing whitespace
   - Fix end of files
   - Check YAML/JSON/TOML syntax
   - Detect large files (>500KB)
   - Check for merge conflicts
   - Detect private keys
   - Fix line endings

2. **Python Formatting:**
   - Black (auto-format)
   - isort (sort imports)

3. **Linting:**
   - Flake8 with plugins:
     - flake8-docstrings
     - flake8-bugbear
     - flake8-comprehensions
     - flake8-simplify

4. **Security:**
   - Bandit (security issues)
   - Safety (dependency vulnerabilities)

5. **Type Checking:**
   - mypy with type stubs

6. **Documentation:**
   - interrogate (docstring coverage)
   - markdownlint (Markdown linting)
   - yamllint (YAML linting)

7. **Modernization:**
   - pyupgrade (upgrade to modern Python syntax)

**Run manually:**
```bash
# All files
pre-commit run --all-files

# Specific hook
pre-commit run black --all-files

# Skip hooks (emergency only)
git commit --no-verify
```

---

## ⚙️ Configuration Files

### `pyproject.toml`

Central configuration for all Python tools:

```toml
[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = ["--cov=src", "--cov-fail-under=80"]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.bandit]
exclude_dirs = ["/tests"]

[tool.pylint.main]
max-line-length = 100
```

### `pytest.ini`

Legacy pytest configuration (can be migrated to pyproject.toml):

```ini
[pytest]
testpaths = tests
addopts = -v --cov=src --cov-report=html
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

---

## 📊 Quality Gates

### Required (Blocking)

✅ **Must pass for PR to merge:**
- All unit tests (190+ tests)
- Code formatting (Black)
- Import sorting (isort)
- Linting critical issues (Flake8 E9, F63, F7, F82)
- Minimum 80% test coverage
- Security scan (Bandit high severity)

### Advisory (Non-blocking)

⚠️ **Should fix but won't block merge:**
- Type checking (mypy)
- Pylint warnings
- Code complexity warnings
- Docstring coverage
- Dependency vulnerabilities (Safety)

---

## 🚦 Status Badges

Add to README.md:

```markdown
[![CI - Tests & Coverage](https://github.com/eteka/Voicebook/actions/workflows/ci.yml/badge.svg)](https://github.com/eteka/Voicebook/actions/workflows/ci.yml)
[![Code Quality](https://github.com/eteka/Voicebook/actions/workflows/code-quality.yml/badge.svg)](https://github.com/eteka/Voicebook/actions/workflows/code-quality.yml)
[![Security Scanning](https://github.com/eteka/Voicebook/actions/workflows/security.yml/badge.svg)](https://github.com/eteka/Voicebook/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/eteka/Voicebook/branch/main/graph/badge.svg)](https://codecov.io/gh/eteka/Voicebook)
```

---

## 🔐 Secrets Required

Configure in GitHub Settings → Secrets and variables → Actions:

### Optional Secrets

- `CODECOV_TOKEN` - For uploading coverage to Codecov (optional but recommended)

### Repository Settings

Enable in Settings → Actions → General:
- ✅ Allow GitHub Actions
- ✅ Allow actions from GitHub and verified creators

Enable in Settings → Code security and analysis:
- ✅ Dependency graph
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Code scanning (CodeQL)
- ✅ Secret scanning

---

## 📈 Monitoring & Reports

### GitHub Actions

View in repository:
- **Actions tab:** All workflow runs
- **Pull Requests:** Status checks
- **Security tab:** Security alerts

### Coverage Reports

- **Codecov:** https://codecov.io/gh/eteka/Voicebook
- **Artifacts:** Download HTML reports from successful runs

### Security Reports

- **Dependabot:** Automated PRs for vulnerable dependencies
- **Code scanning alerts:** Security vulnerabilities found by CodeQL
- **Artifacts:** Download security scan JSON reports

---

## 🛠️ Troubleshooting

### Tests Failing in CI but Passing Locally

**Causes:**
- Different Python versions
- Missing environment variables
- Platform-specific issues

**Solutions:**
```bash
# Test with specific Python version
pyenv install 3.9.18
pyenv shell 3.9.18
pytest tests/

# Run in clean environment
python -m venv clean_venv
source clean_venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/
```

### Pre-commit Hooks Too Slow

**Optimize:**
```bash
# Update hooks
pre-commit autoupdate

# Run specific files only
pre-commit run --files src/module.py

# Skip slow hooks temporarily
SKIP=mypy git commit -m "message"
```

### Coverage Below Threshold

**Fix:**
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html

# Identify uncovered lines
coverage report --show-missing
```

### Dependabot PRs Failing

**Common Issues:**
1. Breaking changes in dependencies
2. Incompatible version constraints
3. Test failures with new versions

**Solutions:**
1. Review CHANGELOG of updated package
2. Update code to handle breaking changes
3. Pin problematic dependency version
4. Close PR and create issue

---

## 🚀 Best Practices

### For Developers

1. **Run tests locally first:**
   ```bash
   pytest tests/ --cov=src
   ```

2. **Use pre-commit hooks:**
   ```bash
   pre-commit run --all-files
   ```

3. **Check coverage:**
   ```bash
   coverage report --fail-under=80
   ```

4. **Commit small, atomic changes**

5. **Write descriptive commit messages**

### For Reviewers

1. **Check CI status** before reviewing code
2. **Review coverage changes** in artifacts
3. **Check security scan results**
4. **Verify documentation updates**
5. **Test manually** for complex features

### For Maintainers

1. **Review Dependabot PRs weekly**
2. **Monitor security alerts daily**
3. **Update workflows quarterly**
4. **Review and update quality gates**
5. **Keep documentation current**

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.com/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Python Packaging Guide](https://packaging.python.org/)

---

**Last Updated:** 2025
**Maintained by:** Voicebook Contributors
